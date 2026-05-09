import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph_app import process_chat
from schemas import ChatPayload

app = FastAPI()

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
        print("[Backend] Procesando chat con Agente ReAct...\n")

        coach_response_dict = process_chat(payload.model_dump())

        print("\n[Backend] Resultado final enviado al backend principal:\n")
        
        return {
            "status": "success",
            "session_id": payload.id,
            "coach_response": coach_response_dict,
            # Campos legacy para mantener compatibilidad
            "route_used": "agent",
            "route_reason": "agent process",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))