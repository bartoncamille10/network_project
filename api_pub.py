from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/account/<int:account>/exists", methods=["GET"])
def account_exists(account):
    # test SANS interroger de base de données
    if account == 708273:
        return jsonify({}), 200  # Le compte existe
    return jsonify({"error": "Le compte n'existe pas."}), 404

@app.route("/currency/<string:currency>/allowed", methods=["GET"])
def currency_allowed(currency):
    return jsonify({"error": "Not Implemented Yet"}), 501

@app.route("/currency/<string:currency>/rate", methods=["POST"])
def set_currency_rate(currency):
    return jsonify({"error": "Not Implemented Yet"}), 501

@app.route("/transaction/card", methods=["POST"])
def transaction_card():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    return jsonify({}), 200  # Transaction acceptée (simulation)

@app.route("/transaction/check", methods=["POST"])
def transaction_check():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    return jsonify({}), 200  # Simulation d'enregistrement

@app.route("/transaction/transfer", methods=["POST"])
def transaction_transfer():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    return jsonify({}), 200  # Simulation d'enregistrement

if __name__ == "__main__":
    app.run(host="10.0.2.1", port=5000, debug=True)
