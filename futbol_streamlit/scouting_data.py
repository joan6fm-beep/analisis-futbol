"""Datos de SCOUTING FFCV: estructura, importación y cálculos.

Fuente y límites
----------------
* La FFCV publica la estructura de grupos en su blog oficial (permitido por robots.txt).
  Los equipos de cada grupo se han transcrito de las imágenes oficiales de esa publicación.
* Las estadísticas de jugador solo se sirven a través de ``ffcv.es/competiciones/api/``,
  ruta que el robots.txt de la FFCV prohíbe a clientes automáticos (y el servidor de datos
  ``appwebffcv.novanet.es`` prohíbe todo). Por eso NO se consulta de forma automática:
  el usuario guarda desde su navegador la página pública del equipo (HTML) o rellena la
  plantilla CSV/XLSX, y este módulo la importa.

Reglas: nunca se inventan valores (vacío = N/D), no se guardan fotos ni fechas de
nacimiento completas (solo el año, cuando la fuente lo publica) y las importaciones
son idempotentes (identificadores estables, sin duplicados).
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import unicodedata
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
DIR = BASE / "data" / "scouting"
FUENTE = DIR / "fuente"

POST_GRUPOS = ("https://ffcv.es/wp/blog/2026/10/"
               "estos-son-los-grupos-de-segona-infantil-castello-para-la-temporada-2026-2027/")
FFCV_COMPETICIONES = "https://ffcv.es/competiciones/#partidos"

STATS = ["convocatorias", "titularidades", "suplencias", "jugados", "goles",
         "amarillas", "dobles_amarillas", "rojas", "verdes"]
STAT_LABEL = {"convocatorias": "Convocados", "titularidades": "Titular", "suplencias": "Suplente",
              "jugados": "Jugados", "goles": "Goles", "amarillas": "Amarillas",
              "dobles_amarillas": "Dobles amarillas", "rojas": "Rojas", "verdes": "Verdes"}

TABLAS = {
    "temporadas": ["temporada_id", "nombre"],
    "competiciones": ["competicion_id", "temporada_id", "nombre", "categoria", "ambito", "fuente_url"],
    "grupos": ["grupo_id", "competicion_id", "numero", "nombre", "fuente_url"],
    "equipos": ["equipo_id", "grupo_id", "nombre", "cod_ffcv", "fuente"],
    "jugadores": ["jugador_id", "nombre", "cod_ffcv", "anio_nacimiento", "anio_verificado",
                  "edad", "edad_fecha_ref"],
    "plantillas": ["jugador_id", "equipo_id", "dorsal", "posicion"],
    "estadisticas": ["jugador_id", "equipo_id", *STATS, "columnas_fuente", "archivo", "fecha_extraccion"],
    "jornadas": ["jugador_id", "equipo_id", "jornada", *STATS, "archivo"],
}
CLAVES = {"temporadas": ["temporada_id"], "competiciones": ["competicion_id"], "grupos": ["grupo_id"],
          "equipos": ["equipo_id"], "jugadores": ["jugador_id"], "plantillas": ["jugador_id", "equipo_id"],
          "estadisticas": ["jugador_id", "equipo_id"], "jornadas": ["jugador_id", "equipo_id", "jornada"]}


# ---------------------------------------------------------------- utilidades
def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9/%.]+", " ", s)).strip()


def slug(s) -> str:
    return re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")


_SIGLAS = {"CF", "CD", "ACD", "UD", "CE", "SAD", "BF", "FB", "FC", "RA", "SP."}


def nombre_visible(nombre: str) -> str:
    """'CD SAN LORENZO DE CASTELLÓN B' -> 'CD San Lorenzo de Castellón «B»' (solo presentación)."""
    toks = str(nombre).split()
    out = []
    for i, t in enumerate(toks):
        if t.upper() in _SIGLAS or re.fullmatch(r"\d+", t):
            out.append(t.upper() if t.upper() != "SP." else "Sp.")
        elif i == len(toks) - 1 and re.fullmatch(r"[B-H]", t) and i > 0:
            out.append(f"«{t}»")
        elif t.lower() in {"de", "del"} and i > 0:
            out.append(t.lower())
        else:
            out.append("-".join(p[:1].upper() + p[1:].lower() for p in t.split("-")))
    s = " ".join(out)
    return s.replace("D'a", "d'A").replace("L'a", "L'A")


def _vacio(v) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and not v.strip())


def to_num(v):
    """Número o None. Celdas vacías, '-' o texto no numérico -> None (N/D), nunca 0."""
    if _vacio(v):
        return None
    if isinstance(v, (int, float)):
        return None if pd.isna(v) else float(v)
    s = str(v).strip().replace(",", ".")
    m = re.fullmatch(r"-?\d+(\.\d+)?", s)
    return float(s) if m else None


# ---------------------------------------------------------------- almacenamiento
def load(tabla: str) -> pd.DataFrame:
    p = DIR / f"{tabla}.csv"
    cols = TABLAS[tabla]
    if not p.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8")
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df[cols]


def save(tabla: str, df: pd.DataFrame) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    df = df[TABLAS[tabla]].fillna("")
    df = df.drop_duplicates(CLAVES[tabla], keep="last").sort_values(CLAVES[tabla])
    df.to_csv(DIR / f"{tabla}.csv", index=False, encoding="utf-8")


def upsert(tabla: str, filas: list[dict]) -> int:
    if not filas:
        return 0
    old = load(tabla)
    new = pd.DataFrame(filas).astype(object).where(lambda d: d.notna(), "")
    for c in TABLAS[tabla]:
        if c not in new.columns:
            new[c] = ""
    new = new[TABLAS[tabla]].astype(str).replace({"None": "", "nan": ""})
    save(tabla, pd.concat([old, new], ignore_index=True))
    return len(new)


def meta() -> dict:
    p = DIR / "meta.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_meta(m: dict) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    (DIR / "meta.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- lectura de archivos
class _Tablas(HTMLParser):
    """Extrae tablas (texto y enlaces por fila) y títulos de un HTML guardado, sin dependencias."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tablas, self.titulos, self.hrefs = [], [], []
        self._t = self._r = self._c = None
        self._rh = []
        self._tit = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("href"):
            self.hrefs.append(a["href"])
        if tag == "table":
            self._t = []
        elif tag == "tr" and self._t is not None:
            self._r, self._rh = [], []
        elif tag in ("td", "th") and self._r is not None:
            self._c = []
            self._span = int(a.get("colspan") or 1) if str(a.get("colspan") or "1").isdigit() else 1
        elif tag == "a" and self._r is not None and a.get("href"):
            self._rh.append(a["href"])
        elif tag == "img" and self._c is not None and a.get("alt"):
            self._c.append(" " + a["alt"] + " ")
        elif tag in ("title", "h1", "h2", "h3"):
            self._tit = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._c is not None and self._r is not None:
            txt = re.sub(r"\s+", " ", "".join(self._c)).strip()
            self._r.extend([txt] + [""] * (self._span - 1))
            self._c = None
        elif tag == "tr" and self._r is not None and self._t is not None:
            if any(self._r):
                self._t.append((self._r, self._rh))
            self._r = None
        elif tag == "table" and self._t is not None:
            self.tablas.append(self._t)
            self._t = None
        elif tag in ("title", "h1", "h2", "h3") and self._tit is not None:
            t = re.sub(r"\s+", " ", "".join(self._tit)).strip()
            if t:
                self.titulos.append(t)
            self._tit = None

    def handle_data(self, data):
        if self._c is not None:
            self._c.append(data)
        if self._tit is not None:
            self._tit.append(data)


