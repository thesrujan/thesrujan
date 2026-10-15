from flask import Flask
import os

app = Flask(__name__)


@app.get("/")
def home():
    return "Hello, Jenkins Multi-Stage Pipeline!"


@app.get("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", "18080"))
    app.run(host="127.0.0.1", port=port, debug=False)
