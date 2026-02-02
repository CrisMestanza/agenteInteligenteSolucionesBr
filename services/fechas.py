from datetime import datetime
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Traer las fechas de agendas presenciales
def fechasPresenciales():
    API_KEY = os.getenv("apiMonday")
    BOARD_ID = "9676101124"
    GROUP_ID = "topics"
    query = f"""
    {{
    boards(ids: {BOARD_ID}) {{
        groups(ids: ["{GROUP_ID}"]) {{
        items_page(limit: 100) {{
            items {{
            name
            column_values {{
                text
                column {{ title }}
            }}
            }}
        }}
        }}
    }}
    }}
    """

    url = "https://api.monday.com/v2"
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}

    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()

    if "errors" in data:
        print("Error:", data["errors"])
        exit()

    items = data["data"]["boards"][0]["groups"][0]["items_page"]["items"]

    # === Crear lista de agendas ===
    presencial = []

    for item in items:
        for col in item["column_values"]:
            if col["column"]["title"] == "Agenda":
                presencial.append(col["text"] or "(sin agenda)")
                break  # si solo hay una columna llamada Agenda, puedes salir del bucle
            
    return presencial


# Traer las fechas de agendas virtuales
def fechasVirtuales():

    API_KEY = os.getenv("apiMonday")
    BOARD_ID = "9676101124"
    GROUP_ID = "group_mktrg3rm"

    query = f"""
    {{
    boards(ids: {BOARD_ID}) {{
        groups(ids: ["{GROUP_ID}"]) {{
        items_page(limit: 100) {{
            items {{
            name
            column_values {{
                text
                column {{ title }}
            }}
            }}
        }}
        }}
    }}
    }}
    """

    url = "https://api.monday.com/v2"
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}

    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()

    if "errors" in data:
        print("Error:", data["errors"])
        exit()

    items = data["data"]["boards"][0]["groups"][0]["items_page"]["items"]

    # === Crear lista de agendas ===
    virtual = []

    for item in items:
        for col in item["column_values"]:
            if col["column"]["title"] == "Agenda":
                virtual.append(col["text"] or "(sin agenda)")
                break  # si solo hay una columna llamada Agenda, puedes salir del bucle

    return virtual


# Fechas a partir de esta fecha
def fechaActual():
    presencial = fechasPresenciales()
    virtual = fechasVirtuales()
    # Inicializamos las nuevas listas
    newPresencial = []
    newVirtual = []

    # Fecha actual
    fechaActual = datetime.now()
    # print("Fecha actual:", fechaActual)

    # Fechas presenciales
    for fecha in presencial:
        try:
            # Convertir texto a datetime (solo si es válido)
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M")
            # Si la fecha es futura o igual a hoy → guardar
            if fecha_dt >= fechaActual:
                newPresencial.append(fecha)
        except ValueError:
            # Ignorar "(sin agenda)" u otros textos no válidos
            continue
        
        
    # Fechas virtuales
    for fecha in virtual:
        try:
            # Convertir texto a datetime (solo si es válido)
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M")
            # Si la fecha es futura o igual a hoy → guardar
            if fecha_dt >= fechaActual:
                newVirtual.append(fecha)
        except ValueError:
            # Ignorar "(sin agenda)" u otros textos no válidos
            continue

    # print("Fechas futuras PRESENCIAL:")
    # print(newPresencial)
    # print("Fechas futuras virtual:")
    # print(newVirtual)
    return newPresencial, newVirtual