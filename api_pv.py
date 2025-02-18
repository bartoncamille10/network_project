from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('bbd_projet.db')
    conn.row_factory = sqlite3.Row
    return conn

#si la db est sur une autre machine : 

#def get_db_connection():
#   conn = psycopg2.connect(
#       host="remote_ip_address",
 #       database="bbd_projet",
  #      user="username",
   #     password="password"
    #)
    #return conn

#aussi installer psycopg2 avec pip

@app.route("/account/<int:account>/exists", methods=["GET"])
def account_exists(account):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account FROM Client WHERE account = ?", (account,))
    account_data = cursor.fetchone()
    conn.close()

    if account_data:
        return jsonify({"message": "Le compte existe"}), 200
    return jsonify({"error": "Le compte n'existe pas."}), 404


@app.route("/currency/<string:currency>/allowed", methods=["GET"])
def currency_allowed(currency):
    allowed_currencies = ["EUR", "USD", "GBP"]
    if currency in allowed_currencies:
        return jsonify({"message": "La devise est acceptée."}), 200
    return jsonify({"error": "La devise n'est pas acceptée."}), 404

@app.route("/currency/<string:currency>/rate", methods=["POST"])
def set_currency_rate(currency):
    data = request.get_json()
    if not data or "rate" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    rate = data["rate"]
    return jsonify({"message": f"Le taux de conversion pour {currency} est fixé à {rate}."}), 200

@app.route("/transaction/card", methods=["POST"])
def transaction_card():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if source account exists
    cursor.execute("SELECT balance FROM Client WHERE account = ?", (data["sourceAccount"],))
    account = cursor.fetchone()
    if not account:
        conn.close()
        return jsonify({"error": "Le compte source n'existe pas."}), 404
    
    # Check if balance is sufficient
    if account["balance"] < data["amount"]:
        conn.close()
        return jsonify({"error": "Solde insuffisant."}), 400
    
    # Update balance
    new_balance = account["balance"] - data["amount"]
    cursor.execute("UPDATE Client SET balance = ? WHERE account = ?", 
                  (new_balance, data["sourceAccount"]))
    
    # Record transaction
    cursor.execute("""
        INSERT INTO Transactions (client_source, client_dest, montant)
        VALUES (?, ?, ?)
    """, (data["sourceAccount"], data.get("destAccount", None), data["amount"]))

    
    conn.commit()
    conn.close()
    return jsonify({"message": "Transaction effectuée avec succès."}), 200


@app.route("/transaction/check", methods=["POST"])
def transaction_check():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if source account exists
    cursor.execute("SELECT balance FROM Client WHERE account = ?", (data["sourceAccount"],))
    account = cursor.fetchone()
    if not account:
        conn.close()
        return jsonify({"error": "Le compte source n'existe pas."}), 404
    
    # Check if balance is sufficient
    if account["balance"] < data["amount"]:
        conn.close()
        return jsonify({"error": "Solde insuffisant."}), 400
    
    conn.close()
    return jsonify({"message": "La transaction peut être effectuée."}), 200


@app.route("/transaction/transfer", methods=["POST"])
def transaction_transfer():
    data = request.get_json()
    if not data or "sourceAccount" not in data or "amount" not in data or "destAccount" not in data:
        return jsonify({"error": "Paramètres invalides"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check si la source existe
    cursor.execute("SELECT balance FROM Client WHERE account = ?", (data["sourceAccount"],))
    source_account = cursor.fetchone()
    if not source_account:
        conn.close()
        return jsonify({"error": "Le compte source n'existe pas."}), 404
    
    # Check si a destination existe
    cursor.execute("SELECT balance FROM Client WHERE account = ?", (data["destAccount"],))
    dest_account = cursor.fetchone()
    if not dest_account:
        conn.close()
        return jsonify({"error": "Le compte destination n'existe pas."}), 404
    
    # Check si il y a asssez das la balance
    if source_account["balance"] < data["amount"]:
        conn.close()
        return jsonify({"error": "Solde insuffisant."}), 400
    
    # Update la balance du compte source
    new_source_balance = source_account["balance"] - data["amount"]
    cursor.execute("UPDATE Client SET balance = ? WHERE account = ?", 
                  (new_source_balance, data["sourceAccount"]))
    
    # Update la balance du compte destinataire
    new_dest_balance = dest_account["balance"] + data["amount"]
    cursor.execute("UPDATE Client SET balance = ? WHERE account = ?", 
                  (new_dest_balance, data["destAccount"]))
    
    # ecrit la transaction
    cursor.execute("""
        INSERT INTO Transactions (client_source, client_dest, montant)
        VALUES (?, ?, ?)
    """, (data["sourceAccount"], data["destAccount"], data["amount"]))

    
    conn.commit()
    conn.close()
    return jsonify({"message": "Transfert effectué avec succès."}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
