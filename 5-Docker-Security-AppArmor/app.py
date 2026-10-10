from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def home():
    return "Hello, this is a secure Flask application running inside a Docker container!"


@app.get("/health")
def health():
    return jsonify(status="healthy")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
