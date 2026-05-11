import requests
from langchain_core.tools import tool

FASTAPI_URL = "http://localhost:8000"

def get_tools(token: str):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    @tool
    def create_plan(title: str, description: str, due_date: str = None) -> str:
        """Crea un nuevo Plan principal (meta) para el usuario. Úsalo cuando el usuario quiera lograr un objetivo grande."""
        print(f"[Tool] Creando plan: {title}")
        payload = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "parent_id": None
        }
        try:
            res = requests.post(f"{FASTAPI_URL}/api/planes", json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return f"Plan '{title}' creado exitosamente. ID: {data.get('id')}"
            return f"Error al crear plan: {res.text}"
        except Exception as e:
            return f"Excepción al crear plan: {e}"

    @tool
    def create_task(plan_id: str, title: str, description: str, due_date: str = None) -> str:
        """Crea una nueva Tarea asignada a un Plan existente. Úsalo para desglosar un plan en pasos accionables."""
        print(f"[Tool] Creando tarea: {title} para plan {plan_id}")
        payload = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "parent_id": plan_id
        }
        try:
            res = requests.post(f"{FASTAPI_URL}/api/planes", json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return f"Tarea '{title}' creada exitosamente."
            return f"Error al crear tarea: {res.text}"
        except Exception as e:
            return f"Excepción al crear tarea: {e}"

    @tool
    def get_current_plans() -> str:
        """Obtiene la lista actual de planes y tareas del usuario. Útil para saber qué planes tiene pendientes antes de crear una tarea."""
        print(f"[Tool] Obteniendo planes actuales...")
        try:
            res = requests.get(f"{FASTAPI_URL}/api/planes", headers=headers)
            if res.status_code == 200:
                import json
                return json.dumps(res.json(), ensure_ascii=False)
            return f"Error al obtener planes: {res.text}"
        except Exception as e:
            return f"Excepción al obtener planes: {e}"

    return [create_plan, create_task, get_current_plans]
