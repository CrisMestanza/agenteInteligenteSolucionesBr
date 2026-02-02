from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}

DIAS_SEMANA = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "sabado": 5
}

def resolver_fecha_usuario(texto_usuario: str):
    texto = texto_usuario.lower()
    hoy = datetime.now(ZoneInfo("America/Lima")).date()

    # 1. Hoy / mañana / pasado mañana
    if "pasado mañana" in texto or "pasadomañana" in texto:
        return hoy + timedelta(days=2)

    if "mañana" in texto:
        return hoy + timedelta(days=1)

    if "hoy" in texto:
        return hoy

    # 2. Fecha explícita: 12 de marzo
    match = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)", texto)
    if match:
        dia = int(match.group(1))
        mes_texto = match.group(2)

        if mes_texto in MESES:
            mes = MESES[mes_texto]
            año = hoy.year
            fecha = datetime(año, mes, dia).date()

            if fecha < hoy:
                fecha = datetime(año + 1, mes, dia).date()

            return fecha

    # 3. Fecha numérica: 12/03 o 12-03
    match = re.search(r"(\d{1,2})[/-](\d{1,2})", texto)
    if match:
        dia, mes = map(int, match.groups())
        año = hoy.year
        fecha = datetime(año, mes, dia).date()

        if fecha < hoy:
            fecha = datetime(año + 1, mes, dia).date()

        return fecha

    # 4. Día de la semana (lunes, martes...)
    for dia_texto, dia_num in DIAS_SEMANA.items():
        if re.search(rf"\b{dia_texto}\b", texto):
            diferencia = dia_num - hoy.weekday()
            if diferencia < 0:
                diferencia += 7
            return hoy + timedelta(days=diferencia)

    return None


def obtener_horarios_validos(fecha_cita):
    if not fecha_cita:
        return ""

    dia_semana = fecha_cita.weekday()  # 0=lunes, 5=sábado

    if dia_semana == 5:  # sábado
        return "- 09:00\n- 10:00\n- 11:00\n- 12:00"
    elif dia_semana < 5:  # lunes a viernes
        return "- 16:00\n- 18:00"
    else:
        return ""  # domingo no se atiende


def obtener_horarios_disponibles(fecha_cita, tipo_cita, ocupados):
    """
    fecha_cita: date
    tipo_cita: 'virtual' | 'presencial'
    ocupados: lista de strings 'YYYY-MM-DD HH:MM'
    """
    if not fecha_cita:
        return ""

    # Horarios base según día
    dia_semana = fecha_cita.weekday()  # 0=lunes ... 5=sábado

    if dia_semana == 5:  # sábado
        horarios_base = ["09:00", "10:00", "11:00", "12:00"]
    elif dia_semana < 5:
        horarios_base = ["16:00", "18:00"]
    else:
        return ""

    fecha_str = fecha_cita.strftime("%Y-%m-%d")

    # Ocupados solo de ese día
    ocupados_dia = {
        h.split(" ")[1]
        for h in ocupados
        if h.startswith(fecha_str)
    }

    # Filtrar
    disponibles = [
        h for h in horarios_base if h not in ocupados_dia
    ]

    return "\n".join([f"- {h}" for h in disponibles])
