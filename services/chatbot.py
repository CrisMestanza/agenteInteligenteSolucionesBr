
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from datetime import datetime, timedelta
import locale
from zoneinfo import ZoneInfo
from services.fechas import *
from services.Leads import *
from services.agregarShooper import *
from services.estadosEmbudo import *
from services.calcularFecha import *
import os
import re
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()

vectordb = Chroma(
    persist_directory="vectordb",
    embedding_function=embeddings
)


retriever = vectordb.as_retriever(search_kwargs={"k": 4})
memories = {}

def get_memory(user_id):
    user_id = str(user_id)  # 🔒 FORZAR STRING

    if user_id not in memories:
        memories[user_id] = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="input_text",
            return_messages=False
        )
    return memories[user_id]



# memory = ConversationBufferMemory(
#     memory_key="chat_history", 
#     input_key="input_text", 
#     return_messages=False 
# ) 

model = ChatOpenAI(model_name="gpt-4o-mini")

prompt = """
Eres un setter de una inmobiliaria, tu función es concretar citas con los nuevos leads que te pasan.
Usa la siguiente información recuperada del sistema para conocer los horarios y fechas:
{context}

IMPORTANTE:
La fecha exacta de la cita ya fue calculada por el sistema backend.
NO intentes recalcular fechas.
NO infieras días ni meses.
USA EXCLUSIVAMENTE la siguiente fecha cuando corresponda:

Fecha calculada de la cita: {fecha_cita}

Usa emojis para hacer la conversación más amena.

Sigue este flujo de conversación:

1 Cuando el usuario te diga diga de donde es preguntale lo siguiente:
    Me gustaría hacerte algunas preguntas para conocer mejor lo que estás buscando 
    ¿Deseas adquirir tu lote para:
    - Primera o segunda vivienda
    - Inversión (Airbnb)
    - Plusvalía
    (No digas hola ya que el usuario ya te saludó)
2. Cuando te responda la pregunta anterior, dile:
    ¡Excelente elección! 
    Encanto de Tarapoto se encuentra en su Primera Etapa de ejecución, donde ya estamos iniciando las obras clave que impulsarán el valor integral del proyecto 
    Esto garantiza que tu inversión / plusvalía sea segura y en constante crecimiento 
    Para poder asesorarte mejor, ¿en cuánto tiempo deseas realizar la compra? 

3. Cuando te responda la pregunta anterior, dile:
    ¿Esta inversión prefieres financiarla o adquirirla con capital propio?
    

4 Cuando te responda la anterior pregunta, dile 
    " ¡Excelente! 
    Basándome en todo lo que me has comentado, Encanto de Tarapoto es el proyecto ideal para ti 
    Coméntame, para que puedas conocer más sobre nuestro Proyecto Encanto de Tarapoto, ¿te agendo una visita virtual o presencial?
    " 
    - Tiene que eligir entre virtual o presencial, si no te responde con una de esas, vuelve a preguntarle hasta que elija una de las dos opciones.
    
5 Si te dice presencial, dile que día de esta o la proxíma semana quiere agendar la cita, conciderando la fecha y el día actual que estamos {now}, 
  ojo no muestres los horarios disponibles ni nada por el estilo, lo importante es saber que día quiere, y dile al final del mensaje que atendemos hasta sabado a medio día, solo eso 
   - Si te dice el día y la hora, dile que irán por pasos e indicale que primero elija unicamente el día o la fecha, obligatoriamente que elija primero el día o la fecha, no digas que horarios estan libres o ocupados en este punto
   y deja que el elija el día, no le digas por ejemplo "¿Te gustaría que sea mañana, 5 de febrero?", no le des opciones, solo dile que elija el día o la fecha
   - Si te dice unicamente el día pasa al punto 7 directamente
  
  
6 Si te dice presencial, dile que día de esta o la proxíma semana quiere agendar la cita, conciderando la fecha y el día actual que estamos {now}, 
  ojo no muestres los horarios disponibles ni nada por el estilo, lo importante es saber que día quiere, y dile al final del mensaje que atendemos hasta sabado a medio día, solo eso 
   - Si te dice el día y la hora, dile que irán por pasos e indicale que primero elija unicamente el día o la fecha, obligatoriamente que elija primero el día o la fecha, no digas que horarios estan libres o ocupados en este punto
    y deja que el elija el día, no le digas por ejemplo "¿Te gustaría que sea mañana, 5 de febrero?", no le des opciones, solo dile que elija el día o la fecha
   - Si te dice unicamente el día pasa al punto 7 directamente
  
7.  Tienen que cumplir el punto 5 o 6 primero, luego de que indique el día o fecha, muestras los Horarios DISPONIBLES para la fecha calculada ({fecha_cita}):
    Para virtual {horariosVirtualesDisponibles} y para presencial {horariosPresencialesDisponibles}, muestra depende lo que eligio el usuario

    IMPORTANTE:
    - SOLO muestra los horarios listados.
    - Si no hay horarios disponibles, indícalo claramente.

8  Si te dice mejor otra fecha o día, muestras los Horarios DISPONIBLES para la fecha calculada ({fecha_cita}):
    Para virtual {horariosVirtualesDisponibles} y para presencial {horariosPresencialesDisponibles}, muestra depende lo que eligio el usuario

    IMPORTANTE:
    - SOLO muestra los horarios listados.
    - Si no hay horarios disponibles, indícalo claramente.
    
    Y así hasta que se decida por un horario, fecha.

9 Cuando te indique la hora de la cita, dile que fue agendado en la fecha y hora que indico y le agradeces y agregas la palabra pk seguido con la palabra virtual o presencial y agrega la fecha y hora que te indico en este formato "2025-10-23 13:40" ej. (pk virtual 2026-03-20 18:00), siempre escribes en este formato la cita que agendo al final(pk virtual 2026-03-20 18:00)

10 Si el usuario pide información acerca del proyecto, responde con información de {context_pdf}, ya sea precios, medidas, etc , pero principalmente enfócate en concretar la cita. 
  Solo da información que se encuentra el pdf, no inventes información.
  Si ya concretaste la cita, ya puedes contestar libremente cualquier otra duda que tenga el usuario, siempre y cuando sea información que se encuentra en el pdf.
  
Memoria : {chat_history}
Mensaje del usuario : {input_text}
"""


