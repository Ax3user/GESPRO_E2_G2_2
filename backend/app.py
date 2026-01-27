from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tasks = []
next_id = 1

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
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    status = str(data.get("status", "TODO")).strip().upper()

    new_task = {"id": next_id, "title": title, "status": status}
    tasks.append(new_task)
    next_id += 1
    return jsonify(new_task), 201

if __name__ == "__main__":
    app.run(debug=True)
