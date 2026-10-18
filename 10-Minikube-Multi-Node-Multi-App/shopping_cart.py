from flask import Flask, jsonify, request

app = Flask(__name__)
cart = []


@app.route("/cart", methods=["GET"])
def get_cart():
    return jsonify(cart)


@app.route("/cart", methods=["POST"])
def add_to_cart():
    item = request.get_json(silent=True)
    if not isinstance(item, dict):
        return jsonify({"error": "Send a JSON object in the request body"}), 400
    cart.append(item)
    return jsonify(cart), 201


@app.route("/health", methods=["GET"])
def health():
    return {"status": "healthy", "app": "shopping-cart"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
