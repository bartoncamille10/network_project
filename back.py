import psycopg2, random
from flask import Flask, jsonify, request


app = Flask(__name__)

try:
    connection = psycopg2.connect(user="postgres",
                                password="postgres",     
                                host="localhost",
                                database="network_project_db")
    cursor = connection.cursor()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)    

def close_connection():
    cursor.close()
    connection.close()



# API PUBLIC

def get_transactions(account_id):
    try:
        query = """
            SELECT client_source, client_dest, montant, date_transaction 
            FROM Transaction
            WHERE client_source = %s OR client_dest = %s
            ORDER BY date_transaction DESC
            LIMIT 50;
        """
        cursor.execute(query, (account_id, account_id))
        transactions = cursor.fetchall()

        if not transactions:
            print(f"Aucune transaction trouvée pour le compte {account_id}.")
            return []

        # transformer le résultat en liste de dictionnaires
        transaction_list = [
            {
                "client_source": row[0],
                "client_dest": row[1],
                "amount": row[2],
                "date_transaction": row[3].isoformat()  # format ISO pour la date
            }
            for row in transactions
        ]

        return transaction_list

    except (Exception, psycopg2.Error) as error:
        print(f"Erreur lors de la récupération des transactions: {error}")
        return []


def check_user(account_id):
    try:
        query = "SELECT * FROM Client WHERE account = %s;"
        cursor.execute(query, (account_id,))
        return cursor.fetchone() is not None  # Retourne True si le compte existe, sinon False
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la vérification de l'utilisateur:", error)
        return False


@app.route('/account', methods=['POST'])
def create_account():
    """Créer un nouveau compte."""
    data = request.get_json()  # Utiliser request.get_json() pour récupérer les données JSON
    balance = data.get("balance", 0.0)
    

    new_account_id = random.randint(1, 999999)

    query = "INSERT INTO Client (account, balance, currency) VALUES (%s, %s, %s);"
    try:
        cursor.execute(query, (new_account_id, balance))
        connection.commit()
        return jsonify({"account": new_account_id, "balance": balance}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 400


def get_balance(account_id):
    """récupérer le solde du compte"""
    query = "SELECT balance FROM Client WHERE account = %s;"
    cursor.execute(query, (account_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None


@app.route('/transaction/card', methods=['POST'])
def transaction_card():
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        data = request.get_json()
        required_fields = ["sourceAccount", "destAccount", "amount", "merchant"]
        
        # vérifier si toutes les données sont bien présentes
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Paramètres invalides"}), 400

        source = data["sourceAccount"]
        dest = data["destAccount"]
        amount = data["amount"]

        # vérifier si les comptes existent
        if not check_user(source) or not check_user(dest):
            return jsonify({"error": "Compte inconnu"}), 404

        # vérifier si le solde est suffisant
        solde_source = get_balance(source)
        if solde_source is None or solde_source < amount:
            return jsonify({"error": "Solde insuffisant"}), 401

        # effectuer la transaction
        query_debit = "UPDATE Client SET balance = balance - %s WHERE account = %s;"
        query_credit = "UPDATE Client SET balance = balance + %s WHERE account = %s;"
        query_insert = "INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);"

        cursor.execute(query_debit, (amount, source))
        cursor.execute(query_credit, (amount, dest))
        cursor.execute(query_insert, (source, dest, amount))

        connection.commit()

        return jsonify({"message": "Transaction par carte réussie"}), 200

    except Exception as error:
        connection.rollback()  # annule la transaction en cas d'échec
        print("Erreur transaction_card:", error)
        return jsonify({"error": "Erreur interne"}), 500


@app.route('/transaction/check', methods=['POST'])
def transaction_check():
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        data = request.get_json()
        required_fields = ["sourceAccount", "destAccount", "currency", "amount"]
        
        # Vérifier si toutes les données sont bien présentes
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Paramètres invalides"}), 400

        source = data["sourceAccount"]
        dest = data["destAccount"]
        currency = data["currency"]
        amount = data["amount"]

        # Vérifier si les comptes existent
        if not check_user(source) or not check_user(dest):
            return jsonify({"error": "Compte inconnu"}), 404

        # Effectuer l'encaissement du chèque (pas de vérification de solde ici)
        query_credit = "UPDATE Client SET balance = balance + %s WHERE account = %s;"
        query_insert = "INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);"

        cursor.execute(query_credit, (amount, dest))  # On crédite directement le destinataire
        cursor.execute(query_insert, (source, dest, amount))

        connection.commit()

        return jsonify({"message": "Encaissement du chèque réussi"}), 200

    except Exception as error:
        connection.rollback()  # Annule la transaction en cas d'échec
        print("Erreur transaction_check:", error)
        return jsonify({"error": "Erreur interne"}), 500


@app.route('/transaction/transfer', methods=['POST'])
def transaction_transfer():
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        data = request.get_json()
        required_fields = ["sourceAccount", "destAccount", "currency", "amount", "label"]
        
        # Vérifier si toutes les données sont bien présentes
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Paramètres invalides"}), 400

        source = data["sourceAccount"]
        dest = data["destAccount"]
        currency = data["currency"]
        amount = data["amount"]
        label = data["label"]

        # Vérifier si les comptes existent
        if not check_user(source) or not check_user(dest):
            return jsonify({"error": "Compte inconnu"}), 404

        # Vérifier si le solde est suffisant
        solde_source = get_balance(source)
        if solde_source is None or solde_source < amount:
            return jsonify({"error": "Solde insuffisant"}), 401

        # Effectuer le virement
        query_debit = "UPDATE Client SET balance = balance - %s WHERE account = %s;"
        query_credit = "UPDATE Client SET balance = balance + %s WHERE account = %s;"
        query_insert = "INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);"

        cursor.execute(query_debit, (amount, source))
        cursor.execute(query_credit, (amount, dest))
        cursor.execute(query_insert, (source, dest, amount))

        connection.commit()

        return jsonify({"message": f"Virement immédiat réussi : {label}"}), 200

    except Exception as error:
        connection.rollback()  # Annule la transaction en cas d'échec
        print("Erreur transaction_transfer:", error)
        return jsonify({"error": "Erreur interne"}), 500


if __name__ == '__main__':
    app.run(debug=True)
    close_connection()