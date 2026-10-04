import base64
import html
from pathlib import Path

import pandas as pd
import streamlit as st


# --- Fallback robusto Villarreal J1-J5 ---
_VIL_TEAM = "Villarreal C.F. 'C'"
_vil_partidos = pd.DataFrame([{'jornada': 1, 'fecha': '06/09/2026', 'local': "Villarreal C.F. 'C'", 'visitante': "C.F. Històrics de València 'A'", 'goles_local': 4, 'goles_visitante': 1, 'campo': 'Ciudad Dptva. José Manuel Llaneza F-11 Vila-real', 'sistema_local': '1-4-4-2', 'sistema_visitante': '1-4-3-3', 'estado': 'validado'}, {'jornada': 2, 'fecha': '12/09/2026', 'local': "Col. Salgui E.D.E. 'A'", 'visitante': "Villarreal C.F. 'C'", 'goles_local': 0, 'goles_visitante': 1, 'campo': 'Campo Fútbol Marcelino F-11', 'sistema_local': '1-4-3-3', 'sistema_visitante': '1-4-4-2', 'estado': 'validado'}, {'jornada': 3, 'fecha': '20/09/2026', 'local': "Bétera C.F. 'A'", 'visitante': "Villarreal C.F. 'C'", 'goles_local': 2, 'goles_visitante': 2, 'campo': 'Polideportivo Mpal. de Bétera F-11', 'sistema_local': '1-5-4-1', 'sistema_visitante': '1-4-4-2', 'estado': 'validado'}, {'jornada': 4, 'fecha': '27/09/2026', 'local': "Villarreal C.F. 'C'", 'visitante': "Paterna C.F. 'A'", 'goles_local': 5, 'goles_visitante': 2, 'campo': 'Ciudad Dptva. José Manuel Llaneza F-11 Vila-real Campo 5', 'sistema_local': '1-4-4-2', 'sistema_visitante': '1-5-4-1', 'estado': 'validado'}, {'jornada': 5, 'fecha': '04/10/2026', 'local': "Patacona C.F. 'B'", 'visitante': "Villarreal C.F. 'C'", 'goles_local': 0, 'goles_visitante': 3, 'campo': 'Campo Mpal. Patacona F-11', 'sistema_local': '1-5-4-1', 'sistema_visitante': '1-4-4-2', 'estado': 'validado'}])
_vil_minutos = pd.DataFrame([{'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 1, 'jugador': 'Daniil Didenko Rohava', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 3, 'jugador': 'Eduardo De Haro Hernández', 'minutos': 82, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 5, 'jugador': 'Manolo Rubert Colonques', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'minutos': 63, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'minutos': 82, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa', 'minutos': 37, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'minutos': 63, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 24, 'jugador': 'Eric Rodriguez Casas', 'minutos': 53, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 15, 'jugador': 'Andres Borras Maestre', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes', 'minutos': 27, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 11, 'jugador': 'Raul Estephano Varzaru Varzaru', 'minutos': 27, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 17, 'jugador': 'Gael Palomar Medina', 'minutos': 8, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 23, 'jugador': 'Salim Khassanov', 'minutos': 8, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 1, 'jugador': 'Daniil Didenko Rohava', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'minutos': 63, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 27, 'jugador': 'Balla Dembele Kamissoko', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'minutos': 80, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'minutos': 60, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa', 'minutos': 60, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'minutos': 80, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes', 'minutos': 10, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 15, 'jugador': 'Andres Borras Maestre', 'minutos': 27, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'minutos': 30, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 21, 'jugador': 'Yago Lapuente Martin', 'minutos': 30, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 11, 'jugador': 'Raul Estephano Varzaru Varzaru', 'minutos': 10, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 23, 'jugador': 'Salim Khassanov', 'minutos': 10, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 1, 'jugador': 'Daniil Didenko Rohava', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'minutos': 65, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'minutos': 77, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 21, 'jugador': 'Yago Lapuente Martin', 'minutos': 84, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'minutos': 65, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'minutos': 77, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 15, 'jugador': 'Andres Borras Maestre', 'minutos': 25, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 17, 'jugador': 'Gael Palomar Medina', 'minutos': 25, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 5, 'jugador': 'Manolo Rubert Colonques', 'minutos': 6, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 27, 'jugador': 'Alvaro Tarraso Perez', 'minutos': 13, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 24, 'jugador': 'Pablo Lopez Argüello', 'minutos': 13, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 25, 'jugador': 'Samuel Ramirez Batchuluun', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'minutos': 57, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'minutos': 67, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 15, 'jugador': 'Andres Borras Maestre', 'minutos': 57, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'minutos': 67, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'minutos': 67, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 21, 'jugador': 'Yago Lapuente Martin', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 17, 'jugador': 'Gael Palomar Medina', 'minutos': 23, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 11, 'jugador': 'Raul Estephano Varzaru Varzaru', 'minutos': 23, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 27, 'jugador': 'Neville Winston Knowles III', 'minutos': 23, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 5, 'jugador': 'Manolo Rubert Colonques', 'minutos': 33, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'minutos': 33, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 25, 'jugador': 'Samuel Ramirez Batchuluun', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 15, 'jugador': 'Andres Borras Maestre', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'minutos': 72, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'minutos': 72, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'minutos': 58, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'minutos': 65, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 4, 'jugador': 'Jesús Caballero Huguet', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa', 'minutos': 18, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 11, 'jugador': 'Raul Estephano Varzaru Varzaru', 'minutos': 18, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 17, 'jugador': 'Gael Palomar Medina', 'minutos': 32, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 27, 'jugador': 'Victor Maestra Rodriguez', 'minutos': 25, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}])
_vil_eventos = pd.DataFrame([{'jornada': 1, 'equipo': "Villarreal C.F. 'C'", 'minuto': 9, 'tipo': 'gol', 'jugador': 'Franklin Chinedu Okolie Okolie', 'detalle': ''}, {'jornada': 1, 'equipo': "Villarreal C.F. 'C'", 'minuto': 50, 'tipo': 'gol', 'jugador': 'Franklin Chinedu Okolie Okolie', 'detalle': ''}, {'jornada': 1, 'equipo': "Villarreal C.F. 'C'", 'minuto': 83, 'tipo': 'penalti_gol', 'jugador': 'Adrian Diaz Fuentes', 'detalle': 'Gol de penalti'}, {'jornada': 1, 'equipo': "Villarreal C.F. 'C'", 'minuto': 90, 'tipo': 'gol', 'jugador': 'Salim Khassanov', 'detalle': ''}, {'jornada': 1, 'equipo': "Villarreal C.F. 'C'", 'minuto': 77, 'tipo': 'gol_contra', 'jugador': 'Rival', 'detalle': ''}, {'jornada': 2, 'equipo': "Villarreal C.F. 'C'", 'minuto': 57, 'tipo': 'gol', 'jugador': 'Gabriel Duarte Santacruz', 'detalle': ''}, {'jornada': 2, 'equipo': "Villarreal C.F. 'C'", 'minuto': 9, 'tipo': 'amarilla', 'jugador': 'Adrian Diaz Fuentes', 'detalle': ''}, {'jornada': 2, 'equipo': "Villarreal C.F. 'C'", 'minuto': 10, 'tipo': 'doble_amarilla', 'jugador': 'Adrian Diaz Fuentes', 'detalle': 'segunda amarilla / expulsión'}, {'jornada': 3, 'equipo': "Villarreal C.F. 'C'", 'minuto': 43, 'tipo': 'gol', 'jugador': 'Nahuel Abadia Garcia', 'detalle': ''}, {'jornada': 3, 'equipo': "Villarreal C.F. 'C'", 'minuto': 60, 'tipo': 'gol', 'jugador': 'Gabriel Duarte Santacruz', 'detalle': ''}, {'jornada': 3, 'equipo': "Villarreal C.F. 'C'", 'minuto': 8, 'tipo': 'gol_contra', 'jugador': 'G.P. Héctor García Vaca', 'detalle': 'Gol en propia'}, {'jornada': 3, 'equipo': "Villarreal C.F. 'C'", 'minuto': 78, 'tipo': 'gol_contra', 'jugador': 'Rival', 'detalle': ''}, {'jornada': 3, 'equipo': "Villarreal C.F. 'C'", 'minuto': 68, 'tipo': 'amarilla', 'jugador': 'Gabriel Duarte Santacruz', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 21, 'tipo': 'gol', 'jugador': 'Gabriel Duarte Santacruz', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 30, 'tipo': 'gol', 'jugador': 'Franklin Chinedu Okolie Okolie', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 46, 'tipo': 'gol', 'jugador': 'Gabriel Duarte Santacruz', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 48, 'tipo': 'gol', 'jugador': 'Gabriel Duarte Santacruz', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 62, 'tipo': 'gol', 'jugador': 'Yago Lapuente Martin', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 13, 'tipo': 'gol_contra', 'jugador': 'Rival', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 67, 'tipo': 'gol_contra', 'jugador': 'Rival', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 12, 'tipo': 'amarilla', 'jugador': 'Hector Garcia Vaca', 'detalle': ''}, {'jornada': 4, 'equipo': "Villarreal C.F. 'C'", 'minuto': 87, 'tipo': 'amarilla', 'jugador': 'Raul Estephano Varzaru Varzaru', 'detalle': ''}, {'jornada': 5, 'equipo': "Villarreal C.F. 'C'", 'minuto': 64, 'tipo': 'gol', 'jugador': 'Pablo Tortajada Balaguer', 'detalle': ''}, {'jornada': 5, 'equipo': "Villarreal C.F. 'C'", 'minuto': 71, 'tipo': 'gol', 'jugador': 'Victor Maestra Rodriguez', 'detalle': ''}, {'jornada': 5, 'equipo': "Villarreal C.F. 'C'", 'minuto': 89, 'tipo': 'gol', 'jugador': 'Adrian Diaz Fuentes', 'detalle': ''}, {'jornada': 5, 'equipo': "Villarreal C.F. 'C'", 'minuto': 12, 'tipo': 'amarilla', 'jugador': 'Pablo Tortajada Balaguer', 'detalle': ''}, {'jornada': 5, 'equipo': "Villarreal C.F. 'C'", 'minuto': 44, 'tipo': 'amarilla', 'jugador': 'Ian Mendez Untiveros', 'detalle': ''}])
_vil_alineaciones = pd.DataFrame([{'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 1, 'jugador': 'Daniil Didenko Rohava', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 3, 'jugador': 'Eduardo De Haro Hernández', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 5, 'jugador': 'Manolo Rubert Colonques', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 1, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 1, 'jugador': 'Daniil Didenko Rohava', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 27, 'jugador': 'Balla Dembele Kamissoko', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 2, 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 1, 'jugador': 'Daniil Didenko Rohava', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 21, 'jugador': 'Yago Lapuente Martin', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 3, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 25, 'jugador': 'Samuel Ramirez Batchuluun', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 15, 'jugador': 'Andres Borras Maestre', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 21, 'jugador': 'Yago Lapuente Martin', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 4, 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 25, 'jugador': 'Samuel Ramirez Batchuluun', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 6, 'jugador': 'Hector Garcia Vaca', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 15, 'jugador': 'Andres Borras Maestre', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Villarreal C.F. 'C'", 'jornada': 5, 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes', 'rol': 'ATA', 'linea': 4, 'orden': 2}])
_vil_plantilla = pd.DataFrame([{'equipo': "Villarreal C.F. 'C'", 'dorsal': 1, 'jugador': 'Daniil Didenko Rohava'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 2, 'jugador': 'Hugo Zoroa Domingo'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 3, 'jugador': 'Eduardo De Haro Hernández'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 5, 'jugador': 'Manolo Rubert Colonques'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 6, 'jugador': 'Hector Garcia Vaca'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 10, 'jugador': 'Gabriel Duarte Santacruz'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 18, 'jugador': 'Pablo Tortajada Balaguer'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 19, 'jugador': 'Adrian Cantalapiedra Cocho'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 22, 'jugador': 'Nahuel Abadia Garcia'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 8, 'jugador': 'Darlington Oghosa Izekor Osazuwa'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 9, 'jugador': 'Franklin Chinedu Okolie Okolie'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 24, 'jugador': 'Eric Rodriguez Casas'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 15, 'jugador': 'Andres Borras Maestre'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 20, 'jugador': 'Adrian Diaz Fuentes'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 11, 'jugador': 'Raul Estephano Varzaru Varzaru'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 17, 'jugador': 'Gael Palomar Medina'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 23, 'jugador': 'Salim Khassanov'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 3, 'jugador': 'Adrian Gregori Villanueva'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 14, 'jugador': 'Ian Mendez Untiveros'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 27, 'jugador': 'Balla Dembele Kamissoko'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 21, 'jugador': 'Yago Lapuente Martin'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 27, 'jugador': 'Alvaro Tarraso Perez'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 24, 'jugador': 'Pablo Lopez Argüello'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 25, 'jugador': 'Samuel Ramirez Batchuluun'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 27, 'jugador': 'Neville Winston Knowles III'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 4, 'jugador': 'Jesús Caballero Huguet'}, {'equipo': "Villarreal C.F. 'C'", 'dorsal': 27, 'jugador': 'Victor Maestra Rodriguez'}])

