from pathlib import Path

ROOT_APP = Path(__file__).resolve().parents[1] / "app.py"
_code = compile(ROOT_APP.read_text(encoding="utf-8"), str(ROOT_APP), "exec")
globals()["__file__"] = str(ROOT_APP)
exec(_code, globals())
