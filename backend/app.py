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
# Datos iniciales (puedes dejarlos o vaciarlos)
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
        "assignees": []
    },
    {
        "id": 2,
        "title": "Configurar backend mínimo en Python",
        "status": "IN_PROGRESS",
        "estimate_min": 45,
        "started_at": now_sec(),
        "completed_at": None,
        "actual_sec": None,
        "assignees": []
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

# ---------------------------
# Participantes predefinidos
# ---------------------------
participants.extend([
    {"id": 1, "name": "Carlos", "role": "product_owner"},
    {"id": 2, "name": "Emmanuel", "role": "member"},
    {"id": 3, "name": "Áxel", "role": "visualizer"},
])
next_participant_id = 4



# ---------------------------
# Health
# ---------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", message="Backend running", tasks_count=len(tasks))


# ---------------------------
# Tasks
# ---------------------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_task_id   # 👈 MOVER ARRIBA

    user = get_user()
    if not user or not is_po(user):
        return jsonify(error="Solo Product Owner puede crear tareas"),403

    data = request.get_json()
    title = data.get("title","").strip()
    if not title:
        return jsonify(error="Título vacío"),400

    t = {
        "id": next_task_id,
        "title": title,
        "status":"TODO",
        "estimate_min":0,
        "started_at":None,
        "completed_at":None,
        "actual_sec":None,
        "assignees":[]
    }

    tasks.append(t)
    next_task_id += 1   # 👈 ahora sí es válido

    return jsonify(t),201



@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id: int):
    data = request.get_json(silent=True) or {}

    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify(error="Tarea no encontrada"), 404

    # Update title
    if "title" in data:
        title = str(data.get("title", "")).strip()
        if not title:
            return jsonify(error="El título no puede estar vacío"), 400
        task["title"] = title

    # Update estimate
    if "estimate_min" in data:
        try:
            est = int(data.get("estimate_min"))
            if est < 0:
                return jsonify(error="El tiempo estimado no puede ser negativo"), 400
            task["estimate_min"] = est
        except Exception:
            return jsonify(error="El tiempo estimado debe ser un entero (minutos)"), 400

    # Assignment (by name)
    if "add_assignee" in data:
        name = str(data.get("add_assignee", "")).strip()
        if not name:
            return jsonify(error="Nombre de participante inválido"), 400
        if "assignees" not in task or task["assignees"] is None:
            task["assignees"] = []
        if name not in task["assignees"]:
            task["assignees"].append(name)

    if "remove_assignee" in data:
        name = str(data.get("remove_assignee", "")).strip()
        if "assignees" in task and name in task["assignees"]:
            task["assignees"].remove(name)

    # Update status (drag & drop lanes)
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


# ---------------------------
# Participants
# ---------------------------
@app.route("/participants", methods=["GET"])
def get_participants():
    return jsonify(participants)


@app.route("/participants", methods=["POST"])
def create_participant():
    global next_participant_id

    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="JSON requerido"), 400

    name = str(data.get("name", "")).strip()
    role = str(data.get("role", "member")).strip().lower()

    if not name:
        return jsonify(error="El nombre no puede estar vacío"), 400
    # Solo permitimos crear nuevos participantes como member o visualizer
    if role not in ["member", "visualizer"]:
        return jsonify(error="Solo se pueden agregar participantes como member o visualizer"), 400

    p = {"id": next_participant_id, "name": name, "role": role}
    participants.append(p)
    next_participant_id += 1
    return jsonify(p), 201

@app.route("/participants/<int:pid>", methods=["PATCH"])
def update_participant(pid: int):
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
        # No permitimos asignar product_owner por edición (solo los predefinidos)
        if role not in ["member", "visualizer", "product_owner"]:
            return jsonify(error="Rol inválido"), 400
        if role == "product_owner":
            return jsonify(error="No se puede asignar product_owner a nuevos participantes"), 400
        p["role"] = role

    return jsonify(p), 200


@app.route("/participants/<int:pid>", methods=["DELETE"])
def delete_participant(pid: int):
    global participants
    before = len(participants)
    participants = [x for x in participants if x["id"] != pid]
    if len(participants) == before:
        return jsonify(error="Participante no encontrado"), 404
    return jsonify(ok=True), 200


if __name__ == "__main__":
    app.run(debug=True)