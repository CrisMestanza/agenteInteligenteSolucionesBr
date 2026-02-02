from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv
from services.chatbot import *
load_dotenv()

app = FastAPI()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Marcar IA = SI
def marcar_ia_si(item_id):
    mutation = f"""
    mutation {{
      change_simple_column_value(
        item_id: {item_id},
        board_id: "9523197333",
        column_id: "text_mkzzx8z1",
        value: "Sí"
      ) {{
        id
      }}
    }}
    """

    requests.post(
        "https://api.monday.com/v2",
        json={"query": mutation},
        headers={"Authorization": API_KEY}
    )


# Verificación webhook (Meta)
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))

    return {"error": "Invalid token"}


# Envíar template de WhatsApp
@app.get("/sendTemplate")
def send_whatsapp_template(to: str, nombre_cliente: str):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "saludo_inicial_variable",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "header", # Cambiado de 'body' a 'header'
                    "parameters": [
                        {
                            "type": "text",
                            "text": nombre_cliente # Aquí enviamos el nombre al encabezado
                        }
                    ]
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    return requests.post(url, json=payload, headers=headers)

#Envíar mensaje de texto, después de la respuesta
@app.get("/sendMessage")
def send_whatsapp_text(to: str, message: str):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("SEND STATUS:", response.status_code, response.json())


# 📥 Recibir mensajes
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        entry = data.get("entry", [])
        if not entry:
            return {"status": "IGNORED"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "IGNORED"}

        value = changes[0].get("value", {})

        # 🔴 IGNORAR eventos sin mensajes
        if "messages" not in value:
            print("ℹ Evento sin mensaje (status/read/delivery)")
            return {"status": "IGNORED"}

        msg = value["messages"][0]

        # 🔴 SOLO texto
        if msg.get("type") != "text":
            return {"status": "IGNORED"}

        from_number = str(msg.get("from"))
        text = msg["text"]["body"]

        if not isinstance(from_number, str):
            print("❌ Teléfono inválido:", from_number)
            return {"status": "IGNORED"}

        print("✅ MENSAJE RECIBIDO:", text)

        respuestaBot = bot("Agente", text, from_number)

        send_whatsapp_text(from_number, respuestaBot)

    except Exception as e:
        print("❌ ERROR WEBHOOK:", e)
        print("❌ DATA:", data)

    return {"status": "EVENT_RECEIVED"}


# Procesador de nuevos leads en Monday
# En main.py, actualiza esta sección:
def procesar_leads():
    leads = newLeads()

    for lead in leads:
        # Limpieza básica del teléfono: eliminar espacios o símbolos si los hubiera
        telefono = str(lead["telefono"]).replace(" ", "").replace("+", "")
        
        print(f"📩 Enviando a {lead['name']} - {telefono}")

        resp = send_whatsapp_template(telefono, lead["name"])

        if resp.status_code == 200:
            marcar_ia_si(lead["item_id"])
            print(f"✅ IA marcada como Sí para {lead['name']}")
        else:
            print(f"❌ Error al enviar WhatsApp a {lead['name']}")
            # ESTO MOSTRARÁ EL ERROR REAL DE META:
            print(f"CÓDIGO: {resp.status_code} | DETALLE: {resp.text}")

# Ejecutar cada 5 segundos 
import time
import threading

def loop_leads():
    while True:
        procesar_leads()
        time.sleep(10)

@app.on_event("startup")
def start_loop():
    thread = threading.Thread(target=loop_leads)
    thread.daemon = True
    thread.start()