# Palabras clave de cabecera -> campo (el orden importa: lo más específico primero).
_CAB = [
    ("dobles_amarillas", r"dobl|2 ?amar|segunda amar"),
    ("goles_media", r"media|promedio|/ ?p|por partido"),
    ("amarillas", r"amarill|^ta$|^am$"),
    ("rojas", r"roja|^tr$"),
    ("verdes", r"verde"),
    ("convocatorias", r"convoc"),
    ("titularidades", r"titular"),
    ("suplencias", r"suplen"),
    ("jugados", r"jugados|^pj$|disputad|part.* jug"),
    ("goles", r"^gol|goles"),
    ("fecha_nac", r"nacim|f ?nac"),
    ("edad", r"^edad"),
    ("dorsal", r"dorsal|^n[ºo.]?$|^num"),
    ("posicion", r"posic|demarc|^pos$|puesto"),
    ("jornada", r"^jornada|^j$|^jor"),
    ("nombre", r"^jugador(a|es)?$|^jugador |nombre|futbolista"),
]


def _mapear(cabecera: list[str]) -> dict[int, str]:
    usados, m = set(), {}
    for i, h in enumerate(cabecera):
        h2 = norm(h)
        for campo, rx in _CAB:
            if campo not in usados and re.search(rx, h2):
                m[i] = campo
                usados.add(campo)
                break
    return m


