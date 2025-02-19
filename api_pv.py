from flask import Flask, jsonify, request

app = Flask(__name__)

EXISTING_ACCOUNTS = {
    "1": {"balance": 500, "currency": "USD"},
    "2": {"balance": 1000, "currency": "USD"},
    "3": {"balance": 50, "currency": "USD"}
}

SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP"]

@app.route("/", methods=["GET"])
def home():
    return "<h1>API PV Homepage </h1>", 200


@app.route("/account/<account>/exists", methods=["GET"])
def check_account(account):
    if account in EXISTING_ACCOUNTS:
        return jsonify({}), 200
    else:
        return jsonify({"error": "Compte non trouvé"}), 404

@app.route("/transaction/card", methods=["POST"])
def transaction_card():
    data = request.json

    if not all(k in data for k in ("sourceAccount", "destAccount", "currency", "amount", "merchant")):
        return jsonify({"error": "Paramètres invalides"}), 400
    
    source_account = data["sourceAccount"]
    dest_account = data["destAccount"]
    currency = data["currency"]
    amount = data["amount"]

    if source_account not in EXISTING_ACCOUNTS or dest_account not in EXISTING_ACCOUNTS:
        return jsonify({"error": "Compte inconnu"}), 404

    if currency not in SUPPORTED_CURRENCIES:
        return jsonify({"error": "Devise non supportée"}), 406

    if EXISTING_ACCOUNTS[source_account]["balance"] < amount:
        return jsonify({"error": "Solde insuffisant"}), 401
    

    EXISTING_ACCOUNTS[source_account]["balance"] -= amount
    EXISTING_ACCOUNTS[dest_account]["balance"] += amount

    return jsonify({}), 200

@app.route("/transaction/check", methods=["POST"])
def transaction_check():
    data = request.json
    if not all(k in data for k in ("sourceAccount", "destAccount", "amount", "currency")):
        return jsonify({"error": "Paramètres invalides"}), 400

    source_account = data["sourceAccount"]
    dest_account = data["destAccount"]
    amount = data["amount"]
    currency = data["currency"]

    if source_account not in EXISTING_ACCOUNTS or dest_account not in EXISTING_ACCOUNTS:
        return jsonify({"error": "Compte inconnu"}), 404

    if currency != "USD":
        return jsonify({"error": "Devise non supportée"}), 406

    EXISTING_ACCOUNTS[dest_account]["balance"] += amount
    return jsonify({}), 200

@app.route("/transaction/transfer", methods=["POST"])
def transaction_transfer():
    data = request.json

    if not all(k in data for k in ("sourceAccount", "destAccount", "amount", "currency", "label")):
        return jsonify({"error": "Paramètres invalides"}), 400

    source_account = data["sourceAccount"]
    dest_account = data["destAccount"]
    amount = data["amount"]
    currency = data["currency"]
    label = data["label"]

    if source_account not in EXISTING_ACCOUNTS or dest_account not in EXISTING_ACCOUNTS:
        return jsonify({"error": "Compte inconnu"}), 404
    
    if currency != "USD":
        return jsonify({"error": "Devise non supportée"}), 406

  
    if EXISTING_ACCOUNTS[source_account]["balance"] < amount:
        return jsonify({"error": "Solde insuffisant"}), 401

    EXISTING_ACCOUNTS[source_account]["balance"] -= amount
    EXISTING_ACCOUNTS[dest_account]["balance"] += amount

    return jsonify({}), 200


app.run(port=5000, debug=True)
