import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph_app import build_graph
from schemas import ChatPayload

app = FastAPI()
graph = build_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "AI-component running"}


@app.post("/chat")
async def generar_respuesta(payload: ChatPayload):
    try:
        print("[Backend] Enviando payload al grafo...\n")

        result = graph.invoke({
            "backend_payload": payload.model_dump(),
            "route": None,
            "route_reason": None,
            "last_user_message": None,
            "ai_result": None,
        })

        print("\n[Backend] Resultado final:\n")
        print(json.dumps(result["ai_result"], ensure_ascii=False, indent=2))

        return {
            "status": "success",
            "session_id": payload.id,
            "route_used": result["route"],
            "route_reason": result["route_reason"],
            "coach_response": result["ai_result"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))