def _filas_de_tabla(filas: list[tuple[list[str], list[str]]]):
    """Busca la fila de cabecera (nombre + al menos 1 estadística/edad) y devuelve registros."""
    for k, (cab, _) in enumerate(filas[:6]):
        m = _mapear(cab)
        if "nombre" in m.values() and set(m.values()) & (set(STATS) | {"edad", "fecha_nac"}):
            regs = []
            for celdas, hrefs in filas[k + 1:]:
                r = {campo: (celdas[i] if i < len(celdas) else "") for i, campo in m.items()}
                if not str(r.get("nombre", "")).strip() or norm(r["nombre"]) in {"total", "totales"}:
                    continue
                cod = next((mm.group(1) for h in hrefs
                            for mm in [re.search(r"cod_?jugador=(\d+)", h, re.I)] if mm), "")
                r["cod_ffcv"] = cod
                regs.append(r)
            return regs, sorted(set(m.values()))
    return [], []


def leer_archivo(nombre: str, contenido: bytes) -> dict:
    """Devuelve {'registros': [...], 'columnas': [...], 'titulos': [...], 'cod_equipo': str, 'jornadas': bool}."""
    ext = Path(nombre).suffix.lower()
    titulos, cod_eq = [], ""
    tablas: list[list[tuple[list[str], list[str]]]] = []
    if ext in (".html", ".htm", ".mhtml"):
        txt = contenido.decode("utf-8", errors="replace")
        p = _Tablas()
        p.feed(txt)
        tablas, titulos = p.tablas, p.titulos
        cod_eq = next((m.group(1) for h in p.hrefs for m in [re.search(r"cod_equipo=(\d+)", h)] if m), "")
    elif ext in (".csv", ".txt"):
        df = None
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(io.BytesIO(contenido), dtype=str, keep_default_na=False,
                                 sep=None, engine="python", encoding=enc)
                break
            except Exception:
                continue
        if df is not None:
            tablas = [[(list(df.columns), [])] + [(list(r), []) for r in df.values.tolist()]]
    elif ext in (".xlsx", ".xls"):
        for _, df in pd.read_excel(io.BytesIO(contenido), sheet_name=None, dtype=str).items():
            df = df.fillna("")
            tablas.append([(list(map(str, df.columns)), [])] + [(list(r), []) for r in df.values.tolist()])
    else:
        raise ValueError(f"Formato no admitido: {ext}. Usa HTML guardado, CSV o XLSX.")
    regs, cols = [], []
    for t in tablas:
        r, c = _filas_de_tabla(t)
        regs += r
        cols = sorted(set(cols) | set(c))
    return {"registros": regs, "columnas": cols, "titulos": titulos, "cod_equipo": cod_eq,
            "jornadas": "jornada" in cols}


