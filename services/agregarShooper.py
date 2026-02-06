import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

API_KEYM = os.getenv("apiMonday")

hoy_dt = datetime.now(ZoneInfo("America/Lima")) + timedelta(hours=5)

# formatear al final
hoy = hoy_dt.strftime("%Y-%m-%d %H:%M:%S")

print(f"Fecha actual en America/Lima: {hoy}")


# agregar agenda virtual
def agregarVirtualShooper(nombre, fecha, telefono,resumen):
    API_KEY = API_KEYM
    BOARD_ID = 9676101124
    """
    Crea un nuevo item en Monday.com con nombre, fecha y teléfono.
    """
    resumen = resumen.replace("\n", " ").replace('"', "'")


    # 🔹 Armar diccionario con columnas
    columnas = {
        "date_mkts5xcj": fecha,      # Columna de fecha (Agenda)
        "phone_mktbj18p": telefono,   # Columna de teléfono
        "text_mm00885h": "Sí",   # Columna IA marcada como Sí
        "date": hoy,
        "long_text_mm088pzm": resumen
    }
    # 🔹 Convertir a JSON escapado (Monday requiere string con comillas escapadas)
    columnas_json = json.dumps(columnas).replace('"', '\\"')

    # 🔹 Armar la query GraphQL
    query = f"""
    mutation {{
      create_item(
        board_id: {BOARD_ID},
        item_name: "{nombre}",
        column_values: "{columnas_json}"
      ) {{
        id
        name
      }}
    }}
    """

    # 🔹 Headers para la API
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    # 🔹 Enviar solicitud a Monday.com
    response = requests.post("https://api.monday.com/v2", json={"query": query}, headers=headers)

    # 🔹 Imprimir respuesta legible
    print(json.dumps(response.json(), indent=2))

    # 🔹 Retornar respuesta limpia (opcional)
    data = response.json().get("data", {}).get("create_item", {})
    return {
        "id": data.get("id"),
        "nombre": data.get("name"),
        "telefono": telefono,
        "fecha": fecha
    }



# Agregar agenda presencial
def agregarShooperPresencial(nombre, fecha, telefono):
    API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUzMTIxNTk0NywiYWFpIjoxMSwidWlkIjo3NzY2MjM2OSwiaWFkIjoiMjAyNS0wNi0yNVQyMTo1NzoyNS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MzAxMzc2OTEsInJnbiI6InVzZTEifQ.EgxW5NmAM3UAYVhIu7oAzkMwKk03qa_1n5-7TaTB4E0"
    BOARD_ID = 9676101124
    GROUP_ID = "topics"
    """
    Crea un nuevo ítem en Monday.com dentro del grupo 'topics'
    con nombre, fecha y teléfono.
    """

    # 🔹 Crear diccionario con columnas (Agenda y Teléfono)
    columnas = {
        "date_mkts5xcj": fecha,       # Columna de fecha (Agenda)
        "phone_mktbj18p": telefono    # Columna de teléfono
    }

    # 🔹 Convertir a JSON escapado (Monday.com requiere comillas escapadas)
    columnas_json = json.dumps(columnas).replace('"', '\\"')

    # 🔹 Armar la query GraphQL
    query = f"""
    mutation {{
      create_item(
        board_id: {BOARD_ID},
        group_id: "{GROUP_ID}",
        item_name: "{nombre}",
        column_values: "{columnas_json}"
      ) {{
        id
        name
        group {{
          title
        }}
      }}
    }}
    """

    # 🔹 Encabezados de autenticación
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    # 🔹 Enviar la solicitud POST a la API de Monday
    response = requests.post("https://api.monday.com/v2", json={"query": query}, headers=headers)

    # 🔹 Imprimir la respuesta completa formateada
    print(json.dumps(response.json(), indent=2))

    # 🔹 Retornar una versión limpia de la respuesta
    data = response.json().get("data", {}).get("create_item", {})
    return {
        "id": data.get("id"),
        "nombre": data.get("name"),
        "grupo": data.get("group", {}).get("title"),
        "telefono": telefono,
        "fecha": fecha
    }



