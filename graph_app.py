from typing import TypedDict, Optional

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from schemas import ChatPayload, RouterDecision, CoachResponse

load_dotenv()


class GraphState(TypedDict):
    backend_payload: dict
    route: Optional[str]
    route_reason: Optional[str]
    last_user_message: Optional[str]
    ai_result: Optional[dict]


def get_router_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=1.0,
        max_retries=2,
    )


def get_planner_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=1.0,
        max_retries=2,
        thinking_level="low",
    )


def get_qa_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=1.0,
        max_retries=2,
    )


def get_fallback_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=1.0,
        max_retries=2,
    )


def extract_last_user_message(state: GraphState):
    payload = ChatPayload(**state["backend_payload"])
    user_messages = [m for m in payload.messages if m.role == "user"]

    if not user_messages:
        raise ValueError("No hay mensajes del usuario en el payload.")

    last_msg = user_messages[-1]
    text_parts = [p.text for p in last_msg.parts if p.type == "text"]
    joined_text = "\n".join(text_parts).strip()

    print(f"[Extractor] Último mensaje usuario: {joined_text}")
    return {"last_user_message": joined_text}


def router_node(state: GraphState):
    payload = ChatPayload(**state["backend_payload"])

    router_prompt = f"""
Clasifica la siguiente petición en UNA de estas rutas:
- planner: si el usuario pide un plan, estrategia, roadmap, rutina o pasos para lograr una meta
- qa: si el usuario hace una duda puntual, seguimiento o aclaración
- fallback: si la petición es ambigua, demasiado general o no encaja

Devuelve solo la estructura solicitada.

SESIÓN:
- session_id: {payload.id}
- trigger: {payload.trigger}
- user_name: {payload.user_name}
- age: {payload.age}

ÚLTIMO MENSAJE:
{state["last_user_message"]}
"""

    model = get_router_model().with_structured_output(
        RouterDecision.model_json_schema(),
        method="json_schema",
    )

    result = model.invoke([
        SystemMessage(content="Eres un router de intenciones para un asistente personal."),
        HumanMessage(content=router_prompt),
    ])

    print(f"[Router] route={result['route']} | reason={result['reason']}")
    return {
        "route": result["route"],
        "route_reason": result["reason"],
    }


def planner_node(state: GraphState):
    payload = ChatPayload(**state["backend_payload"])

    planner_prompt = f"""
Genera un plan accionable, realista y seguro para este usuario.

DATOS:
- user_name: {payload.user_name}
- age: {payload.age}
- session_id: {payload.id}
- trigger: {payload.trigger}

MENSAJE DEL USUARIO:
{state["last_user_message"]}

REGLAS:
- Responde en español.
- Sé concreto.
- Si el usuario pide aprender algo, divide por fases.
- Crea hitos, agenda semanal, riesgos y siguientes acciones.
- response_type = "plan"
- message_for_user debe ser natural, claro y útil.
"""

    model = get_planner_model().with_structured_output(
        CoachResponse.model_json_schema(),
        method="json_schema",
    )

    result = model.invoke([
        SystemMessage(content="Eres un coach digital especializado en planificación de objetivos."),
        HumanMessage(content=planner_prompt),
    ])

    print("[Planner] Plan generado.")
    return {"ai_result": result}


def qa_node(state: GraphState):
    payload = ChatPayload(**state["backend_payload"])

    qa_prompt = f"""
Responde la duda del usuario de forma útil, breve y clara.

DATOS:
- user_name: {payload.user_name}
- age: {payload.age}
- session_id: {payload.id}
- trigger: {payload.trigger}

MENSAJE DEL USUARIO:
{state["last_user_message"]}

REGLAS:
- Responde en español.
- response_type = "answer"
- message_for_user debe responder directamente al usuario.
- No inventes contexto no proporcionado.
"""

    model = get_qa_model().with_structured_output(
        CoachResponse.model_json_schema(),
        method="json_schema",
    )

    result = model.invoke([
        SystemMessage(content="Eres un asistente de seguimiento y preguntas sobre metas y planes."),
        HumanMessage(content=qa_prompt),
    ])

    print("[QA] Respuesta generada.")
    return {"ai_result": result}


def fallback_node(state: GraphState):
    payload = ChatPayload(**state["backend_payload"])

    fallback_prompt = f"""
La petición del usuario es ambigua o demasiado general.

DATOS:
- user_name: {payload.user_name}
- age: {payload.age}
- session_id: {payload.id}
- trigger: {payload.trigger}

MENSAJE DEL USUARIO:
{state["last_user_message"]}

REGLAS:
- Responde en español.
- Explica qué información falta.
- Haz máximo 3 preguntas útiles.
- response_type = "fallback"
- message_for_user debe sonar natural.
"""

    model = get_fallback_model().with_structured_output(
        CoachResponse.model_json_schema(),
        method="json_schema",
    )

    result = model.invoke([
        SystemMessage(content="Eres un asistente que aclara peticiones ambiguas."),
        HumanMessage(content=fallback_prompt),
    ])

    print("[Fallback] Solicitud de aclaración generada.")
    return {"ai_result": result}


def consolidator_node(state: GraphState):
    return {"ai_result": state["ai_result"]}


def route_to_agent(state: GraphState):
    route = state["route"]
    if route == "planner":
        return "planner_node"
    if route == "qa":
        return "qa_node"
    return "fallback_node"


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("extract_last_user_message", extract_last_user_message)
    builder.add_node("router_node", router_node)
    builder.add_node("planner_node", planner_node)
    builder.add_node("qa_node", qa_node)
    builder.add_node("fallback_node", fallback_node)
    builder.add_node("consolidator_node", consolidator_node)

    builder.add_edge(START, "extract_last_user_message")
    builder.add_edge("extract_last_user_message", "router_node")
    builder.add_conditional_edges(
        "router_node",
        route_to_agent,
        {
            "planner_node": "planner_node",
            "qa_node": "qa_node",
            "fallback_node": "fallback_node",
        },
    )
    builder.add_edge("planner_node", "consolidator_node")
    builder.add_edge("qa_node", "consolidator_node")
    builder.add_edge("fallback_node", "consolidator_node")
    builder.add_edge("consolidator_node", END)

    return builder.compile()