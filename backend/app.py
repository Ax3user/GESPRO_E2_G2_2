from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------------
# Persistencia en memoria
# ---------------------------
tasks = []
next_id = 1

# Tareas iniciales
tasks.extend([
    {"id": 1, "title": "Crear estructura base del repositorio", "status": "DONE"},
    {"id": 2, "title": "Configurar backend mínimo en Python", "status": "IN_PROGRESS"},
    {"id": 3, "title": "Crear endpoint de prueba (/health)", "status": "TODO"},
])
next_id = 4


@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", message="Backend running", tasks_count=len(tasks))


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id

    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="JSON requerido"), 400

    title = str(data.get("title", "")).strip()
    status = str(data.get("status", "TODO")).strip().upper()

    if not title:
        return jsonify(error="El título no puede estar vacío"), 400

    if status not in ["TODO", "IN_PROGRESS", "DONE"]:
        return jsonify(error="Estado inválido"), 400

    new_task = {"id": next_id, "title": title, "status": status}
    tasks.append(new_task)
    next_id += 1
    return jsonify(new_task), 201


# ✅ NUEVO: actualizar estado (para drag & drop)
@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id: int):
    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).strip().upper()

    if status not in ["TODO", "IN_PROGRESS", "DONE"]:
        return jsonify(error="Estado inválido"), 400

    for t in tasks:
        if t["id"] == task_id:
            t["status"] = status
            return jsonify(t), 200

    return jsonify(error="Tarea no encontrada"), 404


if __name__ == "__main__":
    app.run(debug=True)
