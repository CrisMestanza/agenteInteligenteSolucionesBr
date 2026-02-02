from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from services.twilio import enviar_whatsapp
from services.chatbot import bot

router = APIRouter()

# Diccionario temporal en memoria (en producción, usa DB)
contactos_respondidos = {}

@router.post("/whatsapp", response_class=PlainTextResponse)
async def recibir_mensaje(From: str = Form(...), Body: str = Form(...)):
    telefono = From.replace("whatsapp:", "")
    mensaje = Body.strip()
    nombre = telefono

    print(f"📩 Mensaje de {telefono}: {mensaje}")

    # ✅ Si el usuario responde por primera vez
    if telefono not in contactos_respondidos:
        contactos_respondidos[telefono] = True  # Lo marcamos como “respondido”

        # Envía un saludo inicial (solo una vez)
        bienvenida = (
            f"👋 ¡Hola! Gracias por escribirnos. Soy tu asistente de *Encanto de Tarapoto*. "
            "¿Podrías confirmarme tu nombre y correo electrónico para continuar?"
        )
        enviar_whatsapp(telefono, bienvenida)
        return "OK"

    # ✅ Si ya respondió antes → sigue la conversación con el bot
    respuesta = bot(nombre, mensaje, telefono)
    print(f"🤖 Bot responde: {respuesta}")

    enviar_whatsapp(telefono, respuesta)
    return "OK"