# ---------------------------------------------------------------- importación
def _edad_y_anio(r: dict, hoy: date):
    """Año de nacimiento solo si la fuente da la fecha (o el año) explícitamente. Nunca se deduce de la edad."""
    anio, verif, edad = "", "no", ""
    f = str(r.get("fecha_nac", "") or "").strip()
    m = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", f) or re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", f)
    if m:
        g = [int(x) for x in m.groups()]
        d, mo, y = (g[2], g[1], g[0]) if g[0] > 31 else (g[0], g[1], g[2])
        try:
            fn = date(y, mo, d)
            anio, verif = str(y), "si"
            edad = str(hoy.year - y - ((hoy.month, hoy.day) < (fn.month, fn.day)))
        except ValueError:
            pass
    elif re.fullmatch(r"(19|20)\d{2}", f):
        anio, verif = f, "si"
    if not edad:
        e = to_num(r.get("edad"))
        edad = str(int(e)) if e is not None else ""
    return anio, verif, edad


def importar(equipo_id: str, nombre_archivo: str, contenido: bytes, guardar_copia: bool = True) -> dict:
    """Importa un archivo de un equipo. Idempotente: reimportar el mismo archivo no duplica nada."""
    eqs = load("equipos")
    if equipo_id not in set(eqs.equipo_id):
        raise ValueError(f"Equipo desconocido: {equipo_id}")
    res = leer_archivo(nombre_archivo, contenido)
    if not res["registros"]:
        return {"ok": False, "jugadores": 0, "columnas": res["columnas"], "titulos": res["titulos"][:3],
                "mensaje": "No se ha encontrado una tabla de jugadores reconocible (cabeceras Jugador + estadísticas)."}
    hoy = date.today()
    ahora = datetime.now().isoformat(timespec="seconds")
    if guardar_copia:
        dst = FUENTE / equipo_id
        dst.mkdir(parents=True, exist_ok=True)
        (dst / Path(nombre_archivo).name).write_bytes(contenido)
    if res["cod_equipo"]:
        eqs.loc[eqs.equipo_id == equipo_id, "cod_ffcv"] = res["cod_equipo"]
        save("equipos", eqs)
    jug, plant, est, jor = [], [], [], []
    stats_cols = [c for c in STATS if c in res["columnas"]]
    for r in res["registros"]:
        nombre = re.sub(r"\s+", " ", str(r["nombre"])).strip()
        jid = f"ffcv-{r['cod_ffcv']}" if r.get("cod_ffcv") else f"{equipo_id}--{slug(nombre)}"
        anio, verif, edad = _edad_y_anio(r, hoy)
        jug.append({"jugador_id": jid, "nombre": nombre, "cod_ffcv": r.get("cod_ffcv", ""),
                    "anio_nacimiento": anio, "anio_verificado": verif, "edad": edad,
                    "edad_fecha_ref": hoy.isoformat() if edad else ""})
        dorsal = to_num(r.get("dorsal"))
        plant.append({"jugador_id": jid, "equipo_id": equipo_id,
                      "dorsal": str(int(dorsal)) if dorsal is not None else "",
                      "posicion": str(r.get("posicion", "") or "").strip()})
        vals = {c: (lambda x: "" if x is None else str(int(x)))(to_num(r.get(c))) for c in STATS}
        if res["jornadas"]:
            j = to_num(r.get("jornada"))
            if j is not None:
                jor.append({"jugador_id": jid, "equipo_id": equipo_id, "jornada": str(int(j)),
                            **vals, "archivo": nombre_archivo})
        else:
            est.append({"jugador_id": jid, "equipo_id": equipo_id, **vals,
                        "columnas_fuente": ";".join(stats_cols), "archivo": nombre_archivo,
                        "fecha_extraccion": ahora})
    # Un jugador puede repetirse por jornada: conservar una ficha por id.
    upsert("jugadores", list({j["jugador_id"]: j for j in jug}.values()))
    upsert("plantillas", list({(p["jugador_id"], p["equipo_id"]): p for p in plant}.values()))
    upsert("estadisticas", est)
    upsert("jornadas", jor)
    m = meta()
    h = hashlib.sha256(contenido).hexdigest()
    m.setdefault("archivos", {})[f"{equipo_id}/{Path(nombre_archivo).name}"] = {"sha256": h, "importado": ahora}
    m["ultima_actualizacion"] = ahora
    save_meta(m)
    return {"ok": True, "jugadores": len({j["jugador_id"] for j in jug}), "columnas": res["columnas"],
            "jornadas": res["jornadas"], "mensaje": "Importado"}


