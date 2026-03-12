# backend_simulator.py
import json
from graph_app import build_graph


def main():
    # Simula lo que enviaría el backend
    backend_payload = {
        "user_profile": {
            "name": "Victor",
            "language": "es",
            "timezone": "America/Mexico_City",
            "constraints": ["30 min al día", "sin gimnasio"]
        },
        "goal": {
            "title": "Correr 5K",
            "category": "deportivo",
            "deadline": "2026-05-30",
            "priority": "alta"
        },
        "current_state": {
            "level": "principiante",
            "habits": ["camina 2 veces por semana"],
            "issues": ["molestia leve en rodilla"]
        },
        "user_message": "Hazme un plan de 8 semanas sin lesionarme."
    }

    print("\n[Backend] Enviando payload al grafo IA...\n")
    app = build_graph()

    final_state = app.invoke({
        "backend_payload": backend_payload,
        "prompt_text": None,
        "ai_result": None,
    })

    print("\n[Backend] Respuesta final recibida del grafo:\n")
    print(json.dumps(final_state["ai_result"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()