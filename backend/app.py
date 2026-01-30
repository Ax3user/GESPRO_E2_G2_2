from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

VALID_STATUSES = ["TODO", "IN_PROGRESS", "DONE"]
VALID_ROLES = ["product_owner", "member", "visualizer"]

# ---------------------------
# Persistencia en memoria
# ---------------------------
tasks = []
participants = []
next_task_id = 1
next_participant_id = 1

def now_sec() -> int:
    return int(time.time())

# ---------------------------
# Datos iniciales
# ---------------------------
tasks.extend([
    {
        "id": 1,
        "title": "Crear estructura base del repositorio",
        "status": "DONE",
        "estimate_min": 30,
        "started_at": None,
        "completed_at": None,
        "actual_sec": 0,
        "assignees": ["Emmanuel"]
    },
    {
        "id": 2,
        "title": "Configurar backend mínimo en Python",
        "status": "IN_PROGRESS",
        "estimate_min": 45,
        "started_at": now_sec(),
        "completed_at": None,
        "actual_sec": None,
        "assignees": ["Emmanuel"]
    },
    {
        "id": 3,
        "title": "Crear endpoint de prueba (/health)",
        "status": "TODO",
        "estimate_min": 20,
        "started_at": None,
        "completed_at": None,
        "actual_sec": None,
        "assignees": []
    }
])
next_task_id = 4

participants.extend([
    {"id": 1, "name": "Carlos", "role": "product_owner"},
    {"id": 2, "name": "Emmanuel", "role": "member"},
    {"id": 3, "name": "Áxel", "role": "visualizer"},
])
next_participant_id = 4

# ---------------------------
# Auth helpers (simple)
# ---------------------------
def current_user():
    """
    Para simplificar: el frontend manda un header:
      X-User: "Carlos"
    """
    name = (request.headers.get("X-User") or "").strip()
    if not name:
        return None
    return next((p for p in participants if p["name"] == name), None)

def require_user():
    u = current_user()
    if not u:
        return None, (jsonify(error="Falta X-User (sesión no iniciada)"), 401)
    return u, None

def is_po(u): return u and u["role"] == "product_owner"
def is_member(u): return u and u["role"] == "member"
def is_visualizer(u): return u and u["role"] == "visualizer"

def find_task(task_id: int):
    return next((t for t in tasks if t["id"] == task_id), None)

def member_can_touch_task(u, task):
    # Member solo puede tocar tareas donde esté asignado
    return u and task and (u["name"] in (task.get("assignees") or []))

# ---------------------------
# Health
# ---------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", message="Backend running", tasks_count=len(tasks))

# ---------------------------
# Participants (GET libre para login, mutaciones solo PO)
# ---------------------------
@app.route("/participants", methods=["GET"])
def get_participants():
    return jsonify(participants)

@app.route("/participants", methods=["POST"])
def create_participant():
    u, err = require_user()
    if err: return err

    if not is_po(u):
        return jsonify(error="Solo Product Owner puede agregar participantes"), 403

    global next_participant_id

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    role = str(data.get("role", "member")).strip().lower()

    if not name:
        return jsonify(error="El nombre no puede estar vacío"), 400
    if role not in ["member", "visualizer"]:
        return jsonify(error="Solo se pueden agregar participantes como member o visualizer"), 400

    p = {"id": next_participant_id, "name": name, "role": role}
    participants.append(p)
    next_participant_id += 1
    return jsonify(p), 201

@app.route("/participants/<int:pid>", methods=["PATCH"])
def update_participant(pid: int):
    u, err = require_user()
    if err: return err

    if not is_po(u):
        return jsonify(error="Solo Product Owner puede editar participantes"), 403

    data = request.get_json(silent=True) or {}
    p = next((x for x in participants if x["id"] == pid), None)
    if not p:
        return jsonify(error="Participante no encontrado"), 404

    if "name" in data:
        name = str(data.get("name", "")).strip()
        if not name:
            return jsonify(error="El nombre no puede estar vacío"), 400
        p["name"] = name

    if "role" in data:
        role = str(data.get("role", "")).strip().lower()
        if role not in ["member", "visualizer", "product_owner"]:
            return jsonify(error="Rol inválido"), 400
        if p["role"] == "product_owner":
            return jsonify(error="No se puede cambiar el rol del Product Owner"), 400
        if role == "product_owner":
            return jsonify(error="No se puede asignar product_owner a nuevos participantes"), 400
        p["role"] = role

    return jsonify(p), 200

