from flask import Flask

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", message="Backend running")

if __name__ == "__main__":
    app.run(debug=True)
