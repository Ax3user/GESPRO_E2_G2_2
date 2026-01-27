from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # permite fetch desde el HTML

# ---------------------------
# Persistencia en memoria
# ---------------------------
tasks = []
next_id = 1

# Tareas iniciales (puedes cambiarlas o borrar esta sección si quieres empezar vacío)
tasks.extend([
    {"id": 1, "title": "Crear estructura base del repositorio", "status": "DONE", "assigned": ""},
    {"id": 2, "title": "Configurar backend mínimo en Python", "status": "IN_PROGRESS", "assigned": ""},
    {"id": 3, "title": "Crear endpoint de prueba (/health)", "status": "TODO", "assigned": ""},
])
next_id = 4


# ---------------------------
# Endpoint de prueba (/health)
# ---------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend running",
        "tasks_count": len(tasks)
    })


# ---------------------------
# Listar tareas (GET /tasks)
# ---------------------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


# ---------------------------
# Crear tarea (POST /tasks) + Validaciones básicas
# Body esperado: {"title":"...", "status":"TODO|IN_PROGRESS|DONE", "assigned":"(opcional)"}
# ---------------------------
@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Body JSON requerido. Ejemplo: {'title':'Mi tarea'}"}), 400

    title = str(data.get("title", "")).strip()
    status = str(data.get("status", "TODO")).strip().upper()
    assigned = str(data.get("assigned", "")).strip()

    # Validación: título no vacío
    if not title:
        return jsonify({"error": "El título no puede estar vacío."}), 400

    # Validación: estado permitido
    allowed_status = {"TODO", "IN_PROGRESS", "DONE"}
    if status not in allowed_status:
        return jsonify({"error": f"Estado inválido. Usa uno de: {sorted(list(allowed_status))}"}), 400

    new_task = {
        "id": next_id,
        "title": title,
        "status": status,
        "assigned": assigned
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


# (Opcional) raíz informativa
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "GESPRO Task Manager API",
        "health": "/health",
        "tasks": "/tasks"
    })


if __name__ == "__main__":
    app.run(debug=True)