@app.route("/participants/<int:pid>", methods=["DELETE"])
def delete_participant(pid: int):
    u, err = require_user()
    if err: return err

    if not is_po(u):
        return jsonify(error="Solo Product Owner puede eliminar participantes"), 403

    global participants
    before = len(participants)
    participants = [x for x in participants if x["id"] != pid]
    if len(participants) == before:
        return jsonify(error="Participante no encontrado"), 404
    return jsonify(ok=True), 200

# ---------------------------
# Tasks (GET libre, mutaciones con permisos)
# ---------------------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def create_task():
    u, err = require_user()
    if err: return err

    if not is_po(u):
        return jsonify(error="Solo Product Owner puede crear tareas"), 403

    global next_task_id

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    status = str(data.get("status", "TODO")).strip().upper()
    estimate_min = data.get("estimate_min", 0)

    if not title:
        return jsonify(error="El título no puede estar vacío"), 400
    if status not in VALID_STATUSES:
        return jsonify(error="Estado inválido"), 400

    try:
        estimate_min = int(estimate_min)
        if estimate_min < 0:
            return jsonify(error="El tiempo estimado no puede ser negativo"), 400
    except Exception:
        return jsonify(error="El tiempo estimado debe ser un entero (minutos)"), 400

    t = {
        "id": next_task_id,
        "title": title,
        "status": status,
        "estimate_min": estimate_min,
        "started_at": None,
        "completed_at": None,
        "actual_sec": None,
        "assignees": []
    }

    # tiempos
    if status == "IN_PROGRESS":
        t["started_at"] = now_sec()
    elif status == "DONE":
        t["started_at"] = now_sec()
        t["completed_at"] = now_sec()
        t["actual_sec"] = 0

    tasks.append(t)
    next_task_id += 1
    return jsonify(t), 201

@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id: int):
    u, err = require_user()
    if err: return err

    task = find_task(task_id)
    if not task:
        return jsonify(error="Tarea no encontrada"), 404

    # Visualizer: nada
    if is_visualizer(u):
        return jsonify(error="Visualizador: solo lectura"), 403

    # Member: solo sus tareas
    if is_member(u) and not member_can_touch_task(u, task):
        return jsonify(error="Member: solo puedes modificar tus tareas asignadas"), 403

    data = request.get_json(silent=True) or {}

    # ---- Reglas de permisos finas ----
    # Member NO puede asignar/quitar assignees
    if is_member(u):
        if "add_assignee" in data or "remove_assignee" in data:
            return jsonify(error="Member: no puedes asignar/quitar participantes"), 403

    # Asignación: SOLO PO
    if "add_assignee" in data:
        if not is_po(u):
            return jsonify(error="Solo Product Owner puede asignar tareas"), 403
        name = str(data.get("add_assignee", "")).strip()
        if not name:
            return jsonify(error="Nombre de participante inválido"), 400
        if name not in [p["name"] for p in participants]:
            return jsonify(error="Participante no existe"), 400
        task.setdefault("assignees", [])
        if name not in task["assignees"]:
            task["assignees"].append(name)

    if "remove_assignee" in data:
        if not is_po(u):
            return jsonify(error="Solo Product Owner puede quitar asignaciones"), 403
        name = str(data.get("remove_assignee", "")).strip()
        if "assignees" in task and name in task["assignees"]:
            task["assignees"].remove(name)

    # Title (PO o Member si es su tarea)
    if "title" in data:
        title = str(data.get("title", "")).strip()
        if not title:
            return jsonify(error="El título no puede estar vacío"), 400
        task["title"] = title

    # Estimate (PO o Member si es su tarea)
    if "estimate_min" in data:
        try:
            est = int(data.get("estimate_min"))
            if est < 0:
                return jsonify(error="El tiempo estimado no puede ser negativo"), 400
            task["estimate_min"] = est
        except Exception:
            return jsonify(error="El tiempo estimado debe ser un entero (minutos)"), 400

    # Status (PO o Member si es su tarea)
    if "status" in data:
        status = str(data.get("status", "")).strip().upper()
        if status not in VALID_STATUSES:
            return jsonify(error="Estado inválido"), 400

        prev = task["status"]
        task["status"] = status

        if status == "IN_PROGRESS":
            if task["started_at"] is None:
                task["started_at"] = now_sec()
            if prev == "DONE":
                task["completed_at"] = None
                task["actual_sec"] = None

        elif status == "DONE":
            if task["started_at"] is None:
                task["started_at"] = now_sec()
            task["completed_at"] = now_sec()
            task["actual_sec"] = max(0, task["completed_at"] - task["started_at"])

        elif status == "TODO":
            task["completed_at"] = None
            task["actual_sec"] = None

    return jsonify(task), 200

if __name__ == "__main__":
    app.run(debug=True)