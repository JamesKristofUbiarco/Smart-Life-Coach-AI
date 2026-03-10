# graph_app.py
import os
import json
from typing import TypedDict, Optional

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage

from schemas import BackendRequest, CoachPlan

load_dotenv()


# -----------------------------
# Estado compartido del grafo
# -----------------------------
class GraphState(TypedDict):
    backend_payload: dict
    prompt_text: Optional[str]
    ai_result: Optional[dict]


# -----------------------------
# Nodo 1: preparar prompt
# -----------------------------
def prepare_prompt(state: GraphState) -> dict:
    payload = BackendRequest(**state["backend_payload"])

    prompt_text = f"""
Genera un plan personalizado para este usuario.

DATOS DEL USUARIO:
{payload.model_dump_json(indent=2)}

REGLAS:
- Responde en español.
- Sé concreto, útil y realista.
- Devuelve estructura exacta del plan.
- No inventes datos que no estén.
- Si falta info crítica, usa next_actions.
"""

    print("\n[LangGraph] Nodo prepare_prompt ejecutado.")
    return {"prompt_text": prompt_text}


# -----------------------------
# Nodo 2: llamar al modelo
# -----------------------------
def call_gemini(state: GraphState) -> dict:
    model = init_chat_model(
        "google_genai:gemini-2.5-flash-lite",
        temperature=0.3,
        timeout=30,
        max_retries=3,
    )

    structured_model = model.with_structured_output(CoachPlan)

    system_prompt = """
Eres un coach digital de objetivos.
Tu tarea es convertir metas del usuario en un plan accionable, seguro y claro.

Debes responder usando exactamente la estructura definida.
"""

    print("[LangGraph] Llamando a Gemini...\n")

    result = structured_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["prompt_text"]),
    ])

    print("[LangGraph] Respuesta recibida de Gemini.")
    return {"ai_result": result.model_dump()}


# -----------------------------
# Construcción del grafo
# -----------------------------
def build_graph():
    graph_builder = StateGraph(GraphState)

    graph_builder.add_node("prepare_prompt", prepare_prompt)
    graph_builder.add_node("call_gemini", call_gemini)

    graph_builder.add_edge(START, "prepare_prompt")
    graph_builder.add_edge("prepare_prompt", "call_gemini")
    graph_builder.add_edge("call_gemini", END)

    return graph_builder.compile()