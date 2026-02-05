import os
from datetime import datetime
from zoneinfo import ZoneInfo
import re

def limpiar_nombre(nombre: str) -> str:
    nombre = nombre.strip()
    nombre = re.sub(r"[^\w\s-]", "", nombre)
    nombre = nombre.replace(" ", "_")
    return nombre


def guardar_conversacion(nombre_lead, telefono, mensaje_usuario, respuesta_bot):
    # 📅 Fecha actual Perú
    hoy = datetime.now(ZoneInfo("America/Lima")).strftime("%Y-%m-%d")

    # 📁 Carpeta por fecha
    base_dir = "conversaciones"
    carpeta_fecha = os.path.join(base_dir, hoy)
    os.makedirs(carpeta_fecha, exist_ok=True)

    # 🏷 Nombre del archivo
    nombre_limpio = limpiar_nombre(nombre_lead)
    archivo = f"{nombre_limpio}_{telefono}.txt"
    ruta_archivo = os.path.join(carpeta_fecha, archivo)

    # ⏰ Hora actual
    hora = datetime.now(ZoneInfo("America/Lima")).strftime("%H:%M:%S")

    # ✍ Guardar conversación
    with open(ruta_archivo, "a", encoding="utf-8") as f:
        f.write(f"[{hora}] Usuario: {mensaje_usuario}\n")
        # f.write(f"[{hora}] Setter: {respuesta_bot}\n")
        f.write("-" * 60 + "\n")


def leer_conversacion_del_dia(nombre_lead, telefono):
    hoy = datetime.now(ZoneInfo("America/Lima")).strftime("%Y-%m-%d")

    base_dir = "conversaciones"
    carpeta_fecha = os.path.join(base_dir, hoy)

    nombre_limpio = limpiar_nombre(nombre_lead)
    archivo = f"{nombre_limpio}_{telefono}.txt"
    ruta = os.path.join(carpeta_fecha, archivo)

    if not os.path.exists(ruta):
        return ""

    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()
