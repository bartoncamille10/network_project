from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/account/<int:account>/exists", methods=["GET"])
def account_exists(account):
    # test SANS interroger de base de données
    if account == 708273:
        return jsonify({"message": "Le compte existe"}), 200  # Message ajouté

    return jsonify({"error": "Le compte n'existe pas."}), 404

@app.route("/currency/<string:currency>/allowed", methods=["GET"])
def currency_allowed(currency):
    allowed_currencies = ["EUR", "USD", "GBP"]  # Liste des devises acceptées
    if currency in allowed_currencies:
        return jsonify({"message": "La devise est acceptée."}), 200
    return jsonify({"error": "La devise n'est pas acceptée."}), 404

@app.route("/currency/<string:currency>/rate", methods=["POST"])
def set_currency_rate(currency):
    data = request.get_json()
    if not data or "rate" not in data or "currency" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    # Logique pour fixer le taux de conversion (simulation)
    rate = data["rate"]
    target_currency = data["currency"]
    return jsonify({"message": f"Le taux de conversion pour {currency} vers {target_currency} est fixé à {rate}."}), 200

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
    app.run(host="127.0.0.1", port=5000, debug=True)