template = PromptTemplate(
    input_variables=[
        "chat_history",
        "context",
        "context_pdf",
        "input_text",
        "now",
        "fecha_cita",
        "horarios_validos"
    ],
    template=prompt
)




def bot(nombre, mensaje, telefono):
    """
    Procesa un mensaje de WhatsApp o chat y devuelve la respuesta del bot.
    Si el usuario indica 'pk presencial' o 'pk virtual', agenda en Monday.
    """
    telefono = str(telefono)
    memory = get_memory(telefono)

    chain = LLMChain(
        llm=model,
        prompt=template,
        memory=memory,
    )
    # Obtener horarios ocupados
    newPresencial, newVirtual = fechaActual()

    # Crear contexto dinámico
    context = f"""
    Fechas PRESENCIALES no disponibles:
    {chr(10).join(newPresencial) if newPresencial else "Sin horarios futuros"}

    Fechas VIRTUALES no disponibles:
    {chr(10).join(newVirtual) if newVirtual else "Sin horarios futuros"}
    """
    # Obtener día y fecha actual de Perú
    hoy_peru = datetime.now(ZoneInfo("America/Lima"))
    
    # Obtener contexto del PDF
    docs_pdf = retriever.get_relevant_documents(mensaje)
    context_pdf = "\n".join([doc.page_content for doc in docs_pdf])

    # obtener fecha calculada 
    fecha_cita = resolver_fecha_usuario(mensaje)
    horarios_validos = obtener_horarios_validos(fecha_cita)

    if fecha_cita:
        fecha_str = fecha_cita.strftime("%Y-%m-%d")
    else:
        fecha_str = "NO_DEFINIDA"


    print("fecha cita calculada:", fecha_str)
    print("Horarios validos:", horarios_validos)
    print("Horarios validos:", horarios_validos)
    print("Horarios virtuales ocupados:", newVirtual)
    
    horarios_virtuales_disponibles = obtener_horarios_disponibles(
                                                                fecha_cita,
                                                                "virtual",
                                                                newVirtual
                                                                )

    horarios_presenciales_disponibles = obtener_horarios_disponibles(
                                                                    fecha_cita,
                                                                    "presencial",
                                                                    newPresencial
                                                                )

    # Generar respuesta del modelo
    respuesta = chain.invoke({
        "context": context,
        "now": hoy_peru.strftime("%A %d de %B de %Y"),
        "input_text": mensaje,
        "context_pdf": context_pdf,
        "fecha_cita": fecha_str,
        "horarios_validos": horarios_validos,
        "horariosVirtualesDisponibles": horarios_virtuales_disponibles,
        "horariosPresencialesDisponibles": horarios_presenciales_disponibles
    })

    respuesta_texto = respuesta["text"]
    respuesta_texto = re.sub(r"^.*?\bAI:\s*", "", respuesta_texto, flags=re.IGNORECASE | re.DOTALL).strip()
    print("\n🤖 Setter:", respuesta_texto, "\n")

    # Buscar si el mensaje contiene "pk presencial" o "pk virtual"
    coincidencia = re.search(
        r"pk\s+(virtual|presencial)[,\s]+(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2})",
        respuesta_texto,
        re.IGNORECASE
    )


    if coincidencia:
        tipo_cita = coincidencia.group(1).lower()
        fecha_hora = coincidencia.group(2)

        # Normalizar hora (añadir segundos)
        if len(fecha_hora.split(":")) == 2:
            fecha_hora += ":00"

        # Convertir a UTC (+5 horas)
        fecha_local = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
        fecha_utc = fecha_local + timedelta(hours=5)
        fecha_formateada = fecha_utc.strftime("%Y-%m-%d %H:%M:%S")

        # Registrar cita en Monday según tipo
        item_id = obtener_item_id_por_telefono(telefono)

        if item_id:
            if tipo_cita == "virtual":
                
                nombreLead = obtener_nombre_item(item_id)
                eliminar_item(item_id)
                agregarVirtualShooper(nombreLead, fecha_formateada, telefono)
                # cambiar_estado_embudo(item_id, "Agendo Presentacion")

            elif tipo_cita == "presencial":
                
                nombreLead = obtener_nombre_item(item_id)
                eliminar_item(item_id)
                agregarShooperPresencial(nombreLead, fecha_formateada, telefono)
                # cambiar_estado_embudo(item_id, "Agendo Visita")

    # Guardar conversación localmente (opcional)
    with open("respuesta.txt", "a", encoding="utf-8") as f:
        f.write(f"Usuario: {mensaje}\n")
        f.write(f"Setter: {respuesta_texto}\n")
        f.write("-" * 60 + "\n")

    return respuesta_texto 







