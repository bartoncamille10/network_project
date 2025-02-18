from datetime import datetime
import flask
from flask import *

#python3 api_pub.py
#curl http://127.0.0.1:5000/account/7/balance
#curl -X POST --data '{"balance": 1000}' -H "Content-Type: application/json" http://127.0.0.1:5000/account

app = flask.Flask(__name__)
app.config["DEBUG"] = True


######################################################################################################################################
#récupération de la BDD
clients = [
   {'account': 0, 
   'currency':"EUR",
	'balance': 100,
   'transaction-list':[
      {'label': "operation A",
      'amount': 100,
      'date_transaction': 1739791517}, 

      {'label':"operation B",
      'amount': 150,
      'date_transaction': 1736507753},

      {'label':"operation C",
      'amount': 72,
      'date_transaction': 1731237353}]
	},
   {'account': 2, 
   'currency':"EUR",
	'balance': 100,
   'transaction-list':[
      {'label':"operation E",
      'amount': 100,
      'timestamp': 1737458153}, 

      {'label':"operation F",
      'amount': 10,
      'timestamp': 1735643753},

      {'label':"operation G",
      'amount': 52,
      'timestamp': 1728555353}]
   },
   {'account': 6, 
   'currency':"EUR",
	'balance': 100,
   'transaction-list':[
      {'label':"operation H",
      'amount': 100,
      'timestamp': 1737976553}, 

      {'label':"operation I",
      'amount': 10,
      'timestamp': 1736680553},

      {'label':"operation J",
      'amount': 2,
      'timestamp': 1736507753},

      {'label':"operation K",
      'amount': 25,
      'timestamp': 1765192553},

      {'label': "operation L",
      'amount': 2,
      'timestamp': 1764587753}]
	}
]


######################################################################################################################################

def get_account(account_number):
   """fonction peremttant de récupérer les infos d'un compte en particulier"""
   index=0
   account_number_tester=clients[index]["account"]
   while account_number_tester!=account_number and index<len(clients):
      index+=1
      account_number_tester=clients[index]["account"]

   if index==len(clients) and account_number_tester!=account_number:
      return "Erreur"
   else:
      return clients[index]


def all_used_id():
   """fonction permettant de lister tous les id utilisés dans la BDD"""
   result=[]
   for i in range(len(clients)):
         result.append(clients[i]['account'])
   return result


def last_id():
   """fonction permettant de calculer le dernier id utilisé"""
   return clients[-1]['account']

######################################################################################################################################

@app.route('/', methods=['GET'])
def home():
   return "<h1>API PUBLIQUE</h1><p>API publique mettant à disposition ces comptes bancaires des utilisateurs de MyLittleBank</p>"

######################################################################################################################################

@app.route('/account', methods=['POST'])
def api_create_account():
   """fonction créant un compte avec une méthode POST"""
   id_user=last_id()+1
   account=request.get_json()
   try :
      solde=int(account['balance'])
   except:
      return "Paramètres invalides", 400 
   
   clients.append({'account': id_user, 'currency': "EUR", 'balance': solde,'transaction-list':[]})
   selected_account=get_account(id_user)
   account_number=selected_account["account"]
   account_currency=selected_account["currency"]
   account_balance=selected_account["balance"]
               
   result={
      'account': account_number,
      'currency': account_currency,
      'balance': account_balance
   }
   return result, 200

######################################################################################################################################

@app.route('/account/<account>/balance', methods=['GET'])
def api_get_balance(account): 
   """fonction permettant d'obtenir le solde d'un compte spécifique"""
   result=all_used_id()
   try:
      compte=int(account)
   except:
      return "Identifiant invalide", 400 
   
   if compte in result:
      selected_account=get_account(compte)
      account_number=selected_account["account"]
      account_currency=selected_account["currency"]
      account_balance=selected_account["balance"]
               
      result={
         'account': account_number,
         'currency': account_currency,
         'balance': account_balance
      }
      return result, 200
   else :
      return "Compte introuvable", 404


######################################################################################################################################

@app.route('/account/<account>/details', methods=['GET'])
def api_get_details(account): 
   """fonction permettant d'obtenir le solde d'un compte spécifique"""
   try:
      compte=int(account)
   except:
      return "Identifiant invalide", 400
   
   result=all_used_id()
   if compte in result:
      selected_account=get_account(compte)
      account_number=selected_account["account"]
      account_currency=selected_account["currency"]
      account_balance=selected_account["balance"]
      account_details=selected_account["transaction-list"]

               
      result= {
         'account': account_number,
         'currency': account_currency,
         'balance': account_balance,
         'operations' : account_details
      }
      return result
   else :
      return "Compte introuvable", 404

######################################################################################################################################
#curl -X POST http://127.0.0.1:5000/account/0/transfer -H "Content-Type: application/json" -d '{"amount": 5.5,"currency": "EUR","label": "Virement Maman","recipient": 2}'
@app.route('/account/<account>/transfer', methods=['POST'])
def virement(account):
    data = request.get_json()
    # Vérification des paramètres fournis
    if not all(key in data for key in ('recipient', 'amount', 'label', 'currency')):
        return "Paramètres manquants", 400

    id_source = int(account)
    id_dest = data['recipient']
    montant = data['amount']
    label = data['label']
    currency = data['currency']

    # Vérification des comptes source et destination
    client_source = next((c for c in clients if c['account'] == id_source), None)
    client_dest = next((c for c in clients if c['account'] == id_dest), None)

    if client_source is None or client_dest is None:
        return "Paramètres invalides", 400

    # Vérification du solde suffisant
    if client_source['balance'] < montant:
        return "Solde insuffisant", 404

    # Effectuer le virement
    client_source['balance'] -= montant
    client_dest['balance'] += montant

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    #label= "from " + str(id_dest) + " to " + str(id_source) + " the " +str(now) #for test purposes

    transaction = {
        'timestamp': int(timestamp),
        'label': label,
        'amount': montant        
    }
    
    client_source['transaction-list'].append(transaction)
    client_dest['transaction-list'].append(transaction)

   #  return (jsonify({
   #      'message': 'Virement effectue avec succes',
   #      'nouveau_solde_source': client_source['balance'],
   #      'nouveau_solde_dest': client_dest['balance'],
   #      'transaction': transaction
   #  }))
    return "Réussi", 200

app.run()