import json
from graph_app import build_graph
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from schemas import Message


def main(backend_payload):
    # backend_payload = {
    #     "id": "session-001",
    #     "trigger": "new_message",
    #     "user_name": "Victor",
    #     "age": 22,
    #     "messages": [
    #         {
    #             "id": "msg-001",
    #             "role": "user",
    #             "parts": [
    #                 {
    #                     "type": "text",
    #                     "text": "Hola coach quiero un plan de trabajo para aprender a hacer un full stack para mi clase de ingeniería de software. Somos 5 estudiantes con nociones básicas de programación. ¿Qué necesitamos aprender?"
    #                 }
    #             ]
    #         }
    #     ]
    # }

    print("[Backend] Enviando payload al grafo...\n")

    graph = build_graph()

    result = graph.invoke({
        "backend_payload": backend_payload,
        "route": None,
        "route_reason": None,
        "last_user_message": None,
        "ai_result": None,
    })

    print("\n[Backend] Resultado final:\n")
    return(json.dumps(result["ai_result"], ensure_ascii=False, indent=2))

app = FastAPI()
@app.post("/Chat")
async def generar_respuesta(texto:Message):
    return(main(texto))