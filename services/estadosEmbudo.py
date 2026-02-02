
import requests
import os
import json

API_KEY = os.getenv("apiMonday")
BOARD_ID = 9523197333
EMBUDO_COLUMN_ID = "color_mksh498j"

def cambiar_estado_embudo(item_id: str, nuevo_estado: str):
    mutation = """
    mutation ($value: JSON!) {
      change_column_value(
        item_id: %s,
        board_id: %s,
        column_id: "%s",
        value: $value
      ) {
        id
      }
    }
    """ % (item_id, BOARD_ID, EMBUDO_COLUMN_ID)

    variables = {
        "value": json.dumps({"label": nuevo_estado})
    }

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": mutation, "variables": variables},
        headers={"Authorization": API_KEY}
    )

    return response.json()

# Eliminar 
def eliminar_item(item_id: str):
    mutation = """
    mutation {
      delete_item (item_id: %s) {
        id
      }
    }
    """ % item_id

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": mutation},
        headers={"Authorization": API_KEY}
    )

    return response.json()

# Nombre del usuario Lead
def obtener_nombre_item(item_id: str):
    query = """
    query {
      items (ids: [%s]) {
        id
        name
      }
    }
    """ % item_id

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query},
        headers={"Authorization": API_KEY}
    )

    data = response.json()
    return data["data"]["items"][0]["name"]

# Hacer busqueda por telefono y obtener item ID
def obtener_item_id_por_telefono(telefono):
    telefono = str(telefono)
    query = f"""
    {{
      boards(ids: {BOARD_ID}) {{
        items_page(limit: 100) {{
          items {{
            id
            column_values {{
              id
              text
            }}
          }}
        }}
      }}
    }}
    """

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query},
        headers={"Authorization": API_KEY}
    )


    items = response.json()["data"]["boards"][0]["items_page"]["items"]

    for item in items:
        for col in item["column_values"]:
            if col["id"] == "phone_mkshh797" and telefono in col["text"]:
                return item["id"]


    return None
