import os
from typing import TypedDict, Optional

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from schemas import BackendRequest, RouterDecision, CoachResponse

load_dotenv()


class GraphState(TypedDict):
    backend_payload: dict
    route: Optional[str]
    route_reason: Optional[str]
    prompt_text: Optional[str]
    ai_result: Optional[dict]


def get_router_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=1.0,   # Gemini 3+ recomienda 1.0 por defecto
        max_retries=2,
    )


def get_planner_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview",
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


def router_node(state: GraphState):
    payload = BackendRequest(**state["backend_payload"])

    router_prompt = f"""
Clasifica la siguiente petición en UNA de estas rutas:
- planner: si el usuario pide un plan, estrategia, roadmap, rutina o pasos para lograr una meta
- qa: si el usuario hace una duda puntual, seguimiento o aclaración
- fallback: si la petición es ambigua, demasiado general o no encaja

Devuelve solo la estructura solicitada.

PETICIÓN:
{payload.model_dump_json(indent=2)}
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
    payload = BackendRequest(**state["backend_payload"])

    planner_prompt = f"""
Genera un plan accionable, realista y seguro para este usuario.

DATOS:
{payload.model_dump_json(indent=2)}

REGLAS:
- Responde en español.
- Sé concreto.
- Crea hitos, agenda semanal, riesgos y siguientes acciones.
- Si falta información crítica, usa next_actions.
- response_type = "plan"
"""

    model = get_planner_model().with_structured_output(
        CoachResponse.model_json_schema(),
        method="json_schema",
    )

    result = model.invoke([
        SystemMessage(content="Eres un coach digital especializado en planificación de objetivos."),
        HumanMessage(content=planner_prompt),
    ])

    return {"ai_result": result}


def qa_node(state: GraphState):
    payload = BackendRequest(**state["backend_payload"])

    qa_prompt = f"""
Responde la duda del usuario de forma útil, breve y clara.

DATOS:
{payload.model_dump_json(indent=2)}

REGLAS:
- Responde en español.
- Si no hay suficiente contexto, dilo claramente.
- response_type = "answer"
- No inventes historial no proporcionado.
"""

    model = get_qa_model().with_structured_output(
        CoachResponse.model_json_schema(),
        method="json_schema",
    )

    result = model.invoke([
        SystemMessage(content="Eres un asistente de seguimiento y preguntas sobre metas y planes."),
        HumanMessage(content=qa_prompt),
    ])

    return {"ai_result": result}


def fallback_node(state: GraphState):
    payload = BackendRequest(**state["backend_payload"])

    fallback_prompt = f"""
La petición del usuario es ambigua o demasiado general.

DATOS:
{payload.model_dump_json(indent=2)}

REGLAS:
- Responde en español.
- Explica qué información falta.
- Haz máximo 3 preguntas útiles.
- response_type = "fallback"
"""

    model = get_fallback_model().with_structured_output(
        CoachResponse.model_json_schema(),
        method="json_schema",
    )

    result = model.invoke([
        SystemMessage(content="Eres un asistente que aclara peticiones ambiguas."),
        HumanMessage(content=fallback_prompt),
    ])

    return {"ai_result": result}


def consolidator_node(state: GraphState):
    # En este MVP solo regresa lo que ya produjo el agente.
    # Aquí luego puedes agregar logs, métricas o formato adicional.
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

    builder.add_node("router_node", router_node)
    builder.add_node("planner_node", planner_node)
    builder.add_node("qa_node", qa_node)
    builder.add_node("fallback_node", fallback_node)
    builder.add_node("consolidator_node", consolidator_node)

    builder.add_edge(START, "router_node")
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