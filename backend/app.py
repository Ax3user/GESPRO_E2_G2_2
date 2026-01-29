from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# ---------------------------
# Persistencia en memoria
# ---------------------------
tasks = []
next_id = 1

# Tareas iniciales (con estimate_min y sin tiempos aún)
tasks.extend([
    {"id": 1, "title": "Crear estructura base del repositorio", "status": "DONE", "estimate_min": 30, "started_at": None, "completed_at": None, "actual_sec": None},
    {"id": 2, "title": "Configurar backend mínimo en Python", "status": "IN_PROGRESS", "estimate_min": 45, "started_at": int(time.time()), "completed_at": None, "actual_sec": None},
    {"id": 3, "title": "Crear endpoint de prueba (/health)", "status": "TODO", "estimate_min": 20, "started_at": None, "completed_at": None, "actual_sec": None},
])
next_id = 4


def now_sec() -> int:
    return int(time.time())


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
    estimate_min = data.get("estimate_min", 0)

    if not title:
        return jsonify(error="El título no puede estar vacío"), 400

    if status not in ["TODO", "IN_PROGRESS", "DONE"]:
        return jsonify(error="Estado inválido"), 400

    # Validación simple del estimado
    try:
        estimate_min = int(estimate_min)
        if estimate_min < 0:
            return jsonify(error="El tiempo estimado no puede ser negativo"), 400
    except Exception:
        return jsonify(error="El tiempo estimado debe ser un número entero (minutos)"), 400

    t = {
        "id": next_id,
        "title": title,
        "status": status,
        "estimate_min": estimate_min,
        "started_at": None,      # epoch seconds
        "completed_at": None,    # epoch seconds
        "actual_sec": None       # int seconds
    }

    # Si se crea directamente en IN_PROGRESS o DONE, se setean tiempos coherentes
    if status == "IN_PROGRESS":
        t["started_at"] = now_sec()
    elif status == "DONE":
        # Si la marcan DONE desde inicio, consideramos 0 segundos reales
        t["started_at"] = now_sec()
        t["completed_at"] = now_sec()
        t["actual_sec"] = 0

    tasks.append(t)
    next_id += 1
    return jsonify(t), 201


# ✅ Update parcial: status / estimate_min / title (si quieres)
# En especial: cuando status pasa a IN_PROGRESS arranca cronómetro;
# cuando pasa a DONE calcula tiempo real vs estimado.
@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id: int):
    data = request.get_json(silent=True) or {}

    # Buscar tarea
    task = None
    for t in tasks:
        if t["id"] == task_id:
            task = t
            break
    if not task:
        return jsonify(error="Tarea no encontrada"), 404

    # Actualizar título (opcional)
    if "title" in data:
        title = str(data.get("title", "")).strip()
        if not title:
            return jsonify(error="El título no puede estar vacío"), 400
        task["title"] = title

    # Actualizar estimado (opcional)
    if "estimate_min" in data:
        try:
            est = int(data.get("estimate_min"))
            if est < 0:
                return jsonify(error="El tiempo estimado no puede ser negativo"), 400
            task["estimate_min"] = est
        except Exception:
            return jsonify(error="El tiempo estimado debe ser un número entero (minutos)"), 400

    # Actualizar status (lo usa el drag & drop)
    if "status" in data:
        status = str(data.get("status", "")).strip().upper()
        if status not in ["TODO", "IN_PROGRESS", "DONE"]:
            return jsonify(error="Estado inválido"), 400

        prev = task["status"]
        task["status"] = status

        # Lógica de tiempos
        if status == "IN_PROGRESS":
            # Si entra a IN_PROGRESS por primera vez, arranca
            if task["started_at"] is None:
                task["started_at"] = now_sec()
            # Si venía de DONE y lo regresan (raro), limpiamos completed/actual
            if prev == "DONE":
                task["completed_at"] = None
                task["actual_sec"] = None

        elif status == "DONE":
            # Si no tenía start, lo arrancamos en ese momento
            if task["started_at"] is None:
                task["started_at"] = now_sec()
            task["completed_at"] = now_sec()
            task["actual_sec"] = max(0, task["completed_at"] - task["started_at"])

        elif status == "TODO":
            # Si la regresan a TODO, detenemos “finalización”
            task["completed_at"] = None
            task["actual_sec"] = None

    return jsonify(task), 200


if __name__ == "__main__":
    app.run(debug=True)
