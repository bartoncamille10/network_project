from flask import Flask, jsonify, request
import requests


app = Flask(__name__)

@app.route("/account/<int:account>/exists", methods=["GET"])
def account_exists(account):
    try:
        backend_url = f"http://backend-machine:5000/account/{account}/exists"
        response = requests.get(backend_url, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Backend connection failed: {str(e)}"}), 500


@app.route("/currency/<string:currency>/allowed", methods=["GET"])
def currency_allowed(currency):
    try:
        backend_url = f"http://backend-machine:5000/currency/{currency}/allowed"
        response = requests.get(backend_url, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Backend connection failed: {str(e)}"}), 500


@app.route("/currency/<string:currency>/rate", methods=["POST"])
def set_currency_rate(currency):
    data = request.get_json()
    if not data or "rate" not in data or "currency" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    try:
        backend_url = f"http://backend-machine:5000/currency/{currency}/rate"
        response = requests.post(backend_url, json=data, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Backend connection failed: {str(e)}"}), 500


@app.route("/transaction/card", methods=["POST"])
def transaction_card():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    # Send request to backend
    try:
        backend_url = "http://backend-machine:5000/transaction"  # Replace with actual backend URL
        response = requests.post(backend_url, json=data, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Backend connection failed: {str(e)}"}), 500


@app.route("/transaction/check", methods=["POST"])
def transaction_check():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    try:
        backend_url = "http://backend-machine:5000/transaction/check"
        response = requests.post(backend_url, json=data, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Backend connection failed: {str(e)}"}), 500


@app.route("/transaction/transfer", methods=["POST"])
def transaction_transfer():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    try:
        backend_url = "http://backend-machine:5000/transaction/transfer"
        response = requests.post(backend_url, json=data, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Backend connection failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
