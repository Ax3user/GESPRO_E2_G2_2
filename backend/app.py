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


if __name__ == "__main__":
    app.run(debug=True)
