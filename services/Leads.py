from fastapi import APIRouter
import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("apiMonday")
BOARD_ID = "9523197333"
GROUP_ID = "topics"

def newLeads():
    query = f"""
    {{
      boards(ids: {BOARD_ID}) {{
        groups(ids: ["{GROUP_ID}"]) {{
          items_page(limit: 100) {{
            items {{
              id
              name
              column_values {{
                id
                text
              }}
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

    items = response.json()["data"]["boards"][0]["groups"][0]["items_page"]["items"]

    nuevos = []

    for item in items:
        telefono = None
        ia = None

        for col in item["column_values"]:
            if col["id"] == "phone_mkshh797":
                telefono = col["text"]
            if col["id"] == "text_mkzzx8z1":  # IA
                ia = col["text"]

        if telefono and (ia is None or ia == ""):
            nuevos.append({
                "item_id": item["id"],
                "name": item["name"],
                "telefono": telefono
            })

    return nuevos

