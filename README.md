# Smart-Life-Coach-AI (LangGraph + Gemini Multi-Agent)

Prototipo del componente de **Inteligencia Artificial** para el proyecto **Smart Life Coach**.

Este módulo implementa un **grafo de estado con LangGraph** que permite enrutar solicitudes del usuario hacia distintos **agentes especializados**, utilizando modelos **Google Gemini** a través de la integración oficial `langchain-google-genai`.

El objetivo es demostrar cómo un backend puede enviar información de usuario y metas a un sistema de IA capaz de:

- clasificar la intención del usuario
- seleccionar el agente adecuado
- generar una respuesta estructurada
- devolver el resultado al backend

## .env

1. Copiar el archivo .env.template en un .env
2. La GOOGLE_API_KEY= se genera en aistudio.google.com

## Correr en entorno virtual con uv y uvicorn

```bash
uv venv .venv --python 3.13.5
```

```bash
source .venv/bin/activate
```

```bash
uv pip install -r requirements.txt
```

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

# Arquitectura general

El flujo del sistema sigue el siguiente pipeline:

```
Backend
   ↓
LangGraph State
   ↓
Router (clasificación de intención)
   ↓
[planner_agent | qa_agent | fallback_agent]
   ↓
Consolidator
   ↓
Backend response
```

---

# Flujo completo del sistema

```
backend_simulator.py
        │
        ▼
     LangGraph
        │
        ▼
      Router
        │
        ▼
  ┌───────────────┬─────────────┬──────────────┐
  │               │             │              │
planner_agent   qa_agent   fallback_agent
  │               │             │
  └───────────────┴─────────────┴──────────────┘
                │
                ▼
           Consolidator
                │
                ▼
            Backend
```

---

# Agentes del sistema

| Agente             | Función                                         | Modelo         |
| ------------------ | ----------------------------------------------- | -------------- |
| **Router**         | Clasifica la intención del usuario              | gemini-3-flash |
| **Planner Agent**  | Genera planes, estrategias y pasos para metas   | gemini-3-flash |
| **QA Agent**       | Responde dudas o preguntas sobre metas o planes | gemini-3-flash |
| **Fallback Agent** | Maneja peticiones ambiguas o incompletas        | gemini-3-flash |
| **Consolidator**   | Estandariza la salida al backend                | N/A            |

---

# Tecnologías usadas

- Python 3.10+
- LangGraph
- LangChain Google Integration
- Google Gemini (AI Studio API)
- Pydantic
- python-dotenv

---

# Estructura del proyecto

```
AI-component/
│
├── backend_simulator.py   # Simula el backend enviando datos al grafo
├── graph_app.py           # Grafo LangGraph con router y agentes
├── schemas.py             # Modelos Pydantic de entrada y salida
├── .env                   # API key de Google
├── README.md
```

---

# Instalación

Clonar el repositorio:

```
git clone https://github.com/tu_usuario/smart-life-coach-ai.git
cd smart-life-coach-ai/AI-component
```

Instalar dependencias:

```
pip install -U langgraph langchain-google-genai python-dotenv pydantic
```

---

# Configurar API Key

Crear un archivo `.env` en la raíz del proyecto:

```
GOOGLE_API_KEY=tu_api_key_aqui
```

Puedes obtener una API key en:

[https://ai.google.dev/](https://ai.google.dev/)

---

# Ejecutar el prototipo

Desde la terminal:

```
python backend_simulator.py
```

---

# Salida esperada en consola

```
[Backend] Enviando payload al grafo...

[Router] route=planner | reason=El usuario solicita un plan

[Planner] Generando plan con Gemini...

[Backend] Resultado final:

{
  "response_type": "plan",
  "plan_title": "Plan para correr 5K en 8 semanas",
  "summary": "...",
  "milestones": [...],
  "weekly_schedule": [...],
  "risks": [...],
  "next_actions": [...]
}
```

---

# Ejemplo de input del backend

```
{
  "user_profile": {
    "name": "Victor",
    "constraints": ["30 min al día", "sin gimnasio"]
  },
  "goal": {
    "title": "Correr 5K",
    "deadline": "2026-05-30"
  },
  "current_state": {
    "level": "principiante"
  },
  "user_message": "Hazme un plan de 8 semanas"
}
```

---

# Ejemplo de output generado

```
{
  "response_type": "plan",
  "plan_title": "Plan para correr 5K en 8 semanas",
  "summary": "Programa progresivo para mejorar resistencia",
  "milestones": [
    {
      "week": 2,
      "target": "Correr 10 minutos continuos"
    }
  ],
  "weekly_schedule": [
    {
      "week": 1,
      "sessions": [
        {
          "day": "Lunes",
          "task": "intervalos caminar/trotar",
          "duration_min": 30
        }
      ]
    }
  ]
}
```

---

# Diferencias con la versión anterior

Versión anterior:

```
Backend → LangGraph → Gemini → Backend
```

Nueva versión:

```
Backend → Router → Agente especializado → Consolidator → Backend
```

Esto permite:

- mayor modularidad
- mejor control del contexto
- agentes especializados
- arquitectura escalable

---

# Ventajas de esta arquitectura

✔ separación clara entre backend e IA
✔ selección dinámica de agente según intención
✔ respuestas estructuradas con Pydantic
✔ integración directa con Google AI Studio
✔ base para sistemas multi-agente

---

# Próximos pasos

Posibles mejoras del sistema:

- integración con **FastAPI**
- memoria de usuario
- historial de conversaciones
- embeddings + base vectorial
- agentes adicionales (nutrición, estudio, deporte)
- soporte multimodal (imagen, audio)

---

# Licencia

MIT Lice
