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

        
        transaction_list = [
            {
                "client_source": row[0],
                "client_dest": row[1],
                "amount": row[2],
                "date_transaction": row[3].isoformat()  
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
        return cursor.fetchone() is not None  
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la vérification de l'utilisateur:", error)
        return False


@app.route('/account', methods=['POST'])
def create_account():
    """Créer un nouveau compte."""
    data = request.get_json()  
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

def get_balance_from_db(account):
    try:
        query = "SELECT balance FROM Client WHERE account = %s;"
        cursor.execute(query, (account,))
        result = cursor.fetchone()

        if result: 
            return float(result[0])  
        return None  
    except Exception as error:
        print("Erreur get_balance_from_db:", error)
        return None


@app.route('/account/<int:account>/balance', methods=['GET'])
def get_balance(account):
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        query = "SELECT balance, currency FROM Client WHERE account = %s;"
        cursor.execute(query, (account,))
        result = cursor.fetchone()

        if result:
            balance, currency = result
            return jsonify({
                "account": account,
                "currency": currency,
                "balance": float(balance)  
            }), 200
        else:
            return jsonify({"error": "Compte introuvable"}), 404

    except Exception as error:
        print("Erreur get_account_balance:", error)
        return jsonify({"error": "Erreur interne"}), 500



@app.route('/account/<int:account>/details', methods=['GET'])
def get_account_details(account):
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        
        query_account = "SELECT balance, currency FROM Client WHERE account = %s;"
        cursor.execute(query_account, (account,))
        account_result = cursor.fetchone()

        if not account_result:
            return jsonify({"error": "Compte introuvable"}), 404

        balance, currency = account_result

        
        query_transactions = """
            SELECT date_transaction, client_source, client_dest, montant 
            FROM Transaction 
            WHERE client_source = %s OR client_dest = %s
            ORDER BY date_transaction DESC
            LIMIT 50;
        """
        cursor.execute(query_transactions, (account, account))
        transactions = cursor.fetchall()

        transaction_list = []
        for transaction in transactions:
            date_transaction, client_source, client_dest, montant = transaction
            label = f"Transaction vers {client_dest}" if client_source == account else f"Transaction de {client_source}"
            transaction_list.append({
                "timestamp": int(date_transaction.timestamp()),
                "label": label,
                "amount": float(montant)
            })

        return jsonify({
            "account": account,
            "currency": currency,
            "balance": float(balance),
            "operations": transaction_list
        }), 200

    except Exception as error:
        print("Erreur get_account_details:", error)
        return jsonify({"error": "Erreur interne"}), 500

@app.route('/account/<int:account>/transfer', methods=['POST'])
def account_transfer(account):
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        data = request.get_json()
        required_fields = ["amount", "currency", "label", "recipient"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Paramètres invalides"}), 400

        amount = data["amount"]
        currency = data["currency"]
        label = data["label"]
        recipient = data["recipient"]

        if currency != "EUR":
            return jsonify({"error": "Seule la devise EUR est acceptée"}), 400

        if not check_user(account) or not check_user(recipient):
            return jsonify({"error": "Compte introuvable"}), 400

        solde_source = get_balance_from_db(account)  
        if solde_source is None or solde_source < amount:
            return jsonify({"error": "Solde insuffisant"}), 400

        query_debit = "UPDATE Client SET balance = balance - %s WHERE account = %s;"
        query_credit = "UPDATE Client SET balance = balance + %s WHERE account = %s;"
        query_insert = "INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);"

        cursor.execute(query_debit, (amount, account))
        cursor.execute(query_credit, (amount, recipient))
        cursor.execute(query_insert, (account, recipient, amount))

        connection.commit()

        return jsonify({"message": f"Virement réussi : {label}"}), 200

    except Exception as error:
        connection.rollback()
        print("Erreur account_transfer:", error)
        return jsonify({"error": "Erreur interne"}), 500


@app.route('/account/<int:account>/exists', methods=['GET'])
def account_exists(account):
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        query = "SELECT COUNT(*) FROM Client WHERE account = %s;"
        cursor.execute(query, (account,))
        count = cursor.fetchone()[0]

        if count > 0:
            return jsonify({"message": "Le compte existe"}), 200
        else:
            return jsonify({"error": "Le compte n'existe pas"}), 404

    except Exception as error:
        print("Erreur account_exists:", error)
        return jsonify({"error": "Erreur interne"}), 500



# API PRIVEE

@app.route('/transaction/card', methods=['POST'])
def transaction_card():
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        data = request.get_json()
        required_fields = ["sourceAccount", "destAccount", "amount", "merchant"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Paramètres invalides"}), 400

        source = data["sourceAccount"]
        dest = data["destAccount"]
        amount = data["amount"]

        if not check_user(source) or not check_user(dest):
            return jsonify({"error": "Compte inconnu"}), 404

        solde_source = get_balance(source)
        if solde_source is None or solde_source < amount:
            return jsonify({"error": "Solde insuffisant"}), 401

        query_debit = "UPDATE Client SET balance = balance - %s WHERE account = %s;"
        query_credit = "UPDATE Client SET balance = balance + %s WHERE account = %s;"
        query_insert = "INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);"

        cursor.execute(query_debit, (amount, source))
        cursor.execute(query_credit, (amount, dest))
        cursor.execute(query_insert, (source, dest, amount))

        connection.commit()

        return jsonify({"message": "Transaction par carte réussie"}), 200

    except Exception as error:
        connection.rollback()  
        print("Erreur transaction_card:", error)
        return jsonify({"error": "Erreur interne"}), 500


@app.route('/transaction/check', methods=['POST'])
def transaction_check():
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        data = request.get_json()
        required_fields = ["sourceAccount", "destAccount", "currency", "amount"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Paramètres invalides"}), 400

        source = data["sourceAccount"]
        dest = data["destAccount"]
        currency = data["currency"]
        amount = data["amount"]

        if not check_user(source) or not check_user(dest):
            return jsonify({"error": "Compte inconnu"}), 404

        
        query_credit = "UPDATE Client SET balance = balance + %s WHERE account = %s;"
        query_insert = "INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);"

        cursor.execute(query_credit, (amount, dest)) 
        cursor.execute(query_insert, (source, dest, amount))

        connection.commit()

        return jsonify({"message": "Encaissement du chèque réussi"}), 200

    except Exception as error:
        connection.rollback()  
        print("Erreur transaction_check:", error)
        return jsonify({"error": "Erreur interne"}), 500


@app.route('/transaction/transfer', methods=['POST'])
def transaction_transfer():
    if not connection:
        return jsonify({"error": "Base de données indisponible"}), 500

    try:
        data = request.get_json()
        required_fields = ["sourceAccount", "destAccount", "currency", "amount", "label"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Paramètres invalides"}), 400

        source = data["sourceAccount"]
        dest = data["destAccount"]
        currency = data["currency"]
        amount = data["amount"]
        label = data["label"]

        if not check_user(source) or not check_user(dest):
            return jsonify({"error": "Compte inconnu"}), 404

        solde_source = get_balance(source)
        if solde_source is None or solde_source < amount:
            return jsonify({"error": "Solde insuffisant"}), 401

        query_debit = "UPDATE Client SET balance = balance - %s WHERE account = %s;"
        query_credit = "UPDATE Client SET balance = balance + %s WHERE account = %s;"
        query_insert = "INSERT INTO Transaction (client_source, client_dest, montant) VALUES (%s, %s, %s);"

        cursor.execute(query_debit, (amount, source))
        cursor.execute(query_credit, (amount, dest))
        cursor.execute(query_insert, (source, dest, amount))

        connection.commit()

        return jsonify({"message": f"Virement immédiat réussi : {label}"}), 200

    except Exception as error:
        connection.rollback()  
        print("Erreur transaction_transfer:", error)
        return jsonify({"error": "Erreur interne"}), 500


if __name__ == '__main__':
    app.run(debug=True)
    close_connection()