def actualizar_desde_fuente() -> dict:
    """Botón «Actualizar FFCV»: reprocesa las copias locales (data/scouting/fuente/<equipo>/).
    Solo se procesan archivos nuevos o modificados; no se hace ninguna petición a la API de la FFCV."""
    m = meta().get("archivos", {})
    nuevos = sin_cambios = errores = 0
    detalles = []
    if FUENTE.exists():
        for f in sorted(FUENTE.glob("*/*")):
            if not f.is_file() or f.name.startswith("."):
                continue
            clave = f"{f.parent.name}/{f.name}"
            data = f.read_bytes()
            if m.get(clave, {}).get("sha256") == hashlib.sha256(data).hexdigest():
                sin_cambios += 1
                continue
            try:
                r = importar(f.parent.name, f.name, data, guardar_copia=False)
                nuevos += r["ok"]
                errores += not r["ok"]
                detalles.append(f"{clave}: {r['mensaje']} ({r.get('jugadores', 0)} jugadores)")
            except Exception as e:  # archivo dañado o equipo inexistente
                errores += 1
                detalles.append(f"{clave}: error {e}")
    mm = meta()
    mm["ultima_comprobacion"] = datetime.now().isoformat(timespec="seconds")
    save_meta(mm)
    return {"nuevos": nuevos, "sin_cambios": sin_cambios, "errores": errores, "detalles": detalles}


