from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tasks = []
next_id = 1

@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", message="Backend running", tasks_count=len(tasks))

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


if __name__ == "__main__":
    app.run(debug=True)
