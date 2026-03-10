# Smart-Life-Coach-AI
Te dejo un **README limpio, profesional y listo para GitHub** para tu parte de IA. Está pensado para que cualquiera pueda clonar el repo, instalar dependencias y correr el demo del flujo **Backend → LangGraph → Gemini → Backend**.

Puedes copiarlo directo.

---

# AI Coach Graph (Gemini + LangGraph Demo)

Demo de integración de **LangGraph + LangChain + Google Gemini** para un asistente personal de objetivos.

Este módulo simula el flujo real de una aplicación full-stack donde:

```
Frontend / Backend
        ↓
     FastAPI
        ↓
     LangGraph
        ↓
   Google Gemini
        ↓
     LangGraph
        ↓
     Backend
```

El objetivo es demostrar cómo un backend puede enviar información del usuario a un **grafo de IA**, que genera un plan personalizado usando un modelo LLM.

---

# Arquitectura

```
backend_simulator.py
        │
        ▼
   LangGraph State
        │
        ▼
   prepare_prompt node
        │
        ▼
    call_gemini node
        │
        ▼
      Gemini API
        │
        ▼
   structured output
        │
        ▼
   respuesta al backend
```

---

# Tecnologías usadas

* **Python 3.10+**
* **LangGraph**
* **LangChain**
* **Google Gemini API**
* **Pydantic**
* **dotenv**

---

# Estructura del proyecto

```
ai-coach-graph/
│
├── backend_simulator.py     # Simula el backend enviando datos
├── graph_app.py             # Grafo LangGraph que orquesta la IA
├── schemas.py               # Modelos Pydantic de entrada y salida
├── .env                     # API key
└── README.md
```

---

# Instalación

Clona el repositorio:

```bash
git clone https://github.com/tu_usuario/ai-coach-graph.git
cd ai-coach-graph
```

Instala dependencias:

```bash
pip install -U langgraph langchain langchain-google-genai python-dotenv
```

---

# Configurar API Key

Crea un archivo `.env` en la raíz del proyecto.

```
GOOGLE_API_KEY=tu_api_key_aqui
```

Puedes obtener una API key en:

[https://ai.google.dev/](https://ai.google.dev/)

---

# Ejecutar el demo

Ejecuta:

```bash
python backend_simulator.py
```

Flujo que verás en consola:

```
[Backend] Enviando payload al grafo IA...

[LangGraph] Nodo prepare_prompt ejecutado.
[LangGraph] Llamando a Gemini...

[LangGraph] Respuesta recibida de Gemini.

[Backend] Respuesta final recibida del grafo:
{
   "plan_title": "...",
   "milestones": ...
}
```

---

# Ejemplo de input del backend

El backend envía un objeto JSON al grafo:

```json
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

La IA devuelve un plan estructurado:

```json
{
  "plan_title": "Plan 5K en 8 semanas",
  "summary": "Programa progresivo para correr 5 km",
  "milestones": [
    {
      "week": 2,
      "target": "correr 10 minutos continuos"
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
  ],
  "risks": [
    {
      "risk": "dolor de rodilla",
      "mitigation": "reducir intensidad"
    }
  ],
  "next_actions": [
    "Confirmar acceso a pista"
  ]
}
```

---

# Cómo funciona el grafo

LangGraph usa un **StateGraph** donde cada nodo procesa el estado compartido.

```
StateGraph
   │
   ├── prepare_prompt
   │
   └── call_gemini
```

### Nodo 1

Prepara el prompt a partir de los datos enviados por el backend.

### Nodo 2

Llama al modelo Gemini usando LangChain y genera la respuesta estructurada.

---

# Ventajas de este enfoque

✔ separación clara entre backend e IA
✔ fácil escalar a agentes más complejos
✔ salida estructurada validada con Pydantic
✔ integración simple con FastAPI

---

# Próximos pasos

Este demo puede evolucionar hacia:

* integración con **FastAPI**
* memoria de usuario con **Supabase**
* almacenamiento de planes
* soporte **voz / imagen**
* agentes más complejos con **LangGraph**

---

# Licencia

MIT License