def comprobar_publicacion_grupos(timeout: int = 10) -> dict:
    """Consulta UNA página del blog oficial (permitida por robots.txt) y compara la lista de imágenes
    de grupos con la registrada. Sirve para detectar si la FFCV ha cambiado los grupos."""
    import urllib.request
    req = urllib.request.Request(POST_GRUPOS, headers={"User-Agent": "PrimerToque-Scouting/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        txt = resp.read().decode("utf-8", errors="replace")
    i = txt.rfind("ha hecho p")
    imgs = sorted(set(re.findall(r"uploads/2026/1\d/(\d+-\d+)-763x1024", txt[max(i, 0):max(i, 0) + 20000])))
    n = re.search(r"los (\d+) grupos", txt[max(i - 400, 0):i + 400])
    mm = meta()
    prev = mm.get("publicacion_grupos", {}).get("imagenes")
    mm["publicacion_grupos"] = {"imagenes": imgs, "grupos_anunciados": int(n.group(1)) if n else None,
                                "comprobado": datetime.now().isoformat(timespec="seconds")}
    save_meta(mm)
    return {"imagenes": imgs, "cambiada": prev is not None and prev != imgs,
            "grupos_anunciados": mm["publicacion_grupos"]["grupos_anunciados"]}


def borrar_importacion_equipo(equipo_id: str) -> None:
    """Elimina los datos importados de un equipo (para corregir una importación equivocada)."""
    for t in ("plantillas", "estadisticas", "jornadas"):
        df = load(t)
        save(t, df[df.equipo_id != equipo_id])
    vivos = set(load("plantillas").jugador_id)
    j = load("jugadores")
    save("jugadores", j[j.jugador_id.isin(vivos)])
    shutil.rmtree(FUENTE / equipo_id, ignore_errors=True)
    m = meta()
    m["archivos"] = {k: v for k, v in m.get("archivos", {}).items() if not k.startswith(equipo_id + "/")}
    save_meta(m)


# ---------------------------------------------------------------- consultas
def tabla_jugadores() -> pd.DataFrame:
    """Una fila por jugador-equipo con estadísticas numéricas (NaN = N/D) y métricas derivadas."""
    pl, j, e = load("plantillas"), load("jugadores"), load("estadisticas")
    eq, gr = load("equipos"), load("grupos")
    if pl.empty:
        return pd.DataFrame(columns=["jugador_id", "equipo_id", "nombre", "equipo", "grupo_id", "grupo",
                                     *STATS, "edad", "posicion", "dorsal"])
    df = pl.merge(j, on="jugador_id", how="left").merge(e.drop(columns=["archivo"]), on=["jugador_id", "equipo_id"], how="left")
    jor = load("jornadas")
    if not jor.empty:  # equipos importados por jornadas: totales = suma de jornadas verificadas
        jj = jor.copy()
        for c in STATS:
            jj[c] = pd.to_numeric(jj[c], errors="coerce")
        agg = jj.groupby(["jugador_id", "equipo_id"])[STATS].sum(min_count=1).reset_index()
        df = df.merge(agg, on=["jugador_id", "equipo_id"], how="left", suffixes=("", "_j"))
        for c in STATS:
            base = pd.to_numeric(df[c], errors="coerce")
            df[c] = base.where(base.notna(), df[c + "_j"])
            df = df.drop(columns=c + "_j")
    for c in STATS + ["edad", "dorsal"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.merge(eq[["equipo_id", "grupo_id", "nombre"]].rename(columns={"nombre": "equipo_oficial"}), on="equipo_id", how="left")
    df = df.merge(gr[["grupo_id", "nombre"]].rename(columns={"nombre": "grupo"}), on="grupo_id", how="left")
    df["equipo"] = df["equipo_oficial"].map(nombre_visible)
    conv, jug = df["convocatorias"], df["jugados"]
    df["pct_titular"] = (df["titularidades"] / conv * 100).where(conv > 0)
    df["pct_participacion"] = (jug / conv * 100).where(conv > 0)
    df["goles_partido"] = (df["goles"] / jug).where(jug > 0)
    df["tarjetas"] = df[["amarillas", "rojas"]].sum(axis=1, min_count=2)
    df["pct_sin_sancion"] = pct_sin_sancion(df)
    return df


def pct_sin_sancion(df: pd.DataFrame) -> pd.Series:
    """Solo calculable con datos por jornada: % de partidos jugados sin amarilla ni roja."""
    jor = load("jornadas")
    out = pd.Series(float("nan"), index=df.index)
    if jor.empty:
        return out
    jj = jor.copy()
    for c in ["jugados", "amarillas", "dobles_amarillas", "rojas"]:
        jj[c] = pd.to_numeric(jj[c], errors="coerce")
    jj = jj[jj.jugados > 0]
    if jj[["amarillas", "rojas"]].isna().any(axis=None):
        jj = jj.dropna(subset=["amarillas", "rojas"])
    g = jj.assign(limpio=(jj.amarillas.fillna(0) + jj.rojas.fillna(0) + jj.dobles_amarillas.fillna(0)) == 0)
    r = g.groupby(["jugador_id", "equipo_id"]).limpio.mean() * 100
    keys = list(zip(df.jugador_id, df.equipo_id))
    return pd.Series([r.get(k, float("nan")) for k in keys], index=df.index)


def estado_equipos() -> pd.DataFrame:
    """Estado de datos por equipo: importado / pendiente."""
    eq = load("equipos")
    pl = load("plantillas")
    n = pl.groupby("equipo_id").size()
    eq["jugadores"] = eq.equipo_id.map(n).fillna(0).astype(int)
    eq["estado"] = eq.jugadores.map(lambda x: "importado" if x else "pendiente")
    return eq
