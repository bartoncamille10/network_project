import psycopg2
import random
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Connexion à la base de données PostgreSQL
try:
    connection = psycopg2.connect(user="postgres",
                                   password="postgres",     
                                   host="localhost",
                                   database="network_project_db")
    cursor = connection.cursor()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

def close_connection():
    """Fermer la connexion à la base de données"""
    cursor.close()
    connection.close()

def check_user(account_id):
    """Vérifie si un utilisateur existe dans la base de données."""
    try:
        query = "SELECT * FROM Client WHERE account = %s;"
        cursor.execute(query, (account_id,))
        return cursor.fetchone() is not None
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la vérification de l'utilisateur:", error)
        return False

def get_balance_from_db(account):
    """Récupère le solde du compte depuis la base de données."""
    try:
        query = "SELECT balance FROM Client WHERE account = %s;"
        cursor.execute(query, (account,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as error:
        print("Erreur get_balance_from_db:", error)
        return None

@app.route('/account', methods=['POST'])
def create_account():
    """Créer un nouveau compte."""
    data = request.get_json()
    balance = data.get("balance", 0.0)
    new_account_id = random.randint(1, 999999)
    
    #appel à l'API publique pour créer le compte
    try:
        response = requests.post(
            'http://127.0.0.1:5000/account', 
            json={'balance': balance}, 
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            query = "INSERT INTO Client (account, balance, currency) VALUES (%s, %s, %s);"
            cursor.execute(query, (new_account_id, balance, "EUR"))
            connection.commit()
            return jsonify({"account": new_account_id, "balance": balance}), 200
        else:
            return jsonify({"error": "Error while creating account via API"}), 400
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/account/<account>/balance', methods=['GET'])
def get_balance(account):
    """Récupère le solde du compte spécifié."""
    if not check_user(account):
        return jsonify({"error": "Compte introuvable"}), 404
    
    balance = get_balance_from_db(account)
    if balance is None:
        return jsonify({"error": "Solde introuvable"}), 404
    
    return jsonify({"account": account, "balance": balance}), 200

@app.route('/account/<account>/transfer', methods=['POST'])
def account_transfer(account):
    """Effectuer un virement entre deux comptes."""
    data = request.get_json()
    required_fields = ["amount", "recipient"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Paramètres invalides"}), 400

    amount = data["amount"]
    recipient = data["recipient"]
    
    if not check_user(account) or not check_user(recipient):
        return jsonify({"error": "Compte introuvable"}), 404

    balance = get_balance_from_db(account)
    if balance is None or balance < amount:
        return jsonify({"error": "Solde insuffisant"}), 400

    try:
        #débit du compte source
        cursor.execute("UPDATE Client SET balance = balance - %s WHERE account = %s;", (amount, account))
        #crédit du compte destinataire
        cursor.execute("UPDATE Client SET balance = balance + %s WHERE account = %s;", (amount, recipient))
        #enregistrement de la transaction
        cursor.execute("INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);", (account, recipient, amount))

        connection.commit()
        return jsonify({"message": "Virement réussi"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/account/<account>/exists', methods=['GET'])
def account_exists(account):
    """Vérifie si un compte existe."""
    if not check_user(account):
        return jsonify({"error": "Le compte n'existe pas"}), 404
    return jsonify({"message": "Le compte existe"}), 200


    

if __name__ == '__main__':
    app.run(debug=True)
    close_connection()
