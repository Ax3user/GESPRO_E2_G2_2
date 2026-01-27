from flask import Flask

app = Flask(__name__)

@app.route("/")
def root():
    return "Backend OK"

if __name__ == "__main__":
    app.run(debug=True)
