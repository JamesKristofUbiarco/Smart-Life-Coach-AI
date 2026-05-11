import os
from typing import TypedDict, Optional, List
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from schemas import ChatPayload
from tools import get_tools

load_dotenv()

def get_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0.7,
        max_retries=2,
    )

def process_chat(payload_dict: dict) -> dict:
    payload = ChatPayload(**payload_dict)
    
    # Extraer mensajes e historial
    langchain_messages = []
    
    # 1. System Prompt basado en Ajustes
    ai_settings = payload.ai_settings or {}
    coach_name = ai_settings.get("nombre", "Smart Life Coach")
    coach_tone = ai_settings.get("tono", "Profesional y motivador")
    
    system_prompt = f"""
    Eres {coach_name}, un asistente personal inteligente y coach de vida.
    Tono: {coach_tone}
    
    Tu objetivo es ayudar al usuario a alcanzar sus metas mediante la creación de planes y tareas.
    Tus herramientas te permiten:
    - Consultar los planes actuales del usuario.
    - Crear un plan nuevo (para metas grandes).
    - Crear tareas dentro de un plan (pasos concretos).
    
    REGLAS:
    1. Si el usuario te pide crear un plan o tarea, USA LAS HERRAMIENTAS correspondientes. NO simules la creación, hazla real.
    2. Cuando uses una herramienta, coméntale al usuario que ya la ejecutaste.
    3. Si el usuario pregunta por sus planes, usa la herramienta para consultarlos.
    4. Responde de manera clara y natural, manteniendo el formato markdown si es necesario.
    """
    
    langchain_messages.append(SystemMessage(content=system_prompt))
    
    # 2. Convertir historial
    for msg in payload.messages:
        text = " ".join([p.text for p in msg.parts if p.type == "text" and p.text is not None])
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=text))
        else:
            langchain_messages.append(AIMessage(content=text))
            
    # Configurar herramientas y agente
    tools = get_tools(payload.token) if payload.token else []
    model = get_model()
    
    # Crear agente ReAct
    agent = create_react_agent(model, tools)
    
    # Ejecutar agente
    print(f"\n[Agent] Invocando agente con {len(langchain_messages)} mensajes...")
    result = agent.invoke({"messages": langchain_messages})
    
    # Extraer la última respuesta del agente
    final_content = result["messages"][-1].content
    
    if isinstance(final_content, list):
        text_blocks = [block.get("text", "") for block in final_content if isinstance(block, dict) and block.get("type") == "text"]
        final_message = "\n".join(text_blocks)
    else:
        final_message = str(final_content)
        
    print(f"[Agent] Respuesta generada:\n{final_message[:100]}...\n")
    
    return {
        "summary": final_message,
        "response_type": "answer",
        "message_for_user": final_message,
    }