st.set_page_config(
    page_title="Fútbol Data Joan",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
DATA = BASE / "data"

MATCH_LINKS = {
    # Villarreal
    ("Villarreal C.F. 'C'", 1): "https://youtu.be/45hlhA5vbIc",
    ("Villarreal C.F. 'C'", 2): "https://app.veo.co/matches/20260912-partido-12-sept-2026-v2488402/",
    ("Villarreal C.F. 'C'", 3): "https://app.veo.co/matches/20260920-juvenil-a-vs-villareal-cf-v78c4164/",
    ("Villarreal C.F. 'C'", 4): "https://youtu.be/rUAjYCPcnrI",

    # Primer Toque
    ("Primer Toque C.F. 'A'", 1): "https://app.veo.co/matches/20260906-juvenil-vs-primer-toque-v69cf952/",
    ("Primer Toque C.F. 'A'", 2): "https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/",
    ("Primer Toque C.F. 'A'", 3): "https://app.veo.co/matches/20260919-juvenil-a-manises-v678eca9/",
    ("Primer Toque C.F. 'A'", 4): "https://app.veo.co/matches/20260927-partido-cdf-canet-vae71aeb",
    ("Primer Toque C.F. 'A'", 5): "https://app.veo.co/matches/20261003-juvenil-a-alboraya-v1bf5286/",

    # Bétera
    ("Bétera C.F. 'A'", 1): "https://app.veo.co/matches/20260906-juvenil-a-vs-col-salgui-v9022f29/",
    ("Bétera C.F. 'A'", 2): "https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/",
    ("Bétera C.F. 'A'", 3): "https://app.veo.co/matches/20260920-juvenil-a-vs-villareal-cf-v78c4164/",
    ("Bétera C.F. 'A'", 4): "https://youtu.be/FwkojfoAnAs?is=a3cp8o-yYGS8kTXm",

    # C.D. Acero
    ("C.D. Acero 'A'", 1): "https://app.veo.co/matches/20260906-patacona-cf-jb-vs-acero-v97c8cc3/",
    ("C.D. Acero 'A'", 2): "https://app.veo.co/matches/20260913-untitled-recording-2026-09-13_17-14-50-va669c7b",
    ("C.D. Acero 'A'", 3): "https://app.veo.co/matches/20260919-juvenil-a-b-vs-ja-cd-acero-v3e5feb3/#t=05:45",
    ("C.D. Acero 'A'", 4): "https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-16-26-v42537de/",

    # Burriana - Salesianos
    ("C.F. At. Burriana - Salesianos 'A'", 1): "https://app.veo.co/matches/20260905-juvenil-a-burriana-v4434b85/",
    ("C.F. At. Burriana - Salesianos 'A'", 2): "https://app.veo.co/matches/20260913-juvenil-a-contra-patacona-v7ea2f8f/",
    ("C.F. At. Burriana - Salesianos 'A'", 3): "https://app.veo.co/matches/20260919-jb-vs-at-burriana-salesianos-v00500cf",
    ("C.F. At. Burriana - Salesianos 'A'", 4): "https://app.veo.co/matches/20260927-untitled-recording-2026-09-27_17-07-43-v157dcb5",
}

# Sincronización validada de goles entre acta FFCV, reloj de partido en Veo y
# timestamp absoluto del vídeo. Son tres relojes distintos y NO se deben mezclar.
# - ffcv_min: minuto del acta oficial usado en los eventos de la app.
# - veo_match_clock: reloj de partido/evento que muestra Veo.
# - video_timestamp: posición absoluta dentro del vídeo completo de Veo.
# - event_url: enlace específico al evento cuando se ha podido validar.
VEO_GOAL_SYNC = {
    (2, "Sebas"): {
        "ffcv_min": 62,
        "veo_match_clock": "66:40",
        "veo_event_min": 67,
        "video_timestamp": "87:47",
        "event_url": "https://app.veo.co/matches/20260912-juvenil-a-betera-ve022cb5/?event_type=FootballShotGoal&event=5e990f44-af76-11f1-b212-0708876e5205#/events/",
    },
    (2, "Núñez"): {
        "ffcv_min": 87,
        "veo_match_clock": "90:00",
        "veo_event_min": 90,
        "video_timestamp": "110:46",
        "event_url": None,
    },
}

def match_link(team, jornada):
    try:
        return MATCH_LINKS.get((str(team), int(jornada)))
    except Exception:
        return None

def short_team_name(name):
    out = str(name)
    for suffix in [" 'A'", " 'B'", " 'C'"]:
        out = out.replace(suffix, "")
    return out


@st.cache_data
def load_csv(name):
    p = DATA / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

equipos = load_csv("equipos_liga.csv")
plantillas = load_csv("plantillas_rivales.csv")
minutos = load_csv("minutos_rivales.csv")
partidos = load_csv("partidos_rivales.csv")
eventos = load_csv("eventos_rivales.csv")
clasificacion = load_csv("clasificacion_liga.csv")
alineaciones = load_csv("alineaciones_rivales.csv")

# Integración robusta Villarreal J1-J5: se aplica DESPUÉS de cargar los CSV.
# Así evitamos NameError y sustituimos únicamente las filas del Villarreal.
if not partidos.empty:
    partidos = partidos[~((partidos["local"] == _VIL_TEAM) | (partidos["visitante"] == _VIL_TEAM))].copy()
partidos = pd.concat([partidos, _vil_partidos], ignore_index=True)

if not minutos.empty:
    minutos = minutos[minutos["equipo"] != _VIL_TEAM].copy()
minutos = pd.concat([minutos, _vil_minutos], ignore_index=True)

if not eventos.empty:
    eventos = eventos[eventos["equipo"] != _VIL_TEAM].copy()
eventos = pd.concat([eventos, _vil_eventos], ignore_index=True)

if not alineaciones.empty:
    alineaciones = alineaciones[alineaciones["equipo"] != _VIL_TEAM].copy()
alineaciones = pd.concat([alineaciones, _vil_alineaciones], ignore_index=True)

if not plantillas.empty:
    plantillas = plantillas[plantillas["equipo"] != _VIL_TEAM].copy()
plantillas = pd.concat([plantillas, _vil_plantilla], ignore_index=True)

# --- Fallback robusto Primer Toque J1-J5 ---
# Si Streamlit conserva CSV antiguos, estas filas canónicas sustituyen solo Primer Toque.
_PT_TEAM = "Primer Toque C.F. 'A'"
_pt_partidos = pd.DataFrame([{'jornada': 1, 'fecha': '06/09/2026', 'local': "Ath. Massamagrell C.F. 'A'", 'visitante': "Primer Toque C.F. 'A'", 'goles_local': 1.0, 'goles_visitante': 0.0, 'campo': 'Estadio Mpal. San Lorenzo F-11 Albuixech', 'sistema_local': '1-4-4-2', 'sistema_visitante': '1-4-4-2', 'estado': 'validado'}, {'jornada': 2, 'fecha': '12/09/2026', 'local': "Primer Toque C.F. 'A'", 'visitante': "Bétera C.F. 'A'", 'goles_local': 2.0, 'goles_visitante': 0.0, 'campo': 'Ciudad Dptva. Chencho Campo A F-11 Castellón', 'sistema_local': '1-4-4-2', 'sistema_visitante': '1-4-3-3', 'estado': 'validado'}, {'jornada': 3, 'fecha': '19/09/2026', 'local': "Primer Toque C.F. 'A'", 'visitante': "Manises C.F. 'A'", 'goles_local': 2.0, 'goles_visitante': 1.0, 'campo': 'Ciudad Dptva. Chencho Campo A F-11 Castellón', 'sistema_local': '1-4-4-2', 'sistema_visitante': '1-4-3-3', 'estado': 'validado'}, {'jornada': 4, 'fecha': '27/09/2026', 'local': "C.D.F. Canet 'A'", 'visitante': "Primer Toque C.F. 'A'", 'goles_local': 1.0, 'goles_visitante': 0.0, 'campo': 'Camp La Figuereta F-11 Canet Berenguer', 'sistema_local': '1-4-3-3', 'sistema_visitante': '1-5-4-1', 'estado': 'validado'}, {'jornada': 5, 'fecha': '03/10/2026', 'local': "Primer Toque C.F. 'A'", 'visitante': "Alboraya U.D. 'B'", 'goles_local': 1.0, 'goles_visitante': 2.0, 'campo': 'Ciudad Dptva. Chencho Campo A F-11 Castellón', 'sistema_local': '1-4-4-2', 'sistema_visitante': '1-4-3-3', 'estado': 'validado'}])
_pt_minutos = pd.DataFrame([{'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 1, 'jugador': 'Alessio', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 2, 'jugador': 'Chelli', 'minutos': 77, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 3, 'jugador': 'Irakli', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 4, 'jugador': 'Sánchez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 14, 'jugador': 'Blázquez', 'minutos': 77, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 21, 'jugador': 'Pedro', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 8, 'jugador': 'Toni', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 10, 'jugador': 'Bilal', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 30, 'jugador': 'Boyan', 'minutos': 65, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 9, 'jugador': 'Sebas', 'minutos': 65, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 24, 'jugador': 'Núñez', 'minutos': 77, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 28, 'jugador': 'Pau', 'minutos': 13, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 6, 'jugador': 'Dennis', 'minutos': 13, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 17, 'jugador': 'Abde', 'minutos': 13, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 19, 'jugador': 'Mois', 'minutos': 25, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 7, 'jugador': 'Ian', 'minutos': 25, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 1, 'jugador': 'Alessio', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 2, 'jugador': 'Chelli', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 3, 'jugador': 'Irakli', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 5, 'jugador': 'Xavi', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 14, 'jugador': 'Blázquez', 'minutos': 82, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 7, 'jugador': 'Ian', 'minutos': 67, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 10, 'jugador': 'Bilal', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 19, 'jugador': 'Mois', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 21, 'jugador': 'Pedro', 'minutos': 82, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 9, 'jugador': 'Sebas', 'minutos': 77, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 24, 'jugador': 'Núñez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 8, 'jugador': 'Toni', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 17, 'jugador': 'Abde', 'minutos': 23, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 11, 'jugador': 'Fran', 'minutos': 13, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 4, 'jugador': 'Sánchez', 'minutos': 8, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 30, 'jugador': 'Boyan', 'minutos': 8, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 13, 'jugador': 'Jordi', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 2, 'jugador': 'Chelli', 'minutos': 86, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 4, 'jugador': 'Sánchez', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 8, 'jugador': 'Toni', 'minutos': 56, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 14, 'jugador': 'Blázquez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 7, 'jugador': 'Ian', 'minutos': 65, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 10, 'jugador': 'Bilal', 'minutos': 86, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 16, 'jugador': 'Hamza', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 21, 'jugador': 'Pedro', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 9, 'jugador': 'Sebas', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 24, 'jugador': 'Núñez', 'minutos': 80, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 3, 'jugador': 'Irakli', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 5, 'jugador': 'Xavi', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 6, 'jugador': 'Dennis', 'minutos': 4, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 11, 'jugador': 'Fran', 'minutos': 10, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 19, 'jugador': 'Mois', 'minutos': 25, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 13, 'jugador': 'Jordi', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 2, 'jugador': 'Chelli', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 3, 'jugador': 'Irakli', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 4, 'jugador': 'Sánchez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 5, 'jugador': 'Xavi', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 14, 'jugador': 'Blázquez', 'minutos': 83, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 7, 'jugador': 'Ian', 'minutos': 72, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 16, 'jugador': 'Hamza', 'minutos': 61, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 21, 'jugador': 'Pedro', 'minutos': 82, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 24, 'jugador': 'Núñez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 19, 'jugador': 'Mois', 'minutos': 72, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 6, 'jugador': 'Dennis', 'minutos': 8, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 17, 'jugador': 'Abde', 'minutos': 18, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 28, 'jugador': 'Pau', 'minutos': 18, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 9, 'jugador': 'Sebas', 'minutos': 29, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 1, 'jugador': 'Alessio', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 3, 'jugador': 'Irakli', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 4, 'jugador': 'Sánchez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 5, 'jugador': 'Xavi', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 28, 'jugador': 'Pau', 'minutos': 52, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 8, 'jugador': 'Toni', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 9, 'jugador': 'Sebas', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 10, 'jugador': 'Bilal', 'minutos': 86, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 17, 'jugador': 'Abde', 'minutos': 75, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 19, 'jugador': 'Mois', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 24, 'jugador': 'Núñez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 21, 'jugador': 'Pedro', 'minutos': 4, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 6, 'jugador': 'Dennis', 'minutos': 15, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 7, 'jugador': 'Ian', 'minutos': 38, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 16, 'jugador': 'Hamza', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}])
_pt_eventos = pd.DataFrame([{'jornada': 1, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 27, 'tipo': 'gol_contra', 'jugador': "Ath. Massamagrell C.F. 'A'", 'detalle': 'Gol encajado'}, {'jornada': 2, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 49, 'tipo': 'amarilla', 'jugador': 'Toni', 'detalle': None}, {'jornada': 2, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 62, 'tipo': 'gol', 'jugador': 'Sebas', 'detalle': None}, {'jornada': 2, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 72, 'tipo': 'amarilla', 'jugador': 'Irakli', 'detalle': None}, {'jornada': 2, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 87, 'tipo': 'gol', 'jugador': 'Núñez', 'detalle': None}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 11, 'tipo': 'gol', 'jugador': 'Sebas', 'detalle': None}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 19, 'tipo': 'gol_contra', 'jugador': "Manises C.F. 'A'", 'detalle': 'Gol encajado'}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 20, 'tipo': 'amarilla', 'jugador': 'Ian', 'detalle': None}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 42, 'tipo': 'gol', 'jugador': 'Núñez', 'detalle': None}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 45, 'tipo': 'amarilla', 'jugador': 'Núñez', 'detalle': None}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 48, 'tipo': 'amarilla', 'jugador': 'Irakli', 'detalle': None}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 56, 'tipo': 'roja', 'jugador': 'Toni', 'detalle': 'Roja directa'}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 82, 'tipo': 'amarilla', 'jugador': 'Bilal', 'detalle': None}, {'jornada': 3, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 86, 'tipo': 'doble_amarilla', 'jugador': 'Bilal', 'detalle': 'segunda amarilla / expulsión'}, {'jornada': 4, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 69, 'tipo': 'gol_contra', 'jugador': "C.D.F. Canet 'A'", 'detalle': 'Gol encajado'}, {'jornada': 4, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 77, 'tipo': 'amarilla', 'jugador': 'Blázquez', 'detalle': None}, {'jornada': 4, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 83, 'tipo': 'roja', 'jugador': 'Blázquez', 'detalle': 'Doble amarilla / segunda amarilla'}, {'jornada': 5, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 37, 'tipo': 'amarilla', 'jugador': 'Irakli', 'detalle': None}, {'jornada': 5, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 43, 'tipo': 'gol', 'jugador': 'Núñez', 'detalle': None}, {'jornada': 5, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 45, 'tipo': 'gol_contra', 'jugador': "Alboraya U.D. 'B'", 'detalle': 'Gol encajado'}, {'jornada': 5, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 50, 'tipo': 'gol_contra', 'jugador': "Alboraya U.D. 'B'", 'detalle': 'Gol encajado'}, {'jornada': 5, 'equipo': "Primer Toque C.F. 'A'", 'minuto': 79, 'tipo': 'amarilla', 'jugador': 'Alessio', 'detalle': None}])
_pt_alineaciones = pd.DataFrame([{'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 1, 'jugador': 'Alessio', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 2, 'jugador': 'Chelli', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 3, 'jugador': 'Irakli', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 4, 'jugador': 'Sánchez', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 14, 'jugador': 'Blázquez', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 21, 'jugador': 'Pedro', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 8, 'jugador': 'Toni', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 10, 'jugador': 'Bilal', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 30, 'jugador': 'Boyan', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 9, 'jugador': 'Sebas', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 1, 'dorsal': 24, 'jugador': 'Núñez', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 1, 'jugador': 'Alessio', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 2, 'jugador': 'Chelli', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 3, 'jugador': 'Irakli', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 5, 'jugador': 'Xavi', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 14, 'jugador': 'Blázquez', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 7, 'jugador': 'Ian', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 10, 'jugador': 'Bilal', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 19, 'jugador': 'Mois', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 21, 'jugador': 'Pedro', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 9, 'jugador': 'Sebas', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 2, 'dorsal': 24, 'jugador': 'Núñez', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 13, 'jugador': 'Jordi', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 2, 'jugador': 'Chelli', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 4, 'jugador': 'Sánchez', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 8, 'jugador': 'Toni', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 14, 'jugador': 'Blázquez', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 7, 'jugador': 'Ian', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 10, 'jugador': 'Bilal', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 16, 'jugador': 'Hamza', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 21, 'jugador': 'Pedro', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 9, 'jugador': 'Sebas', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 3, 'dorsal': 24, 'jugador': 'Núñez', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 13, 'jugador': 'Jordi', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 2, 'jugador': 'Chelli', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 3, 'jugador': 'Irakli', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 4, 'jugador': 'Sánchez', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 5, 'jugador': 'Xavi', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 14, 'jugador': 'Blázquez', 'rol': 'DEF', 'linea': 2, 'orden': 5}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 7, 'jugador': 'Ian', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 16, 'jugador': 'Hamza', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 21, 'jugador': 'Pedro', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 24, 'jugador': 'Núñez', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 4, 'dorsal': 19, 'jugador': 'Mois', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 1, 'jugador': 'Alessio', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 3, 'jugador': 'Irakli', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 4, 'jugador': 'Sánchez', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 5, 'jugador': 'Xavi', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 28, 'jugador': 'Pau', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 8, 'jugador': 'Toni', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 9, 'jugador': 'Sebas', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 10, 'jugador': 'Bilal', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 17, 'jugador': 'Abde', 'rol': 'MED', 'linea': 3, 'orden': 4}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 19, 'jugador': 'Mois', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "Primer Toque C.F. 'A'", 'jornada': 5, 'dorsal': 24, 'jugador': 'Núñez', 'rol': 'ATA', 'linea': 4, 'orden': 2}])
_pt_plantilla = pd.DataFrame([{'equipo': "Primer Toque C.F. 'A'", 'dorsal': 1, 'jugador': 'Alessio'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 2, 'jugador': 'Chelli'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 3, 'jugador': 'Irakli'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 4, 'jugador': 'Sánchez'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 5, 'jugador': 'Xavi'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 6, 'jugador': 'Dennis'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 7, 'jugador': 'Ian'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 8, 'jugador': 'Toni'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 9, 'jugador': 'Sebas'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 10, 'jugador': 'Bilal'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 13, 'jugador': 'Jordi'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 14, 'jugador': 'Blázquez'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 17, 'jugador': 'Abde'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 19, 'jugador': 'Mois'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 21, 'jugador': 'Pedro'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 24, 'jugador': 'Núñez'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 28, 'jugador': 'Pau'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 30, 'jugador': 'Boyan'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 11, 'jugador': 'Fran'}, {'equipo': "Primer Toque C.F. 'A'", 'dorsal': 16, 'jugador': 'Hamza'}])
if not partidos.empty:
    partidos = partidos[~((partidos['local'] == _PT_TEAM) | (partidos['visitante'] == _PT_TEAM))].copy()
partidos = pd.concat([partidos, _pt_partidos], ignore_index=True)
if not minutos.empty:
    minutos = minutos[minutos['equipo'] != _PT_TEAM].copy()
minutos = pd.concat([minutos, _pt_minutos], ignore_index=True)
if not eventos.empty:
    eventos = eventos[eventos['equipo'] != _PT_TEAM].copy()
eventos = pd.concat([eventos, _pt_eventos], ignore_index=True)
if not alineaciones.empty:
    alineaciones = alineaciones[alineaciones['equipo'] != _PT_TEAM].copy()
alineaciones = pd.concat([alineaciones, _pt_alineaciones], ignore_index=True)
if not plantillas.empty:
    plantillas = plantillas[plantillas['equipo'] != _PT_TEAM].copy()
plantillas = pd.concat([plantillas, _pt_plantilla], ignore_index=True)

# --- Fallback robusto Salesianos J1-J5 ---
# Igual que Primer Toque: garantiza que Total/Casa/Fuera, minutos, XI, goles y disciplina
# se carguen aunque Streamlit conserve una versión antigua de alguno de los CSV.
_SAL_TEAM = "C.F. At. Burriana - Salesianos 'A'"
_sal_partidos = pd.DataFrame([{'jornada': 1, 'fecha': '06/09/2026', 'local': "Paterna C.F. 'A'", 'visitante': "C.F. At. Burriana - Salesianos 'A'", 'goles_local': 3.0, 'goles_visitante': 0.0, 'campo': 'Estadio Gerardo Salvador F-11 Paterna', 'sistema_local': '1-3-5-2', 'sistema_visitante': '1-4-3-3', 'estado': 'validado'}, {'jornada': 2, 'fecha': '13/09/2026', 'local': "C.F. At. Burriana - Salesianos 'A'", 'visitante': "Patacona C.F. 'B'", 'goles_local': 3.0, 'goles_visitante': 1.0, 'campo': 'Campo Mpal. Joan Manuel Canós Ferrer Burriana F-11', 'sistema_local': '1-4-3-3', 'sistema_visitante': '1-5-4-1', 'estado': 'validado'}, {'jornada': 3, 'fecha': '19/09/2026', 'local': "C.F. Inter San José Valencia 'B'", 'visitante': "C.F. At. Burriana - Salesianos 'A'", 'goles_local': 4.0, 'goles_visitante': 3.0, 'campo': 'Campo de Fútbol Mpal. de Beniferri F-11', 'sistema_local': '1-4-4-2', 'sistema_visitante': '1-4-3-3', 'estado': 'validado'}, {'jornada': 4, 'fecha': '27/09/2026', 'local': "C.F. At. Burriana - Salesianos 'A'", 'visitante': "C.F. Cracks 'A'", 'goles_local': 2.0, 'goles_visitante': 0.0, 'campo': 'Campo Mpal. Joan Manuel Canós Ferrer Burriana F-11', 'sistema_local': '1-4-3-3', 'sistema_visitante': '1-4-4-2', 'estado': 'validado'}, {'jornada': 5, 'fecha': '04/10/2026', 'local': "C.F. Torre Levante 'A'", 'visitante': "C.F. At. Burriana - Salesianos 'A'", 'goles_local': 0.0, 'goles_visitante': 0.0, 'campo': 'Campo Torre Levante-Orriols F-11', 'sistema_local': '1-5-4-1', 'sistema_visitante': '1-4-3-3', 'estado': 'validado'}])
_sal_minutos = pd.DataFrame([{'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 1, 'jugador': 'Wladislaw Zbrozhek', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 2, 'jugador': 'David Gil Ibañez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 8, 'jugador': 'Victor Mesado Vicente', 'minutos': 64, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 11, 'jugador': 'Guillem Gimenez Llopis', 'minutos': 57, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'minutos': 64, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'minutos': 70, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 12, 'jugador': 'Matias Erros Budassi Sellart', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 19, 'jugador': 'Marcos Espada Sanchez', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot', 'minutos': 26, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 16, 'jugador': 'Miguel Galera Sanz', 'minutos': 26, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 17, 'jugador': 'Alvaro Fuentes Segura', 'minutos': 20, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 21, 'jugador': 'Alvaro Vila Diaz', 'minutos': 33, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 13, 'jugador': 'Marc Roca Gari', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 4, 'jugador': 'Albert Viñes Cerezo', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 17, 'jugador': 'Alvaro Fuentes Segura', 'minutos': 69, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 2, 'jugador': 'David Gil Ibañez', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot', 'minutos': 69, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 23, 'jugador': 'Matias Erros Budassi Sellart', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'minutos': 69, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'minutos': 77, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 19, 'jugador': 'Marcos Espada Sanchez', 'minutos': 57, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 14, 'jugador': 'Jordi Gonzalez Lopez', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 21, 'jugador': 'Alvaro Vila Diaz', 'minutos': 21, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 8, 'jugador': 'Victor Mesado Vicente', 'minutos': 21, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'minutos': 21, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 7, 'jugador': 'David Rubert Morano', 'minutos': 33, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester', 'minutos': 13, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 13, 'jugador': 'Marc Roca Gari', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 14, 'jugador': 'Jordi Gonzalez Lopez', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 17, 'jugador': 'Alvaro Fuentes Segura', 'minutos': 72, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 2, 'jugador': 'David Gil Ibañez', 'minutos': 18, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester', 'minutos': 61, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 23, 'jugador': 'Matias Erros Budassi Sellart', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 7, 'jugador': 'David Rubert Morano', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'minutos': 61, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'minutos': 72, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 11, 'jugador': 'Guillem Gimenez Llopis', 'minutos': 29, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot', 'minutos': 29, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 16, 'jugador': 'Miguel Galera Sanz', 'minutos': 18, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 1, 'jugador': 'Wladislaw Zbrozhek', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 23, 'jugador': 'Matias Erros Budassi Sellart', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 4, 'jugador': 'Albert Viñes Cerezo', 'minutos': 78, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 7, 'jugador': 'David Rubert Morano', 'minutos': 78, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert', 'minutos': 88, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 16, 'jugador': 'Miguel Galera Sanz', 'minutos': 68, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'minutos': 46, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 20, 'jugador': 'Alexandru Constantin Epuraru', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 21, 'jugador': 'Alvaro Vila Diaz', 'minutos': 44, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'minutos': 22, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot', 'minutos': 12, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 19, 'jugador': 'Marcos Espada Sanchez', 'minutos': 12, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 14, 'jugador': 'Jordi Gonzalez Lopez', 'minutos': 2, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 1, 'jugador': 'Wladislaw Zbrozhek', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 20, 'jugador': 'Alexandru Constantin Epuraru', 'minutos': 75, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 21, 'jugador': 'Alvaro Vila Diaz', 'minutos': 62, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 4, 'jugador': 'Albert Viñes Cerezo', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot', 'minutos': 62, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'minutos': 90, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 16, 'jugador': 'Miguel Galera Sanz', 'minutos': 75, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 19, 'jugador': 'Marcos Espada Sanchez', 'minutos': 62, 'titular': 1, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 8, 'jugador': 'Victor Mesado Vicente', 'minutos': 15, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'minutos': 15, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 11, 'jugador': 'Guillem Gimenez Llopis', 'minutos': 28, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 12, 'jugador': 'Matias Erros Budassi Sellart', 'minutos': 28, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'minutos': 28, 'titular': 0, 'fuente': 'FFCV validado desde vídeo'}])
_sal_eventos = pd.DataFrame([{'jornada': 1, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 29, 'tipo': 'gol_contra', 'jugador': "Paterna C.F. 'A'", 'detalle': 'Gol encajado'}, {'jornada': 1, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 45, 'tipo': 'gol_contra', 'jugador': "Paterna C.F. 'A'", 'detalle': 'Gol encajado'}, {'jornada': 1, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 71, 'tipo': 'gol_contra', 'jugador': "Paterna C.F. 'A'", 'detalle': 'Gol encajado'}, {'jornada': 1, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 43, 'tipo': 'amarilla', 'jugador': 'Jorge Agustina Llopis', 'detalle': None}, {'jornada': 1, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 67, 'tipo': 'amarilla', 'jugador': 'Marcos Espada Sanchez', 'detalle': None}, {'jornada': 1, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 67, 'tipo': 'amarilla', 'jugador': 'Eduardo Aurelian Ciutacu', 'detalle': None}, {'jornada': 2, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 53, 'tipo': 'gol', 'jugador': 'Marcos Espada Sanchez', 'detalle': None}, {'jornada': 2, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 61, 'tipo': 'gol_contra', 'jugador': "Patacona C.F. 'B'", 'detalle': 'Gol encajado'}, {'jornada': 2, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 66, 'tipo': 'gol', 'jugador': 'David Rubert Morano', 'detalle': None}, {'jornada': 2, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 81, 'tipo': 'gol', 'jugador': 'David Rubert Morano', 'detalle': None}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 13, 'tipo': 'gol', 'jugador': 'Matias Erros Budassi Sellart', 'detalle': None}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 17, 'tipo': 'gol_contra', 'jugador': "C.F. Inter San José Valencia 'B'", 'detalle': 'Gol encajado'}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 39, 'tipo': 'gol', 'jugador': 'Matteo Morra Climent', 'detalle': None}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 45, 'tipo': 'gol_contra', 'jugador': "C.F. Inter San José Valencia 'B'", 'detalle': 'Gol encajado'}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 54, 'tipo': 'gol_contra', 'jugador': "C.F. Inter San José Valencia 'B'", 'detalle': 'Gol encajado'}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 60, 'tipo': 'gol_contra', 'jugador': "C.F. Inter San José Valencia 'B'", 'detalle': 'Gol encajado'}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 72, 'tipo': 'amarilla', 'jugador': 'Eduardo Aurelian Ciutacu', 'detalle': None}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 74, 'tipo': 'amarilla', 'jugador': 'Jorge Agustina Llopis', 'detalle': None}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 80, 'tipo': 'amarilla', 'jugador': 'David Rubert Morano', 'detalle': None}, {'jornada': 3, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 90, 'tipo': 'gol', 'jugador': 'David Rubert Morano', 'detalle': None}, {'jornada': 4, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 15, 'tipo': 'gol', 'jugador': 'Matias Erros Budassi Sellart', 'detalle': None}, {'jornada': 4, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 69, 'tipo': 'gol', 'jugador': 'David Rubert Morano', 'detalle': None}, {'jornada': 5, 'equipo': "C.F. At. Burriana - Salesianos 'A'", 'minuto': 60, 'tipo': 'amarilla', 'jugador': 'Marcelo Albert Guinot', 'detalle': None}])
_sal_alineaciones = pd.DataFrame([{'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 1, 'jugador': 'Wladislaw Zbrozhek', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 2, 'jugador': 'David Gil Ibañez', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 8, 'jugador': 'Victor Mesado Vicente', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 11, 'jugador': 'Guillem Gimenez Llopis', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 1, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'rol': 'ATA', 'linea': 4, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 13, 'jugador': 'Marc Roca Gari', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 4, 'jugador': 'Albert Viñes Cerezo', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 17, 'jugador': 'Alvaro Fuentes Segura', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 2, 'jugador': 'David Gil Ibañez', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 23, 'jugador': 'Matias Erros Budassi Sellart', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 2, 'dorsal': 19, 'jugador': 'Marcos Espada Sanchez', 'rol': 'ATA', 'linea': 4, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 13, 'jugador': 'Marc Roca Gari', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 14, 'jugador': 'Jordi Gonzalez Lopez', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 17, 'jugador': 'Alvaro Fuentes Segura', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 2, 'jugador': 'David Gil Ibañez', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 23, 'jugador': 'Matias Erros Budassi Sellart', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 7, 'jugador': 'David Rubert Morano', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 9, 'jugador': 'Mario Casino Esteve', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 3, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'rol': 'ATA', 'linea': 4, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 1, 'jugador': 'Wladislaw Zbrozhek', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 23, 'jugador': 'Matias Erros Budassi Sellart', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 4, 'jugador': 'Albert Viñes Cerezo', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 7, 'jugador': 'David Rubert Morano', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 16, 'jugador': 'Miguel Galera Sanz', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 4, 'dorsal': 22, 'jugador': 'Matteo Morra Climent', 'rol': 'ATA', 'linea': 4, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 1, 'jugador': 'Wladislaw Zbrozhek', 'rol': 'POR', 'linea': 1, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert', 'rol': 'DEF', 'linea': 2, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat', 'rol': 'DEF', 'linea': 2, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 20, 'jugador': 'Alexandru Constantin Epuraru', 'rol': 'DEF', 'linea': 2, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 21, 'jugador': 'Alvaro Vila Diaz', 'rol': 'DEF', 'linea': 2, 'orden': 4}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 4, 'jugador': 'Albert Viñes Cerezo', 'rol': 'MED', 'linea': 3, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot', 'rol': 'MED', 'linea': 3, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu', 'rol': 'MED', 'linea': 3, 'orden': 3}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis', 'rol': 'ATA', 'linea': 4, 'orden': 1}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 16, 'jugador': 'Miguel Galera Sanz', 'rol': 'ATA', 'linea': 4, 'orden': 2}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'jornada': 5, 'dorsal': 19, 'jugador': 'Marcos Espada Sanchez', 'rol': 'ATA', 'linea': 4, 'orden': 3}])
_sal_plantilla = pd.DataFrame([{'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 1, 'jugador': 'Wladislaw Zbrozhek'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 2, 'jugador': 'David Gil Ibañez'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 3, 'jugador': 'Pablo Cabrera Gilabert'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 4, 'jugador': 'Albert Viñes Cerezo'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 5, 'jugador': 'Marcelo Albert Guinot'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 6, 'jugador': 'Alexandre Alemany Torrat'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 7, 'jugador': 'David Rubert Morano'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 8, 'jugador': 'Victor Mesado Vicente'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 9, 'jugador': 'Mario Casino Esteve'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 10, 'jugador': 'Jorge Agustina Llopis'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 11, 'jugador': 'Guillem Gimenez Llopis'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 12, 'jugador': 'Matias Erros Budassi Sellart'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 13, 'jugador': 'Marc Roca Gari'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 14, 'jugador': 'Jordi Gonzalez Lopez'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 15, 'jugador': 'Eduardo Aurelian Ciutacu'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 16, 'jugador': 'Miguel Galera Sanz'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 17, 'jugador': 'Alvaro Fuentes Segura'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 18, 'jugador': 'Dani Hernandez Ballester'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 19, 'jugador': 'Marcos Espada Sanchez'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 20, 'jugador': 'Alexandru Constantin Epuraru'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 21, 'jugador': 'Alvaro Vila Diaz'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 22, 'jugador': 'Matteo Morra Climent'}, {'equipo': "C.F. At. Burriana - Salesianos 'A'", 'dorsal': 23, 'jugador': 'Matias Erros Budassi Sellart'}])
if not partidos.empty:
    partidos = partidos[~((partidos['local'] == _SAL_TEAM) | (partidos['visitante'] == _SAL_TEAM))].copy()
partidos = pd.concat([partidos, _sal_partidos], ignore_index=True)
if not minutos.empty:
    minutos = minutos[minutos['equipo'] != _SAL_TEAM].copy()
minutos = pd.concat([minutos, _sal_minutos], ignore_index=True)
if not eventos.empty:
    eventos = eventos[eventos['equipo'] != _SAL_TEAM].copy()
eventos = pd.concat([eventos, _sal_eventos], ignore_index=True)
if not alineaciones.empty:
    alineaciones = alineaciones[alineaciones['equipo'] != _SAL_TEAM].copy()
alineaciones = pd.concat([alineaciones, _sal_alineaciones], ignore_index=True)
if not plantillas.empty:
    plantillas = plantillas[plantillas['equipo'] != _SAL_TEAM].copy()
plantillas = pd.concat([plantillas, _sal_plantilla], ignore_index=True)


NAVY = "#062d5a"
BLUE = "#1d63d8"
ORANGE = "#f59e0b"
BG = "#f5f7fb"
TEXT = "#102a43"
MUTED = "#6b7c93"
RED = "#ef4444"
DGREEN = "#16a34a"

st.markdown(
    f"""
<style>
html, body, [class*="css"] {{font-family: Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}}
[data-testid="stAppViewContainer"] {{background:{BG};color:{TEXT};}}
[data-testid="stHeader"] {{background:transparent;}}
.block-container {{padding-top:.7rem;max-width:1540px;padding-bottom:3rem;}}
[data-testid="stSidebar"] {{background:#fff;border-right:1px solid #e6eaf0;}}
[data-testid="stSidebar"] .block-container {{padding-top:1rem;}}

.brand-box {{display:flex;align-items:center;gap:11px;background:{NAVY};color:white;border-radius:14px;padding:13px 14px;margin-bottom:14px;box-shadow:0 8px 24px rgba(6,45,90,.18)}}
.brand-ball {{width:38px;height:38px;border-radius:12px;background:{ORANGE};display:flex;align-items:center;justify-content:center;font-size:21px}}
.brand-main {{font-weight:900;line-height:1;font-size:1.05rem}} .brand-main span {{color:#ffd166}}
.brand-sub {{font-size:.73rem;opacity:.75;margin-top:4px}}
.side-label {{font-size:.76rem;font-weight:900;color:#6b7c93;text-transform:uppercase;letter-spacing:.04em;margin:.55rem 0 .2rem}}
.team-count {{font-size:.75rem;color:#7c8ea4;margin-top:.25rem}}

.topbar {{background:{NAVY};color:white;border-radius:15px;padding:15px 20px;margin-bottom:13px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 8px 20px rgba(6,45,90,.14)}}
.topbar .title {{font-size:1.05rem;font-weight:800}} .topbar .nav {{opacity:.82;font-size:.88rem}}
.team-head {{background:#fff;border:1px solid #e6eaf0;border-radius:16px;padding:18px 20px;display:flex;align-items:center;gap:18px;box-shadow:0 6px 20px rgba(16,42,67,.05)}}
.team-head img {{width:82px;height:82px;object-fit:contain;border-radius:12px}}
.team-name {{font-size:2rem;font-weight:900;color:{NAVY};line-height:1.05}}
.team-sub {{color:#406080;font-size:.96rem;margin-top:5px}}
.badge {{display:inline-block;background:#eef4ff;color:{BLUE};font-weight:800;border-radius:999px;padding:5px 10px;font-size:.78rem;margin-top:8px}}

.section-title {{font-size:1.08rem;font-weight:900;color:{NAVY};margin:.2rem 0 .65rem}}
.card {{background:#fff;border:1px solid #e6eaf0;border-radius:15px;padding:16px;box-shadow:0 5px 16px rgba(16,42,67,.045);height:100%}}
.kpi {{text-align:center;min-height:112px;display:flex;flex-direction:column;justify-content:center}}
.kpi .v {{font-size:1.78rem;font-weight:900;color:{NAVY};line-height:1}} .kpi .l {{font-size:.79rem;color:{MUTED};margin-top:8px;font-weight:700}} .kpi .s {{font-size:.72rem;color:#8b9bb0;margin-top:4px}}

.form-row {{display:grid;grid-template-columns:90px 1fr 80px;gap:10px;align-items:center;margin:12px 0;font-size:.83rem;font-weight:800}}
.bar {{height:12px;background:#edf1f5;border-radius:999px;overflow:hidden}} .fill {{height:100%;background:linear-gradient(90deg,{BLUE},#57a4ff);border-radius:999px}}
.match-row {{display:grid;grid-template-columns:40px 1fr 70px 14px;gap:9px;align-items:center;padding:9px 0;border-bottom:1px solid #edf0f4;font-size:.82rem}} .match-row:last-child {{border-bottom:0}} .jtag {{font-weight:900;color:{NAVY}}}
.dot {{width:10px;height:10px;border-radius:50%}}

.pitch {{position:relative;width:100%;aspect-ratio:1.42/1;background:linear-gradient(90deg,#21823d,#2d9849);border-radius:12px;overflow:hidden;border:3px solid #fff;box-shadow:inset 0 0 0 2px rgba(255,255,255,.7)}}
.pitch:before {{content:'';position:absolute;left:50%;top:0;bottom:0;border-left:2px solid rgba(255,255,255,.75)}}
.pitch:after {{content:'';position:absolute;width:18%;aspect-ratio:1;left:41%;top:40%;border:2px solid rgba(255,255,255,.75);border-radius:50%}}
.box-l,.box-r {{position:absolute;top:23%;height:54%;width:17%;border:2px solid rgba(255,255,255,.75)}} .box-l {{left:0;border-left:0}} .box-r {{right:0;border-right:0}}
.pchip {{position:absolute;transform:translate(-50%,-50%);text-align:center;color:white;font-size:.68rem;font-weight:800;text-shadow:0 1px 2px rgba(0,0,0,.35);min-width:58px}}
.shirt {{width:35px;height:31px;background:#fff;border:2px solid {NAVY};border-radius:8px 8px 5px 5px;color:{NAVY};display:flex;align-items:center;justify-content:center;margin:0 auto 3px;font-size:.83rem;font-weight:900;box-shadow:0 2px 5px rgba(0,0,0,.2)}}
.ppct {{font-size:.58rem;background:rgba(0,0,0,.28);border-radius:999px;padding:1px 5px;display:inline-block;margin-top:2px}}

.heat-wrap {{background:#fff;border:1px solid #e6eaf0;border-radius:15px;padding:13px;overflow:auto;box-shadow:0 5px 16px rgba(16,42,67,.045)}}
table.heat {{width:100%;border-collapse:separate;border-spacing:0;font-size:.77rem;min-width:980px}} table.heat th {{position:sticky;top:0;background:#f7f9fc;color:#4d6078;padding:8px 7px;border-bottom:1px solid #e7ebf0;text-align:center}} table.heat td {{padding:7px;border-bottom:1px solid #eef1f4;text-align:center}} table.heat td.name {{text-align:left;font-weight:700;color:{NAVY}}} table.heat td.num {{font-weight:900;color:{NAVY};width:34px}}
.m0 {{background:#fecaca}} .m1 {{background:#fdba74}} .m2 {{background:#fde68a}} .m3 {{background:#bbf7d0}} .m4 {{background:#4ade80;color:#073b1e;font-weight:900}} .mx {{background:#f1f5f9;color:#94a3b8}}
.mini-list {{display:flex;flex-direction:column;gap:9px}} .mini-item {{display:flex;justify-content:space-between;gap:10px;align-items:center;border-bottom:1px solid #eef1f4;padding-bottom:8px;font-size:.82rem}} .mini-item:last-child {{border:0}}
.note {{font-size:.78rem;color:{MUTED};margin-top:8px}}
.pending {{color:#94a3b8;font-weight:700}}
.video-callout {{background:#fff;border:1px solid #dbe6f1;border-left:6px solid #e11d48;border-radius:14px;padding:13px 15px;margin:10px 0 14px;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
.video-callout .vt {{font-size:.86rem;font-weight:900;color:{NAVY};margin-bottom:5px}}
.video-callout .vs {{font-size:.76rem;color:{MUTED};margin-bottom:8px}}
.video-link {{display:inline-block;text-decoration:none!important;background:{NAVY};color:#fff!important;font-weight:900;font-size:.78rem;padding:8px 12px;border-radius:10px}}
.match-links-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:8px}}
.match-link-card {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:14px;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
.match-link-card .mj {{font-size:.72rem;font-weight:900;color:#64748b;margin-bottom:4px}}
.match-link-card .mf {{font-size:.88rem;font-weight:900;color:{NAVY};margin-bottom:5px}}
.match-link-card .mr {{font-size:.78rem;color:{MUTED};margin-bottom:10px}}
.match-link-card a {{text-decoration:none!important;font-weight:900;color:#fff!important;background:{NAVY};border-radius:9px;padding:7px 10px;display:inline-block;font-size:.76rem}}
.match-link-card .no-link {{font-size:.76rem;color:#94a3b8;font-weight:800}}
.goal-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(115px,1fr));gap:12px;align-items:stretch}}
.goal-bin {{background:#fff;border:1px solid #e6eaf0;border-radius:15px;padding:14px 8px;text-align:center;min-height:148px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;box-shadow:0 5px 16px rgba(16,42,67,.045)}}
.goal-range {{font-size:.78rem;font-weight:900;color:{NAVY};margin-bottom:10px}}
.goal-bubble-wrap {{height:86px;display:flex;align-items:center;justify-content:center}}
.goal-bubble {{border-radius:50%;background:rgba(22,163,74,.88);color:white;display:flex;align-items:center;justify-content:center;font-weight:900;box-shadow:0 5px 14px rgba(22,163,74,.22)}}
.goal-bubble.against {{background:rgba(239,68,68,.9);box-shadow:0 5px 14px rgba(239,68,68,.2)}}
.goal-bubble.zero {{background:#e8edf3;color:#8292a8;box-shadow:none}}
.goal-pair {{height:88px;display:flex;align-items:center;justify-content:center;gap:10px}}
.goal-legend {{display:flex;gap:16px;align-items:center;font-size:.76rem;color:#6b7c93;margin:-2px 0 10px}}
.legend-dot {{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:5px}}
.goal-count {{font-size:.7rem;color:{MUTED};margin-top:7px;font-weight:700}}
.goal-pctbox {{width:100%;margin-top:9px;background:#f7f9fc;border-radius:10px;padding:8px 8px 6px;box-sizing:border-box}}
.goal-pctrow {{display:grid;grid-template-columns:34px 1fr 70px;gap:6px;align-items:center;margin:5px 0;font-size:.66rem;font-weight:800;color:{NAVY}}}
.goal-pcttrack {{height:8px;background:#e9eef4;border-radius:999px;overflow:hidden}}
.goal-pctfill-gf {{height:100%;background:#16a34a;border-radius:999px}}
.goal-pctfill-gc {{height:100%;background:#ef4444;border-radius:999px}}
.goal-macro-grid {{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:6px 0 14px}}
.goal-macro {{border:1px solid #e4eaf1;border-radius:15px;padding:13px 14px;min-height:118px;box-shadow:0 5px 16px rgba(16,42,67,.045);background:#fff}}
.goal-macro .t {{font-size:.74rem;font-weight:900;color:{NAVY};margin-bottom:4px}}
.goal-macro .big {{font-size:1.52rem;font-weight:950;line-height:1;color:{NAVY};margin:4px 0}}
.goal-macro .sub {{font-size:.69rem;color:{MUTED};line-height:1.35}}
.goal-macro.blue {{background:#eef7ff}} .goal-macro.green {{background:#f0fbf1}} .goal-macro.red {{background:#fff1f1}} .goal-macro.purple {{background:#f5f1ff}} .goal-macro.pink {{background:#fff0f5}}
.goal-activity {{display:flex;align-items:center;justify-content:center;margin:2px 0 7px}}
.goal-ring {{width:58px;height:58px;border-radius:50%;display:grid;place-items:center}}
.goal-ring-inner {{width:42px;height:42px;border-radius:50%;background:#fff;display:grid;place-items:center;font-weight:950;font-size:.82rem;color:{NAVY}}}
.goal-detail-wrap {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:10px 12px;margin-top:12px;box-shadow:0 5px 16px rgba(16,42,67,.04);overflow:auto}}
.goal-detail-title {{font-size:.83rem;font-weight:900;color:{NAVY};margin:0 0 8px}}
table.goal-detail {{width:100%;border-collapse:collapse;font-size:.72rem;min-width:760px}}
table.goal-detail th {{background:#f7f9fc;color:{NAVY};font-weight:900;padding:7px;border:1px solid #e6ebf1;text-align:center}}
table.goal-detail td {{padding:7px;border:1px solid #e6ebf1;text-align:center}} table.goal-detail td:first-child {{text-align:left;font-weight:800;color:{NAVY};background:#fbfcfe}}
.diff-pos {{background:#ecfdf3!important;color:#15803d;font-weight:900}} .diff-neg {{background:#fff1f2!important;color:#dc2626;font-weight:900}} .diff-zero {{background:#f8fafc!important;color:#64748b;font-weight:900}}
@media (max-width: 1050px) {{.goal-macro-grid {{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
[data-testid="stMetric"] {{background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:10px 13px;box-shadow:0 5px 16px rgba(16,42,67,.04)}}
</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
<style>
.ind-hero{background:linear-gradient(135deg,#052b56 0%,#0b4079 100%);color:#fff;border-radius:18px;padding:18px 20px;box-shadow:0 10px 28px rgba(6,45,90,.18);min-height:210px}
.ind-hero .shirt-no{font-size:3rem;font-weight:950;line-height:.95}.ind-hero .pname{font-size:1.65rem;font-weight:950;line-height:1.05;margin-top:8px}.ind-hero .pos{display:inline-block;background:#1d63d8;padding:5px 10px;border-radius:999px;font-size:.76rem;font-weight:900;margin-top:10px}.ind-hero .meta{font-size:.8rem;opacity:.82;margin-top:12px;line-height:1.7}
.ind-panel{background:#fff;border:1px solid #e6eaf0;border-radius:16px;padding:15px;box-shadow:0 5px 16px rgba(16,42,67,.045);height:100%}.ind-title{font-size:.92rem;font-weight:950;color:#062d5a;margin-bottom:10px}.ind-sub{font-size:.72rem;color:#6b7c93}
.ind-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.ind-mini{background:#f7f9fc;border:1px solid #edf1f5;border-radius:12px;padding:11px 8px;text-align:center}.ind-mini .v{font-size:1.28rem;font-weight:950;color:#062d5a}.ind-mini .l{font-size:.67rem;color:#6b7c93;font-weight:800;margin-top:3px}.ind-mini.warn .v{color:#d97706}.ind-mini.red .v{color:#dc2626}.ind-mini.green .v{color:#16a34a}
.ind-stat{display:grid;grid-template-columns:1fr auto;gap:10px;padding:7px 0;border-bottom:1px solid #edf1f5;font-size:.78rem}.ind-stat:last-child{border-bottom:0}.ind-stat b{color:#062d5a}.ind-stat .muted{color:#94a3b8}
.pos-tabs{display:flex;gap:7px;flex-wrap:wrap;margin:4px 0 12px}.pos-pill{border:1px solid #dce5ef;background:#fff;color:#31506f;padding:7px 11px;border-radius:999px;font-size:.75rem;font-weight:900}.pos-pill.active{background:#eaf2ff;color:#1d63d8;border-color:#b7cff7}
.player-strip{display:flex;gap:8px;overflow:auto;padding-bottom:6px}.player-chip{min-width:110px;background:#fff;border:1px solid #e5eaf0;border-radius:12px;padding:8px 10px}.player-chip .n{font-weight:950;color:#062d5a;font-size:.8rem}.player-chip .r{font-size:.65rem;color:#7b8da4}.player-chip.active{border:2px solid #1d63d8;background:#f2f7ff}
.ind-bar-row{display:grid;grid-template-columns:1fr 80px;gap:10px;align-items:center;margin:9px 0;font-size:.77rem}.ind-bar-bg{height:8px;background:#edf2f7;border-radius:999px;overflow:hidden}.ind-bar-fill{height:100%;background:linear-gradient(90deg,#1d63d8,#5aa2ff);border-radius:999px}.ind-rank{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.rank-card{background:#f7f9fc;border:1px solid #edf1f5;border-radius:12px;padding:11px;text-align:center}.rank-card .place{font-size:1.25rem;font-weight:950;color:#1d63d8}.rank-card .desc{font-size:.67rem;color:#66788e;line-height:1.3;margin-top:3px}
.timeline{position:relative;height:48px;margin:10px 2px 3px}.timeline:before{content:'';position:absolute;left:0;right:0;top:18px;height:8px;border-radius:999px;background:#dbeafe}.timeline .played{position:absolute;left:0;top:18px;height:8px;border-radius:999px;background:#60a5fa}.timeline .ev{position:absolute;top:9px;transform:translateX(-50%);font-size:15px}.timeline-labels{display:flex;justify-content:space-between;font-size:.62rem;color:#8494a8}
.video-badge{display:inline-block;background:#fef3c7;color:#92400e;border:1px solid #fde68a;padding:5px 8px;border-radius:999px;font-size:.67rem;font-weight:900}.verified-badge{display:inline-block;background:#ecfdf3;color:#166534;border:1px solid #bbf7d0;padding:5px 8px;border-radius:999px;font-size:.67rem;font-weight:900}
@media(max-width:900px){.ind-kpis,.ind-rank{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
""",
    unsafe_allow_html=True,
)


def render_individual():
    team = "Primer Toque C.F. 'A'"
    pt_min = minutos[minutos.equipo == team].copy()
    pt_ev = eventos[eventos.equipo == team].copy()
    pt_al = alineaciones[alineaciones.equipo == team].copy()
    pt_roster = plantillas[plantillas.equipo == team].copy()

    # Datos avanzados: solo partidos de casa. La arquitectura queda lista para J2/J3/J5.
    adv_frames = []
    for j in (2, 3, 5):
        p = DATA / f"individual_video_j{j}.csv"
        if p.exists():
            d = pd.read_csv(p)
            if "jornada" not in d.columns:
                d["jornada"] = j
            adv_frames.append(d)
    adv_all = pd.concat(adv_frames, ignore_index=True) if adv_frames else pd.DataFrame()
    advanced_available = sorted(adv_all.jornada.dropna().astype(int).unique().tolist()) if not adv_all.empty else []

    # Posición principal a partir de las alineaciones reales.
    role_map = {}
    if not pt_al.empty:
        for p, grp in pt_al.groupby("jugador"):
            vals = grp["rol"].dropna().astype(str)
            if not vals.empty:
                role_map[p] = vals.mode().iloc[0]
    role_name = {"POR":"Portero", "DEF":"Defensa", "MED":"Mediocentro", "ATA":"Delantero"}
    role_group = {"POR":"Porteros", "DEF":"Defensas", "MED":"Mediocentros", "ATA":"Delanteros"}

    roster = pt_roster.copy()
    if roster.empty:
        roster = pt_min[["dorsal","jugador"]].drop_duplicates()
    roster["rol"] = roster["jugador"].map(role_map).fillna("MED")
    roster["grupo"] = roster["rol"].map(role_group).fillna("Mediocentros")
    roster = roster.sort_values(["rol","dorsal","jugador"]).reset_index(drop=True)

    st.markdown("""
    <style>
    .ind-v2-head{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;margin:2px 0 12px}.ind-v2-title{font-size:2rem;font-weight:950;color:#062d5a;letter-spacing:-.04em}.ind-v2-sub{font-size:.8rem;color:#6b7c93;margin-top:2px}.data-note{display:inline-flex;align-items:center;gap:6px;background:#eef6ff;color:#195ea8;border:1px solid #d6e8fb;padding:6px 10px;border-radius:999px;font-size:.68rem;font-weight:900}
    .global-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px;margin:8px 0 12px}.global-card{background:#fff;border:1px solid #e6ebf1;border-radius:15px;padding:13px 12px;box-shadow:0 5px 16px rgba(16,42,67,.04)}.global-card .big{font-size:1.55rem;font-weight:950;color:#062d5a}.global-card .small{font-size:.66rem;color:#718096;font-weight:800;margin-top:2px}.global-card .accent{font-size:.67rem;color:#1d63d8;font-weight:900;margin-top:6px}
    .rank-list{display:grid;gap:8px}.rank-row{display:grid;grid-template-columns:28px 1fr auto;gap:8px;align-items:center}.rank-num{width:26px;height:26px;border-radius:8px;background:#edf4ff;color:#1d63d8;display:grid;place-items:center;font-size:.72rem;font-weight:950}.rank-name{font-size:.75rem;font-weight:900;color:#17324d}.rank-value{font-size:.74rem;font-weight:950;color:#062d5a}.microbar{height:6px;background:#edf2f7;border-radius:999px;overflow:hidden;margin-top:4px}.microbar span{display:block;height:100%;background:linear-gradient(90deg,#1d63d8,#78b1ff);border-radius:999px}
    .minute-card{background:#fff;border:1px solid #e7ebf1;border-radius:13px;padding:10px 11px}.minute-card .top{display:flex;justify-content:space-between;gap:8px;font-size:.74rem;font-weight:900;color:#17324d}.minute-card .mins{font-size:.75rem;font-weight:950}.minbar{height:8px;background:#edf1f5;border-radius:99px;overflow:hidden;margin-top:7px}.minbar span{display:block;height:100%;border-radius:99px}.minutes-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
    .map-shell{background:#fff;border:1px solid #e5eaf0;border-radius:16px;padding:11px;box-shadow:0 5px 16px rgba(16,42,67,.04);overflow:hidden}.map-label{font-size:.82rem;font-weight:950;color:#062d5a;margin-bottom:7px}.map-img-wrap{width:100%;overflow:hidden;border-radius:12px;background:#fff}.map-img-wrap img{display:block;width:100%;height:auto;max-width:100%;object-fit:contain;object-position:center}.map-empty{min-height:215px;display:grid;place-items:center;text-align:center;background:linear-gradient(135deg,#f8fafc,#eef4f8);border:1px dashed #cfdae6;border-radius:12px;color:#8292a6;font-size:.75rem;padding:18px}
    .per90-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin-top:9px}.per90-card{background:linear-gradient(180deg,#fbfdff,#f4f8fc);border:1px solid #e0e8f1;border-radius:13px;padding:11px 10px}.per90-card .v{font-size:1.05rem;font-weight:950;color:#073866}.per90-card .l{font-size:.62rem;font-weight:900;color:#72849a;text-transform:uppercase;letter-spacing:.03em;margin-top:3px}.conversion-pill{display:inline-flex;align-items:center;gap:7px;background:#eaf8ef;color:#17733b;border:1px solid #cdebd7;padding:6px 9px;border-radius:999px;font-weight:950;font-size:.7rem}.video-day{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:13px;padding:11px;margin-top:9px}.video-day-title{font-size:.78rem;font-weight:950}.video-goal{font-size:.7rem;line-height:1.45;margin-top:7px;padding-top:7px;border-top:1px solid rgba(255,255,255,.14)}
    .source-card{background:linear-gradient(135deg,#061f3e,#0d4074);color:white;border-radius:16px;padding:15px}.source-card a{display:inline-block;text-decoration:none;background:white;color:#063565;padding:8px 11px;border-radius:10px;font-size:.72rem;font-weight:950;margin:5px 5px 0 0}.source-muted{font-size:.69rem;opacity:.78;line-height:1.5}
    .section-kicker{font-size:.7rem;color:#6f8095;font-weight:900;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px}.section-title{font-size:1.05rem;color:#062d5a;font-weight:950;margin-bottom:9px}
    [data-testid="stButton"] button{border-radius:12px!important;font-weight:850!important;border:1px solid #dfe7ef!important;min-height:42px}.player-label{font-size:.64rem;color:#77899e;text-align:center;margin-top:-8px;margin-bottom:7px}
    @media(max-width:1000px){.global-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.minutes-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    </style>
    """, unsafe_allow_html=True)

    def map_image_html(path_obj, alt_text):
        """Render a full-width image without Streamlit clipping/cropping."""
        if not path_obj.exists():
            return ""
        mime = "image/png" if path_obj.suffix.lower() == ".png" else "image/jpeg"
        b64 = base64.b64encode(path_obj.read_bytes()).decode()
        return f"<div class='map-img-wrap'><img src='data:{mime};base64,{b64}' alt='{html.escape(alt_text, quote=True)}'></div>"

    # Cabecera + jornada. No se usa "Periodo": solo jornadas con tracking de casa + Total.
    h1,h2 = st.columns([3.0,1.0])
    with h1:
        st.markdown("<div class='ind-v2-head'><div><div class='ind-v2-title'>Individual</div><div class='ind-v2-sub'>Rendimiento por jugador y posición · acta oficial + tracking de partidos de casa</div></div></div>", unsafe_allow_html=True)
    with h2:
        jornada_ui = st.selectbox("Jornada", ["J2","J3","Total"], index=0)
    if jornada_ui == "Total":
        js = [2,3]
        advanced_js = [j for j in js if j in advanced_available]
        view_label = "Total · partidos de casa"
    else:
        j = int(jornada_ui[1:])
        js = [j]
        advanced_js = [j] if j in advanced_available else []
        view_label = jornada_ui
    avail_txt = " + ".join(f"J{x}" for x in advanced_available) if advanced_available else "ninguna"
    st.markdown(f"<span class='data-note'>● Tracking avanzado disponible: {html.escape(avail_txt)} · Total solo suma jornadas cargadas</span>", unsafe_allow_html=True)

    if "ind_group" not in st.session_state:
        st.session_state.ind_group = "Todos"
    if "ind_selected_player" not in st.session_state:
        st.session_state.ind_selected_player = None

    # Posiciones como botones, no desplegable.
    st.markdown("<div style='height:8px'></div><div class='section-kicker'>Explorar plantilla</div>", unsafe_allow_html=True)
    groups = ["Todos","Porteros","Defensas","Mediocentros","Delanteros"]
    gcols = st.columns(5)
    for col,g in zip(gcols,groups):
        with col:
            icon = {"Todos":"◉","Porteros":"🧤","Defensas":"🛡️","Mediocentros":"⚙️","Delanteros":"⚡"}[g]
            if st.button(f"{icon} {g}", key=f"grp_{g}", use_container_width=True):
                st.session_state.ind_group = g
                st.session_state.ind_selected_player = None

    group = st.session_state.ind_group
    roster_view = roster if group == "Todos" else roster[roster.grupo == group]
    roster_view = roster_view.sort_values(["dorsal","jugador"]).reset_index(drop=True)

    # En "Todos" mostramos un dashboard-resumen limpio. Los jugadores aparecen solo al pulsar una posición.
    st.markdown(f"<div class='section-title'>{html.escape(group)}</div>", unsafe_allow_html=True)
    if group != "Todos":
        rows = [roster_view.iloc[i:i+5] for i in range(0,len(roster_view),5)]
        for chunk in rows:
            cols = st.columns(5)
            for idx,(_,r) in enumerate(chunk.iterrows()):
                with cols[idx]:
                    label = f"#{int(r.dorsal)} · {r.jugador}"
                    if st.button(label, key=f"pl_{int(r.dorsal)}_{r.jugador}", use_container_width=True):
                        st.session_state.ind_selected_player = str(r.jugador)
                    st.markdown(f"<div class='player-label'>{html.escape(role_name.get(r.rol,'Jugador'))}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='data-note'>Resumen global · elige una posición para abrir jugadores individuales ordenados por dorsal</div>", unsafe_allow_html=True)

    # ---------- VISTA TODOS / POSICIÓN ----------
    player = st.session_state.ind_selected_player
    if player is None:
        sub_roster = roster_view.copy()
        dorsals = sub_roster.dorsal.astype(int).tolist()
        official = pt_min[(pt_min.jornada.isin(js)) & (pt_min.jugador.isin(sub_roster.jugador))].copy()
        advv = adv_all[(adv_all.jornada.isin(advanced_js)) & (adv_all.dorsal.astype(int).isin(dorsals))].copy() if advanced_js and not adv_all.empty else pd.DataFrame()

        total_minutes = int(official.minutos.sum()) if not official.empty else 0
        players_used = int(official.loc[official.minutos>0,"jugador"].nunique()) if not official.empty else 0
        goals = int(pt_ev[(pt_ev.jornada.isin(js)) & (pt_ev.jugador.isin(sub_roster.jugador)) & (pt_ev.tipo.isin(["gol","penalti_gol"]))].shape[0])
        shots = int(pd.to_numeric(advv.get("tiros", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not advv.empty else 0
        distance = float(pd.to_numeric(advv.get("distancia_km", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not advv.empty else 0

        st.markdown(f"""
        <div class='global-grid'>
          <div class='global-card'><div class='big'>{players_used}</div><div class='small'>Jugadores utilizados</div><div class='accent'>{html.escape(view_label)}</div></div>
          <div class='global-card'><div class='big'>{total_minutes}</div><div class='small'>Minutos oficiales acumulados</div><div class='accent'>acta</div></div>
          <div class='global-card'><div class='big'>{goals}</div><div class='small'>Goles del grupo</div><div class='accent'>acta validada</div></div>
          <div class='global-card'><div class='big'>{shots if advanced_js else '—'}</div><div class='small'>Tiros detectados</div><div class='accent'>{'tracking' if advanced_js else 'pendiente de datos'}</div></div>
          <div class='global-card'><div class='big'>{str(round(distance,1)).replace('.',',') if advanced_js else '—'}{(' km' if advanced_js else '')}</div><div class='small'>Distancia rastreada</div><div class='accent'>{'tracking' if advanced_js else 'pendiente de datos'}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Rankings visuales.
        r1,r2,r3 = st.columns(3)
        def ranking_html(frame, col, label, suffix="", topn=5):
            if frame.empty or col not in frame.columns:
                return "<div class='ind-sub'>Sin datos avanzados todavía.</div>"
            t=frame.copy(); t[col]=pd.to_numeric(t[col],errors='coerce'); t=t.dropna(subset=[col])
            if t.empty: return "<div class='ind-sub'>Sin datos avanzados todavía.</div>"
            t=t.groupby('dorsal',as_index=False)[col].sum().sort_values(col,ascending=False).head(topn)
            mx=max(float(t[col].max()),1)
            rr=[]
            for pos,(_,x) in enumerate(t.iterrows(),1):
                d=int(x.dorsal); name=roster.loc[roster.dorsal.astype(int)==d,'jugador']
                nm=name.iloc[0] if not name.empty else f"#{d}"
                val=float(x[col]); vtxt=str(round(val,1)).replace('.',',') if not float(val).is_integer() else str(int(val))
                rr.append(f"<div class='rank-row'><div class='rank-num'>{pos}</div><div><div class='rank-name'>#{d} · {html.escape(str(nm))}</div><div class='microbar'><span style='width:{min(100,val/mx*100):.1f}%'></span></div></div><div class='rank-value'>{vtxt}{suffix}</div></div>")
            return "<div class='rank-list'>"+''.join(rr)+"</div>"
        with r1:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>🏃 Distancia</div>{ranking_html(advv,'distancia_km','Distancia',' km')}</div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>🔥 Alta intensidad</div>{ranking_html(advv,'carreras_alta_intensidad','Alta intensidad')}</div>", unsafe_allow_html=True)
        with r3:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>⚽ Tiros</div>{ranking_html(advv,'tiros','Tiros')}</div>", unsafe_allow_html=True)

        # La misma comparación normalizada por 90 minutos.
        def ranking_per90_html(frame, col, suffix="", topn=5):
            if frame.empty or col not in frame.columns or official.empty:
                return "<div class='ind-sub'>Sin datos suficientes para calcular /90.</div>"
            vals = frame.copy()
            vals[col] = pd.to_numeric(vals[col], errors='coerce')
            vals = vals.dropna(subset=[col])
            if vals.empty:
                return "<div class='ind-sub'>Sin datos suficientes para calcular /90.</div>"
            vals = vals.groupby('dorsal', as_index=False)[col].sum()
            mins = official.groupby('jugador', as_index=False)['minutos'].sum()
            map_df = sub_roster[['dorsal','jugador']].copy()
            map_df['dorsal'] = map_df['dorsal'].astype(int)
            map_df = map_df.merge(mins, on='jugador', how='left')
            vals['dorsal'] = vals['dorsal'].astype(int)
            vals = vals.merge(map_df[['dorsal','minutos']], on='dorsal', how='left')
            vals = vals[pd.to_numeric(vals['minutos'], errors='coerce').fillna(0) > 0].copy()
            if vals.empty:
                return "<div class='ind-sub'>Sin minutos oficiales para calcular /90.</div>"
            vals['per90'] = vals[col] * 90.0 / vals['minutos']
            vals = vals.sort_values('per90', ascending=False).head(topn)
            mx = max(float(vals['per90'].max()), 1e-9)
            rr=[]
            for pos,(_,x) in enumerate(vals.iterrows(),1):
                d=int(x.dorsal); name=roster.loc[roster.dorsal.astype(int)==d,'jugador']
                nm=name.iloc[0] if not name.empty else f"#{d}"
                val=float(x.per90); vtxt=str(round(val,1)).replace('.',',')
                rr.append(f"<div class='rank-row'><div class='rank-num'>{pos}</div><div><div class='rank-name'>#{d} · {html.escape(str(nm))}</div><div class='microbar'><span style='width:{min(100,val/mx*100):.1f}%'></span></div></div><div class='rank-value'>{vtxt}{suffix}</div></div>")
            return "<div class='rank-list'>"+''.join(rr)+"</div>"

        st.markdown("<div style='height:10px'></div><div class='section-title'>Rendimiento por 90 minutos</div>", unsafe_allow_html=True)
        p1,p2,p3 = st.columns(3)
        with p1:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>🏃 Distancia /90</div>{ranking_per90_html(advv,'distancia_km',' km')}</div>", unsafe_allow_html=True)
        with p2:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>🔥 Alta intensidad /90</div>{ranking_per90_html(advv,'carreras_alta_intensidad')}</div>", unsafe_allow_html=True)
        with p3:
            st.markdown(f"<div class='ind-panel'><div class='ind-title'>⚽ Tiros /90</div>{ranking_per90_html(advv,'tiros')}</div>", unsafe_allow_html=True)

        # Minutos en formato heatmap visual, solo en Individual.
        st.markdown("<div style='height:10px'></div><div class='section-title'>Carga de minutos</div>", unsafe_allow_html=True)
        minute_cards=[]
        for _,r in sub_roster.iterrows():
            m=int(official.loc[official.jugador==r.jugador,'minutos'].sum()) if not official.empty else 0
            cap=90*len(js)
            pct=min(100,m/cap*100) if cap else 0
            avg=m/len(js) if js else 0
            if avg < 25: color='#ef4444'
            elif avg < 45: color='#f59e0b'
            elif avg < 60: color='#facc15'
            elif avg < 75: color='#86efac'
            else: color='#15803d'
            minute_cards.append(f"<div class='minute-card'><div class='top'><span>#{int(r.dorsal)} {html.escape(str(r.jugador))}</span><span class='mins' style='color:{color}'>{m}'</span></div><div class='minbar'><span style='width:{pct:.1f}%;background:{color}'></span></div></div>")
        st.markdown("<div class='minutes-grid'>"+''.join(minute_cards)+"</div>", unsafe_allow_html=True)

        # Tabla resumen enriquecida.
        st.markdown("<div style='height:12px'></div><div class='section-title'>Tabla de rendimiento</div>", unsafe_allow_html=True)
        table=[]
        for _,r in sub_roster.iterrows():
            d=int(r.dorsal); p=str(r.jugador)
            pm=official[official.jugador==p]
            av=advv[advv.dorsal.astype(int)==d] if not advv.empty else pd.DataFrame()
            table.append({"#":d,"Jugador":p,"Posición":role_name.get(r.rol,'Jugador'),"Min":int(pm.minutos.sum()) if not pm.empty else 0,"Tit.":int(pm.titular.sum()) if not pm.empty else 0,"Km":round(pd.to_numeric(av.get('distancia_km',pd.Series(dtype=float)),errors='coerce').sum(),1) if not av.empty else None,"Tiros":int(pd.to_numeric(av.get('tiros',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty else None,"Eventos":int(pd.to_numeric(av.get('eventos_totales',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty else None})
        st.dataframe(pd.DataFrame(table).sort_values('Min',ascending=False),hide_index=True,use_container_width=True)
        st.caption("Pulsa directamente sobre un jugador para abrir su ficha individual.")
        return

    # ---------- FICHA INDIVIDUAL ----------
    pr = roster[roster.jugador==player]
    if pr.empty:
        st.session_state.ind_selected_player=None
        st.rerun()
    dorsal=int(pr.iloc[0].dorsal); rol=str(pr.iloc[0].rol); pos_label=role_name.get(rol,'Jugador')
    pm=pt_min[(pt_min.jugador==player)&(pt_min.jornada.isin(js))].copy()
    pe=pt_ev[(pt_ev.jugador==player)&(pt_ev.jornada.isin(js))].copy()
    minutes=int(pm.minutos.sum()) if not pm.empty else 0
    starts=int(pm.titular.sum()) if not pm.empty else 0
    appearances=int((pm.minutos>0).sum()) if not pm.empty else 0
    goals=int(pe.tipo.isin(['gol','penalti_gol']).sum()) if not pe.empty else 0
    yellows=int((pe.tipo=='amarilla').sum()) if not pe.empty else 0
    expulsions=int(pe.tipo.isin(['doble_amarilla','segunda_amarilla','roja']).sum()) if not pe.empty else 0
    av=adv_all[(adv_all.jornada.isin(advanced_js))&(adv_all.dorsal.astype(int)==dorsal)].copy() if advanced_js and not adv_all.empty else pd.DataFrame()

    if st.button("← Volver al resumen", key="back_individual"):
        st.session_state.ind_selected_player=None
        st.rerun()

    left,right=st.columns([1.0,2.35])
    with left:
        logo=BASE/'primer_toque_logo.png'; logo_tag=''
        if logo.exists():
            b64=base64.b64encode(logo.read_bytes()).decode(); logo_tag=f"<img src='data:image/png;base64,{b64}' style='width:58px;height:58px;object-fit:contain;float:right;background:white;border-radius:12px;padding:5px'>"
        status='Titular' if starts else ('Suplente utilizado' if minutes else 'Sin minutos')
        st.markdown(f"<div class='ind-hero'>{logo_tag}<div class='shirt-no'>#{dorsal}</div><div class='pname'>{html.escape(player)}</div><span class='pos'>{html.escape(pos_label)}</span><div class='meta'><b>{html.escape(view_label)}</b><br>{status} · {minutes} min oficiales<br>{appearances} apariciones · {starts} titularidades</div></div>",unsafe_allow_html=True)
    with right:
        dist=float(pd.to_numeric(av.get('distancia_km',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty else None
        shots=int(pd.to_numeric(av.get('tiros',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty else None
        hi=int(pd.to_numeric(av.get('carreras_alta_intensidad',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty and 'carreras_alta_intensidad' in av.columns else None
        sprints=int(pd.to_numeric(av.get('sprints',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty and 'sprints' in av.columns else None
        events_track=int(pd.to_numeric(av.get('eventos_totales',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty and 'eventos_totales' in av.columns else None
        pass_ok=int(pd.to_numeric(av.get('pases_exitosos',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av.empty and 'pases_exitosos' in av.columns and pd.to_numeric(av['pases_exitosos'],errors='coerce').notna().any() else None
        conversion = (goals / shots * 100.0) if shots not in (None,0) else None
        factor90 = (90.0 / minutes) if minutes > 0 else None
        dist90 = (dist * factor90) if (factor90 is not None and dist is not None) else None
        hi90 = (hi * factor90) if (factor90 is not None and hi is not None) else None
        sprints90 = (sprints * factor90) if (factor90 is not None and sprints is not None) else None
        shots90 = (shots * factor90) if (factor90 is not None and shots is not None) else None
        goals90 = goals * factor90 if factor90 is not None else None
        events90 = (events_track * factor90) if (factor90 is not None and events_track is not None) else None
        st.markdown(f"""<div class='ind-panel'><div class='ind-title'>Resumen</div><div class='ind-kpis'>
        <div class='ind-mini'><div class='v'>{minutes}'</div><div class='l'>MINUTOS</div></div>
        <div class='ind-mini green'><div class='v'>{goals}</div><div class='l'>GOLES</div></div>
        <div class='ind-mini'><div class='v'>{shots if shots is not None else '—'}</div><div class='l'>TIROS</div></div>
        <div class='ind-mini'><div class='v'>{(str(round(dist,1)).replace('.',',')+' km') if dist is not None else '—'}</div><div class='l'>DISTANCIA</div></div>
        <div class='ind-mini warn'><div class='v'>{yellows}</div><div class='l'>AMARILLAS</div></div>
        <div class='ind-mini red'><div class='v'>{expulsions}</div><div class='l'>EXPULSIONES</div></div>
        <div class='ind-mini'><div class='v'>{hi if hi is not None else '—'}</div><div class='l'>ALTA INT.</div></div>
        <div class='ind-mini green'><div class='v'>{(str(round(conversion,1)).replace('.',',')+'%') if conversion is not None else '—'}</div><div class='l'>CONVERSIÓN</div></div>
        </div></div>""",unsafe_allow_html=True)

        def fmt90(v, suffix=''):
            if v is None:
                return '—'
            txt = str(round(float(v),1)).replace('.',',')
            return txt + suffix
        st.markdown(f"""<div class='ind-panel' style='margin-top:9px'><div class='ind-title'>Por 90 minutos</div><div class='per90-grid'>
        <div class='per90-card'><div class='v'>{fmt90(dist90,' km')}</div><div class='l'>Distancia /90</div></div>
        <div class='per90-card'><div class='v'>{fmt90(hi90)}</div><div class='l'>Alta intensidad /90</div></div>
        <div class='per90-card'><div class='v'>{fmt90(sprints90)}</div><div class='l'>Sprints /90</div></div>
        <div class='per90-card'><div class='v'>{fmt90(shots90)}</div><div class='l'>Tiros /90</div></div>
        <div class='per90-card'><div class='v'>{fmt90(goals90)}</div><div class='l'>Goles /90</div></div>
        <div class='per90-card'><div class='v'>{fmt90(events90)}</div><div class='l'>Eventos /90</div></div>
        </div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    maps_dir=BASE/'individual_maps'
    map_days = advanced_js if jornada_ui == "Total" else advanced_js
    if jornada_ui == "Total":
        st.markdown("<div class='section-title'>Mapas por jornada</div>", unsafe_allow_html=True)
    for map_j in map_days:
        if jornada_ui == "Total":
            st.markdown(f"<div class='section-kicker'>Jornada {map_j}</div>", unsafe_allow_html=True)
        m1,m2=st.columns(2)
        heat=maps_dir/f"heat_j{map_j}_{dorsal}.png"
        shot=maps_dir/f"shots_j{map_j}_{dorsal}.png"
        av_day=adv_all[(adv_all.jornada==map_j)&(adv_all.dorsal.astype(int)==dorsal)] if not adv_all.empty else pd.DataFrame()
        shots_day=int(pd.to_numeric(av_day.get('tiros',pd.Series(dtype=float)),errors='coerce').fillna(0).sum()) if not av_day.empty else None
        with m1:
            st.markdown("<div class='map-shell'><div class='map-label'>🔥 Mapa de calor</div>",unsafe_allow_html=True)
            if heat.exists():
                st.markdown(map_image_html(heat, f"Mapa de calor J{map_j} {player}"), unsafe_allow_html=True)
                st.caption(f"Captura del tracking Veo · J{map_j}")
            else:
                st.markdown("<div class='map-empty'>Mapa todavía no extraído para este jugador/jornada.</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with m2:
            st.markdown("<div class='map-shell'><div class='map-label'>🎯 Mapa de tiros</div>",unsafe_allow_html=True)
            if shot.exists():
                st.markdown(map_image_html(shot, f"Mapa de tiros J{map_j} {player}"), unsafe_allow_html=True)
                st.caption(f"Campo completo · portería de ataque visible · J{map_j}")
            elif shots_day == 0:
                st.markdown("<div class='map-empty'>0 tiros detectados en esta jornada.</div>",unsafe_allow_html=True)
            else:
                st.markdown("<div class='map-empty'>Hay acciones registradas, pero el mapa específico todavía no está extraído.</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
    if not map_days:
        st.markdown("<div class='map-empty'>Sin tracking avanzado para esta jornada.</div>", unsafe_allow_html=True)

    c1,c2,c3=st.columns([1.1,1.1,1])
    with c1:
        rows=''
        if not av.empty:
            sums=[('Ocasiones','ocasiones'),('Tiros','tiros'),('Eventos','eventos_totales'),('Pases exitosos','pases_exitosos')]
            for lab,col in sums:
                if col in av.columns and pd.to_numeric(av[col],errors='coerce').notna().any():
                    val=pd.to_numeric(av[col],errors='coerce').fillna(0).sum(); val=int(val) if float(val).is_integer() else round(float(val),1)
                    rows+=f"<div class='ind-stat'><span>{lab}</span><b>{val}</b></div>"
            # Goles del acta validada: evita que el tracking deje a 0 un gol real (p. ej. Sebas J2).
            rows+=f"<div class='ind-stat'><span>Goles detectados</span><b>{goals}</b></div>"
            conv_txt = (str(round(conversion,1)).replace('.',',')+'%') if conversion is not None else '—'
            rows+=f"<div class='ind-stat'><span>Conversión tiros → gol</span><b>{conv_txt}</b></div>"
        if not rows: rows="<div class='ind-sub'>Sin métricas técnicas de tracking para esta jornada.</div>"
        st.markdown(f"<div class='ind-panel'><div class='ind-title'>⚽ Técnico</div>{rows}</div>",unsafe_allow_html=True)
    with c2:
        rows=''
        if not av.empty:
            metrics=[('Distancia', 'distancia_km',' km'),('Vel. media','velocidad_media_kmh',' km/h'),('Vel. máxima','velocidad_max_kmh',' km/h'),('Sprints','sprints',''),('Alta intensidad','carreras_alta_intensidad','')]
            for lab,col,suf in metrics:
                if col in av.columns and pd.to_numeric(av[col],errors='coerce').notna().any():
                    if col in ['velocidad_media_kmh','velocidad_max_kmh']:
                        val=pd.to_numeric(av[col],errors='coerce').max()
                    else: val=pd.to_numeric(av[col],errors='coerce').fillna(0).sum()
                    txt=str(round(float(val),1)).replace('.',',') if not float(val).is_integer() else str(int(val))
                    rows+=f"<div class='ind-stat'><span>{lab}</span><b>{txt}{suf}</b></div>"
        if not rows: rows="<div class='ind-sub'>Sin métricas físicas todavía.</div>"
        st.markdown(f"<div class='ind-panel'><div class='ind-title'>🏃 Físico</div>{rows}</div>",unsafe_allow_html=True)
    with c3:
        evrows=''
        if not pe.empty:
            ico={'gol':'⚽','penalti_gol':'⚽P','amarilla':'🟨','doble_amarilla':'🟨🟥','segunda_amarilla':'🟨🟥','roja':'🟥'}
            for _,e in pe.sort_values(['jornada','minuto']).iterrows():
                evrows+=f"<div class='ind-stat'><span>{ico.get(str(e.tipo),'•')} J{int(e.jornada)} · {html.escape(str(e.tipo).replace('_',' '))}</span><b>{int(e.minuto)}'</b></div>"
        if not evrows: evrows="<div class='ind-sub'>Sin goles o tarjetas en esta vista.</div>"
        st.markdown(f"<div class='ind-panel'><div class='ind-title'>🧾 Eventos</div>{evrows}</div>",unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    a,b=st.columns([1.2,1])
    with a:
        # Evolución de minutos solo J2/J3/J5, con color por carga.
        cards=[]
        for jj in [2,3]:
            rr=pt_min[(pt_min.jugador==player)&(pt_min.jornada==jj)]
            mm=int(rr.minutos.sum()) if not rr.empty else 0
            if mm <25: col='#ef4444'
            elif mm<45: col='#f59e0b'
            elif mm<60: col='#facc15'
            elif mm<75: col='#86efac'
            else: col='#15803d'
            cards.append(f"<div class='minute-card'><div class='top'><span>J{jj}</span><span class='mins' style='color:{col}'>{mm}'</span></div><div class='minbar'><span style='width:{min(100,mm/90*100):.1f}%;background:{col}'></span></div></div>")
        st.markdown("<div class='ind-panel'><div class='ind-title'>⏱️ Minutos · partidos de casa</div><div class='minutes-grid'>"+''.join(cards)+"</div><div class='ind-sub' style='margin-top:8px'>Rojo 0–25 · naranja 25–45 · amarillo 45–60 · verde claro 60–75 · verde oscuro 75–90.</div></div>",unsafe_allow_html=True)
    with b:
        day_blocks=''
        fixture_names={2:'Primer Toque C.F. 2–0 Bétera C.F.',3:'Primer Toque C.F. 2–1 Manises C.F.'}
        for link_j in js:
            link=match_link(team,link_j)
            if not link:
                continue
            goals_day=pt_ev[(pt_ev.jornada==link_j)&(pt_ev.jugador==player)&(pt_ev.tipo.isin(['gol','penalti_gol']))].sort_values('minuto')
            goal_html=''
            if not goals_day.empty:
                for _,e in goals_day.iterrows():
                    sync = VEO_GOAL_SYNC.get((int(link_j), str(player)))
                    if sync is not None:
                        ffcv_min = int(sync.get("ffcv_min", int(e.minuto)))
                        veo_clock = str(sync.get("veo_match_clock", "—"))
                        video_ts = str(sync.get("video_timestamp", "—"))
                        event_url = sync.get("event_url")
                        # Si tenemos URL específica del evento, abrimos el evento. Si no, abrimos el partido completo
                        # y mostramos el timestamp absoluto validado para localizar el gol sin inventar un enlace de salto.
                        clip_url = event_url or link
                        goal_html += (
                            f"<div class='video-goal'>⚽ <b>{html.escape(player)}</b><br>"
                            f"<span>Acta FFCV: <b>{ffcv_min}'</b> · reloj Veo: <b>{html.escape(veo_clock)}</b> · vídeo: <b>{html.escape(video_ts)}</b></span><br>"
                            f"<a href='{html.escape(clip_url,quote=True)}' target='_blank'>▶ {'Ver evento del gol' if event_url else 'Abrir partido en Veo'} · vídeo {html.escape(video_ts)}</a></div>"
                        )
                    else:
                        goal_html += (
                            f"<div class='video-goal'>⚽ <b>{html.escape(player)}</b> · acta FFCV {int(e.minuto)}' "
                            f"<span style='opacity:.72'>· sincronización Veo pendiente</span></div>"
                        )
            else:
                goal_html="<div class='video-goal' style='opacity:.72'>Sin gol del jugador en esta jornada.</div>"
            day_blocks+=f"<div class='video-day'><div class='video-day-title'>Jornada {link_j} · {fixture_names.get(link_j,'Partido')}</div><a href='{html.escape(link,quote=True)}' target='_blank'>▶ Ver partido completo</a>{goal_html}</div>"
        if not day_blocks:
            day_blocks="<span class='source-muted'>Sin enlaces específicos en esta vista.</span>"
        st.markdown(f"<div class='source-card'><div style='font-weight:950;font-size:.92rem'>🎥 Fuentes de vídeo</div><div class='source-muted'>Cada jornada muestra el partido y, debajo, los goles del jugador. Distinguimos: minuto del acta FFCV, reloj/evento de partido en Veo y timestamp absoluto del vídeo completo. El timestamp absoluto es la referencia para localizar el gol dentro del vídeo.</div>{day_blocks}</div>",unsafe_allow_html=True)

# ---------------- Sidebar / menú desplegable de rivales ----------------
with st.sidebar:
    st.markdown(
        """<div class='brand-box'><div class='brand-ball'>⚽</div><div><div class='brand-main'>FÚTBOL DATA <span>JOAN</span></div><div class='brand-sub'>Temporada 2026/27</div></div></div>""",
        unsafe_allow_html=True,
    )
    modulo = st.radio("Navegación", ["Rivales", "Equipo", "Individual"], label_visibility="collapsed")

    seleccionado = None
    if modulo == "Rivales":
        st.markdown("<div class='side-label'>Rivales · 16 equipos</div>", unsafe_allow_html=True)
        lista = equipos.sort_values("orden")["equipo"].tolist() if not equipos.empty else []
        default_idx = lista.index("Bétera C.F. 'A'") if "Bétera C.F. 'A'" in lista else 0
        seleccionado = st.selectbox(
            "Selecciona rival",
            lista,
            index=default_idx,
            help="Elige cualquiera de los 16 equipos. Bétera, C.D. Acero, Primer Toque, Salesianos y Villarreal ya tienen análisis real cargado.",
        )
        st.markdown(f"<div class='team-count'>Equipo seleccionado: <b>{html.escape(seleccionado)}</b></div>", unsafe_allow_html=True)
        with st.expander("Ver los 16 equipos"):
            for _, row in equipos.sort_values("orden").iterrows():
                mark = "✅" if row.equipo == seleccionado else "•"
                st.write(f"{mark} {int(row.orden)}. {row.equipo}")

st.markdown(
    "<div class='topbar'><div class='title'>⚽ FÚTBOL DATA JOAN · V15.6 INDIVIDUAL</div><div class='nav'>Inicio &nbsp;&nbsp; Nuestro equipo &nbsp;&nbsp; <b>Rivales</b> &nbsp;&nbsp; Competición &nbsp;&nbsp; Informes</div></div>",
    unsafe_allow_html=True,
)

if modulo == "Individual":
    render_individual()
    st.stop()
elif modulo == "Equipo":
    st.markdown(
        "<div class='team-head'><div><div class='team-name'>Equipo</div><div class='team-sub'>Módulo de Primer Toque preparado para la siguiente fase.</div></div></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------- Helpers ----------------
def team_formations(team):
    tp = partidos[(partidos.local == team) | (partidos.visitante == team)].copy()
    arr = []
    for _, r in tp.sort_values("jornada").iterrows():
        f = r.sistema_local if r.local == team else r.sistema_visitante
        if pd.notna(f) and str(f).strip() and str(f) != "PENDIENTE":
            arr.append((int(r.jornada), str(f)))
    return arr


def team_score(row, team):
    if pd.isna(row.goles_local) or pd.isna(row.goles_visitante):
        opp = row.visitante if row.local == team else row.local
        return None, None, opp
    if row.local == team:
        return int(row.goles_local), int(row.goles_visitante), row.visitante
    return int(row.goles_visitante), int(row.goles_local), row.local


def minute_class(v):
    if pd.isna(v):
        return "mx"
    x = float(v)
    if x <= 20:
        return "m0"
    if x <= 45:
        return "m1"
    if x <= 60:
        return "m2"
    if x <= 75:
        return "m3"
    return "m4"


def short_name(name):
    bits = str(name).split()
    return bits[0] if bits else ""


def display_name(name, dorsal=None):
    # El dorsal 1 figura únicamente como "Alex" en las capturas FFCV aportadas.
    # No inventamos apellidos: lo marcamos como pendiente hasta disponer del nombre completo.
    if dorsal == 1 and str(name).strip() == "Alex":
        return "Alex (apellidos pendientes)"
    return str(name)


def name_with_number(name, dorsal):
    try:
        d_int = int(dorsal)
        d_label = str(d_int)
        shown = display_name(name, d_int)
    except (TypeError, ValueError):
        d_label = str(dorsal)
        shown = display_name(name, None)
    return f"{shown} ({d_label})"


def dorsal_labels(roster_df):
    if roster_df.empty:
        return {}
    tmp = roster_df[["jugador", "dorsal"]].dropna().copy()
    tmp["dorsal"] = tmp["dorsal"].astype(int)
    return tmp.groupby("jugador")["dorsal"].apply(lambda x: "/".join(str(v) for v in sorted(set(x)))).to_dict()


def image_html(path):
    if not path.exists():
        return "<div style='font-size:54px'>🛡️</div>"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"<img src='data:image/png;base64,{b64}'>"

# ---------------- Rival elegido ----------------
team_parts = partidos[(partidos.local == seleccionado) | (partidos.visitante == seleccionado)].copy()
roster = plantillas[plantillas.equipo == seleccionado].copy()
forms = team_formations(seleccionado)

if seleccionado == "Bétera C.F. 'A'":
    logo_path = BASE / "betera_logo.png"
elif seleccionado == "C.D. Acero 'A'":
    logo_path = BASE / "acero_logo.png"
elif seleccionado == "Primer Toque C.F. 'A'":
    logo_path = BASE / "primer_toque_logo.png"
elif seleccionado == "C.F. At. Burriana - Salesianos 'A'":
    logo_path = BASE / "salesianos_logo.png"
else:
    logo_path = Path("__missing__")

st.markdown(
    f"""<div class='team-head'>{image_html(logo_path)}<div><div class='team-name'>{html.escape(seleccionado)}</div><div class='team-sub'>Lliga Comunitat Juvenil · Nord · Temporada 2026/27</div><span class='badge'>{'ANÁLISIS REAL J1–J5' if seleccionado in ["Primer Toque C.F. 'A'", "C.F. At. Burriana - Salesianos 'A'", "Villarreal C.F. 'C'"] else ('ANÁLISIS REAL J1–J4' if seleccionado in ["Bétera C.F. 'A'", "C.D. Acero 'A'"] else 'PERFIL PREPARADO · DATOS PENDIENTES')}</span></div></div>""",
    unsafe_allow_html=True,
)

# Perfiles ya desarrollados con jornadas completas.
analizados = ["Bétera C.F. 'A'", "C.D. Acero 'A'", "Primer Toque C.F. 'A'", "C.F. At. Burriana - Salesianos 'A'", "Villarreal C.F. 'C'"]
if seleccionado not in analizados:
    st.info(
        "Este equipo ya está dentro del menú de Rivales. Todavía no hemos cargado sus actas y jornadas. "
        "Bétera C.F., C.D. Acero, Primer Toque, Salesianos y Villarreal son perfiles completos y sirven como plantilla para el resto."
    )
    st.markdown("### Próximo paso cuando carguemos este rival")
    st.write("Alineaciones por jornada · minutos · % titularidad · posible XI · sistemas · goles · tarjetas · cambios · casa/fuera.")
    st.stop()

# ---------------- Filtros del rival ----------------
st.markdown("<div class='note' style='margin:8px 0 6px'><b>Todos los paneles de la ficha responden al mismo filtro:</b> Total / Casa / Fuera y, opcionalmente, a una jornada concreta.</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.1, 1, 1])
with c1:
    ambito = st.radio("Ámbito", ["Total", "Casa", "Fuera"], horizontal=True, index=0)
with c2:
    js_all = sorted(minutos.loc[minutos.equipo == seleccionado, "jornada"].dropna().astype(int).unique().tolist())
    jornada_sel = st.selectbox("Jornada", ["Total"] + [f"J{x}" for x in js_all])
with c3:
    st.selectbox("Temporada", ["2026/27"])

part = team_parts.copy()
if ambito == "Casa":
    part = part[part.local == seleccionado]
elif ambito == "Fuera":
    part = part[part.visitante == seleccionado]
if jornada_sel != "Total":
    part = part[part.jornada == int(jornada_sel[1:])]

m = minutos[minutos.equipo == seleccionado].copy()
if ambito != "Total":
    valid_js = []
    for _, r in team_parts.iterrows():
        if ambito == "Casa" and r.local == seleccionado:
            valid_js.append(int(r.jornada))
        if ambito == "Fuera" and r.visitante == seleccionado:
            valid_js.append(int(r.jornada))
    m = m[m.jornada.isin(valid_js)]
if jornada_sel != "Total":
    m = m[m.jornada == int(jornada_sel[1:])]

# Jornadas activas del filtro: todos los paneles inferiores usan exactamente el mismo ámbito.
scope_js = sorted(part.jornada.dropna().astype(int).unique().tolist()) if not part.empty else []
mm = minutos[(minutos.equipo == seleccionado) & (minutos.jornada.isin(scope_js))].copy()
al_scope = alineaciones[(alineaciones.equipo == seleccionado) & (alineaciones.jornada.isin(scope_js))].copy()
ev_scope = eventos[(eventos.equipo == seleccionado) & (eventos.jornada.isin(scope_js))].copy()

# ---------------- KPIs ----------------
stand = clasificacion[clasificacion.equipo == seleccionado].sort_values("jornada").tail(1)
pos, pts = "—", "—"
if not stand.empty:
    pos = f"{int(stand.iloc[0].posicion)}º"
    pts = str(int(stand.iloc[0].puntos))

scores = []
for _, r in part.sort_values("jornada").iterrows():
    gf, gc, opp = team_score(r, seleccionado)
    scores.append((gf, gc, opp, int(r.jornada), str(r.estado)))

known_scores = [(gf, gc) for gf, gc, _, _, _ in scores if gf is not None]
V = sum(gf > gc for gf, gc in known_scores)
E = sum(gf == gc for gf, gc in known_scores)
D = sum(gf < gc for gf, gc in known_scores)
GF = sum(gf for gf, _ in known_scores)
GC = sum(gc for _, gc in known_scores)

forms_scope = []
for _, r in part.sort_values("jornada").iterrows():
    f = r.sistema_local if r.local == seleccionado else r.sistema_visitante
    if pd.notna(f) and str(f).strip() and str(f) != "PENDIENTE":
        forms_scope.append((int(r.jornada), str(f)))
vc = pd.Series([f for _, f in forms_scope]).value_counts() if forms_scope else pd.Series(dtype=int)
main_form = vc.index[0] if len(vc) else "—"
main_pct = (vc.iloc[0] / len(forms_scope) * 100) if len(vc) else 0

cols = st.columns(6)
kpis = [
    (len(scope_js), "Jornadas del filtro", " · ".join(f"J{x}" for x in scope_js) if scope_js else "Sin jornadas"),
    (f"{V}-{E}-{D}", "V · E · D", "Victorias · Empates · Derrotas"),
    (GF if known_scores else "—", "Goles a favor", f"{len(scope_js)} jornadas" if scope_js else "Sin jornadas"),
    (GC if known_scores else "—", "Goles en contra", f"{len(scope_js)} jornadas" if scope_js else "Sin jornadas"),
    (main_form, "Sistema más usado", f"{main_pct:.0f}% ({int(vc.iloc[0]) if len(vc) else 0}/{len(forms_scope)})"),
    (pos, "Clasificación J5", f"{pts} puntos · 04/10/2026"),
]
for c, (v, l, s) in zip(cols, kpis):
    c.markdown(f"<div class='card kpi'><div class='v'>{v}</div><div class='l'>{l}</div><div class='s'>{s}</div></div>", unsafe_allow_html=True)

# Jornada concreta: acceso directo al partido arriba de la ficha.
if jornada_sel != "Total" and not part.empty:
    _rr = part.sort_values("jornada").iloc[0]
    _j = int(_rr.jornada)
    _fixture = f"{short_team_name(_rr.local)} – {short_team_name(_rr.visitante)}"
    _url = match_link(seleccionado, _j)
    if _url:
        st.markdown(
            f"<div class='video-callout'><div class='vt'>🎥 J{_j} · {html.escape(_fixture)}</div><div class='vs'>Acceso directo al partido analizado de esta jornada.</div><a class='video-link' href='{html.escape(_url, quote=True)}' target='_blank'>▶ Ver partido</a></div>",
            unsafe_allow_html=True,
        )
    elif seleccionado == "Villarreal C.F. 'C'":
        st.markdown(
            f"<div class='video-callout'><div class='vt'>🎥 J{_j} · {html.escape(_fixture)}</div><div class='vs'>Enlace del partido todavía pendiente de incorporar.</div></div>",
            unsafe_allow_html=True,
        )

# Control de coherencia: el total de eventos de gol debe cuadrar con el marcador agregado.
_ev_gf = int(ev_scope.tipo.isin(['gol','penalti_gol']).sum()) if not ev_scope.empty else 0
_ev_gc = int(ev_scope.tipo.isin(['gol_contra','penalti_contra_gol']).sum()) if not ev_scope.empty else 0
if known_scores and (_ev_gf != GF or _ev_gc != GC):
    st.warning(f"Revisión de datos: marcador agregado {GF}-{GC}, eventos cargados {_ev_gf}-{_ev_gc}. Hay que revisar algún minuto de gol.")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ---------------- Formaciones / partidos / posible XI ----------------
a, b, c = st.columns([1.05, .95, 1.35])
with a:
    rows = ""
    for form, count in vc.items():
        pct = count / len(forms_scope) * 100
        rows += f"<div class='form-row'><div>{form}</div><div class='bar'><div class='fill' style='width:{pct:.0f}%'></div></div><div>{pct:.0f}% ({count})</div></div>"
    st.markdown(
        f"<div class='card'><div class='section-title'>Formaciones utilizadas</div>{rows}<div class='note'>{' · '.join(f'J{j}: {f}' for j, f in forms_scope) if forms_scope else 'Sin formaciones para este filtro.'}</div></div>",
        unsafe_allow_html=True,
    )

with b:
    rows = ""
    for _, rr in part.sort_values("jornada").iterrows():
        j = int(rr.jornada)
        gf, gc, opp = team_score(rr, seleccionado)
        local_name = str(rr.local).replace(" 'A'", "").replace(" 'B'", "").replace(" 'C'", "")
        away_name = str(rr.visitante).replace(" 'A'", "").replace(" 'B'", "").replace(" 'C'", "")
        fixture = f"{local_name} - {away_name}"
        if pd.isna(rr.goles_local) or pd.isna(rr.goles_visitante):
            col = "#cbd5e1"
            result_html = "<span class='pending'>Pendiente</span>"
        else:
            gl, gv = int(rr.goles_local), int(rr.goles_visitante)
            col = DGREEN if gf > gc else ("#9ca3af" if gf == gc else RED)
            result_html = f"<b>{gl} - {gv}</b>"
        rows += f"<div class='match-row' style='grid-template-columns:40px 1fr 70px 14px'><div class='jtag'>J{j}</div><div>{html.escape(fixture)}</div><div>{result_html}</div><div class='dot' style='background:{col}'></div></div>"
    st.markdown(
        f"<div class='card'><div class='section-title'>Jornadas analizadas</div>{rows}</div>",
        unsafe_allow_html=True,
    )

with c:
    # XI dinámico: cambia con Total/Casa/Fuera y también con la jornada elegida.
    al = al_scope.copy()
    xi_m = mm.copy()
    njs = max(1, len(scope_js))
    starts = xi_m.groupby("dorsal")["titular"].sum() / njs * 100 if not xi_m.empty else pd.Series(dtype=float)
    recent_js = scope_js[-2:]
    recent = (
        xi_m[xi_m.jornada.isin(recent_js)].groupby("dorsal")["titular"].sum() / max(1, len(recent_js)) * 100
        if recent_js else pd.Series(dtype=float)
    )
    prob = (0.6 * starts.add(recent, fill_value=0) + 0.4 * recent.add(starts, fill_value=0)).fillna(0)
    # La fórmula anterior preserva la ponderación cuando un jugador solo aparece en una de las series.
    if not starts.empty:
        prob = (0.6 * starts.reindex(starts.index.union(recent.index), fill_value=0) +
                0.4 * recent.reindex(starts.index.union(recent.index), fill_value=0))

    rc = al.groupby(["rol", "dorsal", "jugador"]).size().reset_index(name="n") if not al.empty else pd.DataFrame(columns=["rol","dorsal","jugador","n"])
    rc["prob"] = rc.dorsal.map(prob).fillna(0) if not rc.empty else pd.Series(dtype=float)

    # El sistema del XI se adapta al sistema más usado dentro del filtro.
    system_for_xi = main_form if main_form != "—" else "1-4-3-3"
    try:
        nums = [int(x) for x in system_for_xi.split("-") if x.isdigit()]
        outfield = nums[1:] if nums and nums[0] == 1 else nums
    except Exception:
        outfield = [4, 3, 3]
    if len(outfield) != 3:
        outfield = [4, 3, 3]
    needs = {"POR": 1, "DEF": outfield[0], "MED": outfield[1], "ATA": outfield[2]}

    selected = []
    for role, n in needs.items():
        selected += rc[rc.rol == role].sort_values(["n", "prob"], ascending=False).head(n).to_dict("records")

    def line_coords(x, n):
        if n <= 1:
            ys = [50]
        else:
            ys = [18 + i * (64 / (n - 1)) for i in range(n)]
        return [(x, y) for y in ys]

    # Sentido correcto: portero dentro del área izquierda y equipo atacando hacia la derecha.
    coords = {
        "POR": line_coords(7, 1),
        "DEF": line_coords(27, needs["DEF"]),
        "MED": line_coords(51, needs["MED"]),
        "ATA": line_coords(78, needs["ATA"]),
    }
    used = {k: 0 for k in coords}
    chips = []
    for r in selected:
        role = r["rol"]
        i = used[role]
        if i >= len(coords[role]):
            continue
        used[role] += 1
        x, y = coords[role][i]
        player_label = display_name(r["jugador"], int(r["dorsal"]))
        chips.append(
            f"<div class='pchip' style='left:{x}%;top:{y}%'><div class='shirt'>{int(r['dorsal'])}</div>{html.escape(short_name(player_label))}<br><span class='ppct'>{float(r['prob']):.0f}%</span></div>"
        )
    pitch = "<div class='pitch'><div class='box-l'></div><div class='box-r'></div>" + "".join(chips) + "</div>"
    filter_label = ambito if jornada_sel == "Total" else f"{ambito} · {jornada_sel}"
    st.markdown(
        f"<div class='card'><div class='section-title'>Posible XI · {system_for_xi} · {filter_label}</div>{pitch}<div class='note'>El XI se recalcula automáticamente al cambiar Total/Casa/Fuera. Portero en su área y ataque hacia la derecha.</div></div>",
        unsafe_allow_html=True,
    )

# ---------------- Tabla de minutos ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Jugadores · minutos por jornada, peso competitivo y titularidad</div>", unsafe_allow_html=True)

js = sorted(m.jornada.astype(int).unique()) if not m.empty else []
# Una misma persona puede llevar dorsales distintos entre jornadas (p. ej. Ibrahim Zahidi 2/18).
# La tabla se agrupa por jugador para no partir sus minutos en dos filas.
dlabels = dorsal_labels(roster)
players_all = sorted(set(roster.jugador.dropna().astype(str)) | set(m.jugador.dropna().astype(str)))
table = pd.DataFrame({"jugador": players_all})
table["dorsal"] = table.jugador.map(dlabels).fillna("")
for j in js:
    d = m[m.jornada == j].groupby("jugador", as_index=False)["minutos"].sum().rename(columns={"minutos": f"J{j}"})
    table = table.merge(d, on="jugador", how="left")

jcols = [f"J{j}" for j in js]
if jcols:
    table["Total"] = table[jcols].sum(axis=1, skipna=True)
    avail = 90 * len(js)
    table["% min"] = (table.Total / avail * 100).round(0)
    starts_m = m.groupby("jugador")["titular"].sum()
    table["% tit"] = (table.jugador.map(starts_m).fillna(0) / max(1, len(js)) * 100).round(0)
    recent_js = js[-2:]
    recent_m = m[m.jornada.isin(recent_js)].groupby("jugador")["titular"].sum()
    recent_pct = table.jugador.map(recent_m).fillna(0) / max(1, len(recent_js)) * 100
    table["Prob. XI"] = (0.60 * table["% tit"] + 0.40 * recent_pct).round(0)

    evg = ev_scope[ev_scope.tipo.isin(["gol", "penalti_gol"])].groupby("jugador").size()
    eva = ev_scope[ev_scope.tipo == "amarilla"].groupby("jugador").size()
    # Distingue expulsión por doble amarilla de roja directa.
    det = ev_scope.get("detalle", pd.Series(index=ev_scope.index, dtype="object")).fillna("").astype(str).str.lower()
    double_mask = (ev_scope.tipo == "doble_amarilla") | ((ev_scope.tipo == "roja") & det.str.contains(r"doble amarilla|segunda amarilla|amarilla previa", regex=True))
    ev2a = ev_scope[double_mask].groupby("jugador").size()
    evr = ev_scope[(ev_scope.tipo == "roja") & ~double_mask].groupby("jugador").size()
    table["G"] = table.jugador.map(evg).fillna(0).astype(int)
    table["🟨"] = table.jugador.map(eva).fillna(0).astype(int)
    table["🟨🟥"] = table.jugador.map(ev2a).fillna(0).astype(int)
    table["🟥"] = table.jugador.map(evr).fillna(0).astype(int)
    table = table.sort_values(["Total", "% tit", "jugador"], ascending=[False, False, True]).reset_index(drop=True)

    head = "<tr><th>#</th><th style='text-align:left'>Jugador</th>" + "".join(f"<th>{x}</th>" for x in jcols) + "<th>Total</th><th>% min</th><th>% tit</th><th>Prob. XI</th><th>G</th><th>🟨</th><th>🟨🟥</th><th>🟥</th></tr>"
    body = []
    for _, r in table.iterrows():
        cells = "".join(f"<td class='{minute_class(r[x])}'>{'—' if pd.isna(r[x]) else int(r[x])}</td>" for x in jcols)
        body.append(
            f"<tr><td class='num'>{html.escape(str(r.dorsal))}</td><td class='name'>{html.escape(display_name(r.jugador))}</td>{cells}<td><b>{int(r.Total)}</b></td><td>{int(r['% min'])}%</td><td>{int(r['% tit'])}%</td><td><b>{int(r['Prob. XI'])}%</b></td><td>{int(r.G)}</td><td>{int(r['🟨'])}</td><td>{int(r['🟨🟥'])}</td><td>{int(r['🟥'])}</td></tr>"
        )
    st.markdown(
        f"<div class='heat-wrap'><table class='heat'>{head}{''.join(body)}</table><div class='note'>Colores: 0–20 rojo · 21–45 naranja · 46–60 amarillo · 61–75 verde claro · 76–90 verde oscuro. &nbsp; 🟨🟥 = expulsión por doble amarilla · 🟥 = roja directa.</div></div>",
        unsafe_allow_html=True,
    )
else:
    st.info("Sin minutos cargados para este filtro.")

# ---------------- Goles, disciplina, núcleo del XI y carga ----------------
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)

with d1:
    ev = ev_scope[ev_scope.tipo.isin(["gol", "penalti_gol"])]
    vcg = ev.jugador.value_counts()
    dorsal_map = dorsal_labels(roster)
    items = "".join(
        f"<div class='mini-item'><span>⚽ {html.escape(name_with_number(n, dorsal_map.get(n, 0)))}</span><b>{int(v)}</b></div>"
        if dorsal_map.get(n) else f"<div class='mini-item'><span>⚽ {html.escape(str(n))}</span><b>{int(v)}</b></div>"
        for n, v in vcg.items()
    ) or "<div class='note'>Sin goles cargados para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Goleadores registrados</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d2:
    ea = ev_scope[ev_scope.tipo == "amarilla"].jugador.value_counts()
    det_disc = ev_scope.get("detalle", pd.Series(index=ev_scope.index, dtype="object")).fillna("").astype(str).str.lower()
    double_disc_mask = (ev_scope.tipo == "doble_amarilla") | ((ev_scope.tipo == "roja") & det_disc.str.contains(r"doble amarilla|segunda amarilla|amarilla previa", regex=True))
    e2a = ev_scope[double_disc_mask].jugador.value_counts()
    er = ev_scope[(ev_scope.tipo == "roja") & ~double_disc_mask].jugador.value_counts()
    def discipline_items(series, icon):
        out = []
        for n, v in series.items():
            dorsal = dorsal_map.get(n)
            label = name_with_number(n, dorsal) if dorsal else str(n)
            out.append(f"<div class='mini-item'><span>{icon} {html.escape(label)}</span><b>{int(v)}</b></div>")
        return "".join(out)
    items = discipline_items(ea, "🟨") + discipline_items(e2a, "🟨🟥") + discipline_items(er, "🟥")
    if not items:
        items = "<div class='note'>Sin tarjetas para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Disciplina</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d3:
    # Más útil que el banquillo: identifica el núcleo que el entrenador repite de inicio.
    if not mm.empty:
        core = mm.groupby("jugador").agg(Titularidades=("titular", "sum"), Partidos=("jornada", "nunique")).reset_index()
        core["pct"] = core["Titularidades"] / max(1, len(scope_js)) * 100
        core = core.sort_values(["pct", "Titularidades", "jugador"], ascending=[False, False, True]).head(7)
        dmap_core = dorsal_labels(roster)
        items = "".join(
            f"<div class='mini-item'><span>⭐ {html.escape(name_with_number(r.jugador, dmap_core.get(r.jugador, '')))}</span><b>{r.pct:.0f}% tit.</b></div>"
            for _, r in core.iterrows()
        )
    else:
        items = "<div class='note'>Sin datos para este filtro</div>"
    st.markdown(f"<div class='card'><div class='section-title'>Núcleo del XI</div><div class='mini-list'>{items}</div></div>", unsafe_allow_html=True)

with d4:
    players = int(mm[mm.minutos > 0].jugador.nunique()) if not mm.empty else 0
    st.markdown(
        f"<div class='card'><div class='section-title'>Carga competitiva</div><div class='kpi' style='min-height:125px'><div class='v'>{players}</div><div class='l'>Jugadores utilizados</div><div class='s'>{html.escape(ambito)}{' · ' + html.escape(jornada_sel) if jornada_sel != 'Total' else ''}</div></div></div>",
        unsafe_allow_html=True,
    )

    # Penaltis: icono de balón con portería en FFCV. Se guarda jornada, minuto, lanzador y resultado.
    pen = ev_scope[ev_scope.tipo.isin(["penalti_gol", "penalti_fallado"])].sort_values(["jornada", "minuto"]) if not ev_scope.empty else pd.DataFrame()
    if not pen.empty:
        pen_items = []
        for _, pr in pen.iterrows():
            result = "Gol" if pr.tipo == "penalti_gol" else "Fallado"
            icon = "✅" if pr.tipo == "penalti_gol" else "❌"
            dorsal = dorsal_map.get(pr.jugador)
            label = name_with_number(pr.jugador, dorsal) if dorsal else str(pr.jugador)
            pen_items.append(f"<div class='mini-item'><span>{icon} J{int(pr.jornada)} · {int(pr.minuto)}' · {html.escape(label)}</span><b>{result}</b></div>")
        pen_html = "".join(pen_items)
    else:
        pen_html = "<div class='note'>Sin penaltis a favor registrados en este filtro</div>"
    st.markdown(f"<div style='height:10px'></div><div class='card'><div class='section-title'>Penaltis</div><div class='mini-list'>{pen_html}</div></div>", unsafe_allow_html=True)

# ---------------- Conversión de gol por jugador ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Conversión de gol por jugador</div>", unsafe_allow_html=True)

# Solo jugadores del equipo seleccionado que han marcado. Los autogoles no cuentan como goleador propio.
scorer_goals = ev_scope[(ev_scope.tipo.isin(["gol", "penalti_gol"])) & (~ev_scope.jugador.isin(["Autogol rival", "G.P."]))].groupby("jugador").size().reset_index(name="goles")
if not scorer_goals.empty and not mm.empty:
    mins_player = mm.groupby("jugador", as_index=False)["minutos"].sum()
    conv = scorer_goals.merge(mins_player, on="jugador", how="left")
    conv = conv[conv.minutos.fillna(0) > 0].copy()
    if not conv.empty:
        dorsal_map = dorsal_labels(roster)
        conv["Jugador"] = conv["jugador"].apply(lambda n: name_with_number(n, dorsal_map.get(n, 0)) if dorsal_map.get(n) else str(n))
        conv["Goles / 90"] = (conv["goles"] / conv["minutos"] * 90).round(2)
        conv["Minutos por gol"] = (conv["minutos"] / conv["goles"]).round(0)
        conv = conv.sort_values(["Goles / 90", "goles"], ascending=[False, False])
        # SVG propio: orden estricto de mayor a menor y columnas finas.
        n = len(conv)
        width = max(900, 105 * n)
        height = 315
        left, right, top, bottom = 58, 24, 28, 92
        plot_w, plot_h = width - left - right, height - top - bottom
        vmax = max(float(conv["Goles / 90"].max()), 0.1)
        step = plot_w / max(1, n)
        bar_w = min(24, max(12, step * 0.24))
        svg = []
        svg.append(f"<svg viewBox='0 0 {width} {height}' style='width:100%;height:auto;background:#fff;border:1px solid #e6eaf0;border-radius:14px;padding:4px'>")
        for frac in [0, .25, .5, .75, 1.0]:
            yy = top + plot_h * (1-frac)
            val_tick = vmax * frac
            svg.append(f"<line x1='{left}' y1='{yy:.1f}' x2='{width-right}' y2='{yy:.1f}' stroke='#e8edf3' stroke-width='1'/>")
            svg.append(f"<text x='{left-9}' y='{yy+4:.1f}' text-anchor='end' font-size='10' fill='#6b7c93'>{val_tick:.2f}</text>")
        for i, (_, r) in enumerate(conv.iterrows()):
            x = left + step * (i + .5)
            val = float(r["Goles / 90"])
            bh = (val / vmax) * plot_h if vmax else 0
            y0 = top + plot_h - bh
            label = html.escape(str(r["Jugador"]))
            meta = f"{int(r['goles'])} gol{'es' if int(r['goles']) != 1 else ''} · {int(r['minutos'])}'"
            svg.append(f"<rect x='{x-bar_w/2:.1f}' y='{y0:.1f}' width='{bar_w:.1f}' height='{bh:.1f}' rx='4' fill='#16a34a'/>")
            svg.append(f"<text x='{x:.1f}' y='{max(14,y0-7):.1f}' text-anchor='middle' font-size='11' font-weight='800' fill='#0b6b2e'>{val:.2f}</text>")
            svg.append(f"<text x='{x:.1f}' y='{top+plot_h+22:.1f}' text-anchor='middle' font-size='10' font-weight='700' fill='#102a43' transform='rotate(-28 {x:.1f} {top+plot_h+22:.1f})'>{label}</text>")
            svg.append(f"<text x='{x:.1f}' y='{height-14:.1f}' text-anchor='middle' font-size='9' fill='#6b7c93'>{html.escape(meta)}</text>")
        svg.append(f"<text x='16' y='{top+plot_h/2:.1f}' transform='rotate(-90 16 {top+plot_h/2:.1f})' text-anchor='middle' font-size='11' font-weight='700' fill='#64748b'>Goles / 90</text>")
        svg.append("</svg>")
        st.markdown("".join(svg), unsafe_allow_html=True)
        st.dataframe(conv[["Jugador", "goles", "minutos", "Goles / 90", "Minutos por gol"]], use_container_width=True, hide_index=True)
        st.markdown("<div class='note'>Ordenado de mayor a menor eficacia: el mejor G/90 aparece a la izquierda. Las columnas son deliberadamente finas para facilitar la comparación.</div>", unsafe_allow_html=True)
    else:
        st.info("No hay goleadores con minutos registrados para este filtro.")
else:
    st.info("No hay goleadores registrados para este filtro.")

# ---------------- Goles por tramo ----------------
st.markdown("<div style='height:10px'></div><div class='section-title'>Distribución de goles por minuto · A favor y en contra</div>", unsafe_allow_html=True)
st.markdown("<div class='goal-legend'><span><span class='legend-dot' style='background:#16a34a'></span>A favor</span><span><span class='legend-dot' style='background:#ef4444'></span>En contra</span></div>", unsafe_allow_html=True)

goals_for = ev_scope[ev_scope.tipo.isin(["gol", "penalti_gol"])].copy()
goals_against = ev_scope[ev_scope.tipo.isin(["gol_contra", "penalti_contra_gol"])].copy()
bins = [(0, 15), (15, 30), (30, 45), (45, 60), (60, 75), (75, 90)]

def count_bins(df):
    vals = []
    for lo, hi in bins:
        if lo == 0:
            n = int(((df.minuto >= lo) & (df.minuto <= hi)).sum())
        else:
            n = int(((df.minuto > lo) & (df.minuto <= hi)).sum())
        vals.append(n)
    return vals

counts_for = count_bins(goals_for)
counts_against = count_bins(goals_against)
max_goals = max(counts_for + counts_against) if (counts_for or counts_against) else 0
total_gf = sum(counts_for)
total_gc = sum(counts_against)
total_situations = total_gf + total_gc
activity = [gf + gc for gf, gc in zip(counts_for, counts_against)]
diffs = [gf - gc for gf, gc in zip(counts_for, counts_against)]
pct_for = [(gf / total_gf * 100) if total_gf else 0.0 for gf in counts_for]
pct_against = [(gc / total_gc * 100) if total_gc else 0.0 for gc in counts_against]
pct_activity = [(n / total_situations * 100) if total_situations else 0.0 for n in activity]

def tramo_label(idx):
    lo, hi = bins[idx]
    return f"{lo}–{hi}'"

def fmt_pct(v):
    return f"{v:.1f}%".replace(".0%", "%")

# Macro: primero responder dónde sucede lo importante.
if total_situations:
    idx_activity = max(range(len(bins)), key=lambda i: activity[i])
    idx_favourable = max(range(len(bins)), key=lambda i: (diffs[i], counts_for[i]))
    idx_vulnerable = min(range(len(bins)), key=lambda i: (diffs[i], -counts_against[i]))
    idx_pct_gf = max(range(len(bins)), key=lambda i: pct_for[i])
    idx_pct_gc = max(range(len(bins)), key=lambda i: pct_against[i])
    macro = (
        f"<div class='goal-macro-grid'>"
        f"<div class='goal-macro blue'><div class='t'>🎯 Tramo con más actividad</div><div class='big'>{tramo_label(idx_activity)}</div><div class='big' style='font-size:1.18rem'>{fmt_pct(pct_activity[idx_activity])}</div><div class='sub'>{activity[idx_activity]} situaciones de {total_situations} · {counts_for[idx_activity]} GF · {counts_against[idx_activity]} GC</div></div>"
        f"<div class='goal-macro green'><div class='t'>↗ Tramo más favorable</div><div class='big'>{tramo_label(idx_favourable)}</div><div class='big' style='font-size:1.18rem;color:#15803d'>{diffs[idx_favourable]:+d}</div><div class='sub'>{counts_for[idx_favourable]} GF · {counts_against[idx_favourable]} GC · diferencia</div></div>"
        f"<div class='goal-macro red'><div class='t'>🛡 Tramo más vulnerable</div><div class='big'>{tramo_label(idx_vulnerable)}</div><div class='big' style='font-size:1.18rem;color:#dc2626'>{diffs[idx_vulnerable]:+d}</div><div class='sub'>{counts_for[idx_vulnerable]} GF · {counts_against[idx_vulnerable]} GC · diferencia</div></div>"
        f"<div class='goal-macro purple'><div class='t'>▥ Mayor % de goles a favor</div><div class='big'>{tramo_label(idx_pct_gf)}</div><div class='big' style='font-size:1.18rem'>{fmt_pct(pct_for[idx_pct_gf])}</div><div class='sub'>{counts_for[idx_pct_gf]} de {total_gf} goles a favor</div></div>"
        f"<div class='goal-macro pink'><div class='t'>▥ Mayor % de goles en contra</div><div class='big'>{tramo_label(idx_pct_gc)}</div><div class='big' style='font-size:1.18rem;color:#dc2626'>{fmt_pct(pct_against[idx_pct_gc])}</div><div class='sub'>{counts_against[idx_pct_gc]} de {total_gc} goles en contra</div></div>"
        f"</div>"
    )
    st.markdown(macro, unsafe_allow_html=True)
else:
    st.markdown("<div class='note'>No hay goles registrados en este filtro para calcular patrones por tramo.</div>", unsafe_allow_html=True)

# Nivel medio: seis tramos, primero actividad total y después detalle GF/GC.
blocks = []
for i, ((lo, hi), gf, gc) in enumerate(zip(bins, counts_for, counts_against)):
    def bubble(n, against=False):
        if n == 0:
            size = 32
            klass = "goal-bubble zero"
        else:
            size = 36 + (44 * n / max(1, max_goals))
            klass = "goal-bubble against" if against else "goal-bubble"
        return f"<div class='{klass}' style='width:{size:.0f}px;height:{size:.0f}px'>{n}</div>"
    pa = pct_activity[i]
    pgf, pgc = pct_for[i], pct_against[i]
    blocks.append(
        f"<div class='goal-bin'><div class='goal-range'>{lo}–{hi}'</div>"
        f"<div class='goal-activity'><div class='goal-ring' style='background:conic-gradient(#1d63d8 {pa:.1f}%,#e8edf3 0)'><div class='goal-ring-inner'>{fmt_pct(pa)}</div></div></div>"
        f"<div class='goal-count' style='margin-top:0'>{activity[i]} de {total_situations} situaciones</div>"
        f"<div class='goal-pair'>{bubble(gf)}{bubble(gc, True)}</div>"
        f"<div class='goal-count'><span style='color:#15803d;font-weight:800'>{gf} GF</span> · <span style='color:#dc2626;font-weight:800'>{gc} GC</span></div>"
        f"<div class='goal-pctbox'>"
        f"<div class='goal-pctrow'><span>% GF</span><div class='goal-pcttrack'><div class='goal-pctfill-gf' style='width:{pgf:.1f}%'></div></div><span>{fmt_pct(pgf)} ({gf}/{total_gf})</span></div>"
        f"<div class='goal-pctrow'><span>% GC</span><div class='goal-pcttrack'><div class='goal-pctfill-gc' style='width:{pgc:.1f}%'></div></div><span>{fmt_pct(pgc)} ({gc}/{total_gc})</span></div>"
        f"</div></div>"
    )
st.markdown("<div class='goal-grid'>" + "".join(blocks) + "</div>", unsafe_allow_html=True)

# Micro: tabla corta, solo GF, GC y diferencia como pidió el usuario.
headers = "".join(f"<th>{lo}–{hi}'</th>" for lo, hi in bins) + "<th>Total</th>"
gf_cells = "".join(f"<td>{v}</td>" for v in counts_for) + f"<td><b>{total_gf}</b></td>"
gc_cells = "".join(f"<td>{v}</td>" for v in counts_against) + f"<td><b>{total_gc}</b></td>"
diff_cells_parts = []
for v in diffs:
    cls = "diff-pos" if v > 0 else ("diff-neg" if v < 0 else "diff-zero")
    diff_cells_parts.append(f"<td class='{cls}'>{v:+d}</td>")
total_diff = total_gf - total_gc
cls_total = "diff-pos" if total_diff > 0 else ("diff-neg" if total_diff < 0 else "diff-zero")
diff_cells = "".join(diff_cells_parts) + f"<td class='{cls_total}'><b>{total_diff:+d}</b></td>"
advanced = (
    "<div class='goal-detail-wrap'><div class='goal-detail-title'>⌄ Detalle avanzado por tramo de partido</div>"
    "<table class='goal-detail'><thead><tr><th></th>" + headers + "</tr></thead><tbody>"
    "<tr><td>Goles a favor (GF)</td>" + gf_cells + "</tr>"
    "<tr><td>Goles en contra (GC)</td>" + gc_cells + "</tr>"
    "<tr><td>Diferencia (GF − GC)</td>" + diff_cells + "</tr>"
    "</tbody></table></div>"
)
st.markdown(advanced, unsafe_allow_html=True)
st.markdown(
    "<div class='note'>Lectura de macro a micro: primero se identifica dónde se concentra la actividad; después se compara cada tramo y, por último, se muestra el balance exacto GF/GC. Todo responde a Total/Casa/Fuera y a la jornada seleccionada.</div>",
    unsafe_allow_html=True,
)

# Los círculos rojos de FFCV en el lado del propio equipo se guardan como G.P. (gol en propia), nunca como goleador rival.
gp_count = int(((ev_scope.tipo == "gol_contra") & (ev_scope.jugador == "G.P.")).sum()) if not ev_scope.empty else 0
if gp_count:
    st.markdown(f"<div class='note'><b>G.P.</b> · goles en propia registrados en este filtro: {gp_count}.</div>", unsafe_allow_html=True)

# ---------------- Evolución de la clasificación ----------------
st.markdown("<div style='height:14px'></div><div class='section-title'>Evolución de la clasificación · J1–J4</div>", unsafe_allow_html=True)

evo = clasificacion[clasificacion.jornada.isin([1, 2, 3, 4])].copy()
if evo.empty:
    st.info("Sin clasificación histórica cargada.")
else:
    width, height = 1100, 390
    left, right, top, bottom = 70, 30, 28, 50
    plot_w, plot_h = width-left-right, height-top-bottom
    xmap = {j: left + (j-1) * plot_w/3 for j in [1,2,3,4]}
    y = lambda pos: top + (float(pos)-1) * plot_h/15
    accent = "#16a34a" if seleccionado == "Bétera C.F. 'A'" else ("#991b1b" if seleccionado == "C.D. Acero 'A'" else ("#c2414b" if seleccionado == "C.F. At. Burriana - Salesianos 'A'" else ("#f2c400" if seleccionado == "Villarreal C.F. 'C'" else "#1d63d8")))
    parts = [f"<svg viewBox='0 0 {width} {height}' style='width:100%;height:auto;background:white;border-radius:14px'>"]
    for pos in [1,4,8,12,16]:
        yy=y(pos); parts.append(f"<line x1='{left}' y1='{yy}' x2='{width-right}' y2='{yy}' stroke='#e5e7eb' stroke-width='1'/><text x='18' y='{yy+5}' font-size='13' fill='#64748b'>{pos}º</text>")
    for j in [1,2,3,4]:
        xx=xmap[j]; parts.append(f"<text x='{xx}' y='{height-16}' text-anchor='middle' font-size='14' font-weight='700' fill='#334155'>J{j}</text>")
    # rest of league first
    for team, g in evo[evo.equipo != seleccionado].groupby('equipo'):
        g=g.sort_values('jornada')
        pts=' '.join(f"{xmap[int(r.jornada)]:.1f},{y(r.posicion):.1f}" for _,r in g.iterrows())
        if pts: parts.append(f"<polyline points='{pts}' fill='none' stroke='#cbd5e1' stroke-width='1.4' opacity='0.72'/>")
    sel=evo[evo.equipo==seleccionado].sort_values('jornada')
    if not sel.empty:
        pts=' '.join(f"{xmap[int(r.jornada)]:.1f},{y(r.posicion):.1f}" for _,r in sel.iterrows())
        parts.append(f"<polyline points='{pts}' fill='none' stroke='{accent}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>")
        for _,r in sel.iterrows():
            xx,yy=xmap[int(r.jornada)],y(r.posicion)
            parts.append(f"<circle cx='{xx}' cy='{yy}' r='6' fill='{accent}'/><text x='{xx}' y='{yy-12}' text-anchor='middle' font-size='14' font-weight='800' fill='{accent}'>{int(r.posicion)}º</text>")
    parts.append('</svg>')
    st.markdown("<div class='card'>"+''.join(parts)+"</div>", unsafe_allow_html=True)
    if not sel.empty:
        seq = " → ".join(f"J{int(r.jornada)}: {int(r.posicion)}º" for _, r in sel.iterrows())
        st.markdown(f"<div class='card' style='border-left:7px solid {accent};margin-top:8px'><b>{html.escape(seleccionado)}</b> · {seq}</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>El equipo que estás analizando aparece siempre destacado; el resto de la liga queda en segundo plano.</div>", unsafe_allow_html=True)

# En vista Total, biblioteca de todos los partidos del equipo con sus enlaces.
if ambito == "Total" and jornada_sel == "Total":
    st.markdown("<div style='height:14px'></div><div class='section-title'>Partidos analizados · enlaces de vídeo</div>", unsafe_allow_html=True)
    _cards = []
    for _, _rr in team_parts.sort_values("jornada").iterrows():
        _j = int(_rr.jornada)
        _fixture = f"{short_team_name(_rr.local)} – {short_team_name(_rr.visitante)}"
        if pd.notna(_rr.goles_local) and pd.notna(_rr.goles_visitante):
            _res = f"{int(_rr.goles_local)}–{int(_rr.goles_visitante)}"
        else:
            _res = "Resultado pendiente"
        _url = match_link(seleccionado, _j)
        _action = (f"<a href='{html.escape(_url, quote=True)}' target='_blank'>▶ Ver partido</a>" if _url else "<span class='no-link'>Enlace pendiente</span>")
        _cards.append(
            f"<div class='match-link-card'><div class='mj'>Jornada {_j}</div><div class='mf'>{html.escape(_fixture)}</div><div class='mr'>{html.escape(_res)}</div>{_action}</div>"
        )
    st.markdown("<div class='match-links-grid'>" + "".join(_cards) + "</div>", unsafe_allow_html=True)

st.caption("V15.6 · Individual J2 + J3 · rankings /90 · conversión · mapas completos · sincronización Veo con timestamp absoluto validado.")
