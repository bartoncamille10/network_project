import psycopg2, requests
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
#pv 

# def verifierCompte():


# def transactionCard():

# def transactionVirement():

# def transactionCheque():

# def lireFichier():



# API PUBLIC
# def transaction():


def check_user(id):
    try:
        query = "SELECT * FROM Client WHERE id = %s;"
        cursor.execute(query, (id,))
        print(cursor.fetchall())
    except (Exception, psycopg2.Error) as error:
        print("Error, user not found", error)

def create_account(id):
    user = check_user(id)
    if not user:
        url = "http://localhost:5000/create_account"
        response = requests.get(url)
        if(response.status_code == 200):
            print("Account created")
        else:
            print("Error while creating account")
            exit(1)

def get_balance(account_id):
    url = f"http://localhost:5000/account/{account_id}/balance"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        account_info = response.json()
        print(f"Solde du compte {account_id}: {account_info['balance']} {account_info['currency']}")
    else:
        print("Erreur lors de la récupération du solde:", response.status_code)

# Exemple d'appel
# get_balance(789123)

        
# def creation():
    

# TO DOOOOOOOOOOO mettre la sortie de la query en tableau de dictionnaire



# def retrieve_user(user):
#     connection_to_db()
#     try:
#         query = "SELECT * FROM Client WHERE username = %s;"
#         cursor.execute(query, (user,))
#     except (Exception, psycopg2.Error) as error:
#         print("Error, user not found", error)

if __name__ == '__main__':
    check_user(3)
    get_balance(1)
    close_connection()
