from datetime import datetime
import flask 
from flask import *
#curl http://127.0.0.1:5000//account/1/exists
#curl -X POST http://127.0.0.1:5000/transaction/transfer -H "Content-Type: application/json" -d '{"sourceAccount": 6,  "destAccount": 829330,  "currency": "USD",  "amount": 51.5,  "label": "Virement Papa"}'

app = flask.Flask(__name__)
app.config["DEBUG"] = True

BACKEND_URL = "http://192.168.5.4:5000/"

######################################################################################################################################
#récupération de la BDD
rates_EUR={'USD':1.04, 'GBP':0.83 }
rates_GBP={'USD':1.26, 'EUR':1.21 }
rates_USD={'EUR':0.96, 'GBP':0.79 }
accepted_currency=["USD", "EUR", "GBP"]

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
   """fonction permettant de récupérer les infos d'un compte en particulier"""
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

##################################/####################################################################################################

@app.route("/account/<account>/exists", methods=["GET"])
def account_exists(account):
   result=all_used_id()
   try :
      compte=int(account)
      if compte in result:
         return "Le compte existe", 200
      else:
         return "Le compte n'existe pas.", 404
   except:
      return "Paramètres invalides",400


@app.route("/currency/<currency>/allowed", methods=["GET"])
def currency_allowed(currency):
   allowed_currencies = ["EUR", "USD", "GBP"]
   try:
      int(currency)
   except:
      if isinstance(currency, str):
         if currency in allowed_currencies:
            return "La devise est acceptée.", 200
         else :
            return "La devise n'est pas acceptées.", 404
   return "Paramètres invalides.", 400

@app.route("/currency/<currency>/rate", methods=["POST"])
def set_currency_rate(currency):
   data_tmp = request.get_json()
   data=json.loads(data_tmp)
   data_currency=data['currency']
   
   if "rate" not in data or data_currency not in accepted_currency or currency not in accepted_currency or currency==data_currency:
      return "Paramètres invalides", 400
   
   if currency=="EUR":
      rates_EUR[data_currency]=data['rate']
      print(rates_EUR)
   elif currency=="USD":
      rates_USD[data_currency]=data['rate']
      print(rates_USD)
   elif currency=="GBP":
      rates_GBP[data_currency]=data['rate']
      print(rates_GBP)
   return {}, 200

@app.route("/transaction/card", methods=["POST"])
def transaction_card():
   data_tmp = request.get_json()
   data=json.loads(data_tmp)
   if not all(key in data for key in ('sourceAccount', 'destAccount', 'currency', 'amount', 'merchant')):
      return "Paramètres invalides", 400
   if isinstance(data['sourceAccount'], int) and isinstance(data['destAccount'], int) and isinstance(data['currency'], str) and (isinstance(data['amount'], float) or isinstance(data['amount'], int)) and isinstance(data['merchant'], str):
      source=data['sourceAccount']
      destination=data["destAccount"]
      currency=data["currency"]
      amount=data["amount"]
      merchant=data["merchant"]

      #list all used_ids
      result=all_used_id()

      # Check if the source account exists
      if source not in result:
         return "Compte inconnu", 404


      #Get the account to better manipulate the entity
      account_source=get_account(source)


      if currency!=account_source['currency']:
         if currency=="EUR":
            amount*=rates_EUR[account_source['currency']]
         elif currency=="USD":
            amount*=rates_USD[account_source['currency']]
         elif currency=="GBP":
            amount*=rates_GBP[account_source['currency']]

      # Check if the balance is sufficient
      if account_source["balance"] < amount:
         return "La transaction est rejetée du fait d'un solde insuffisant.", 401

      # Update balance
      account_source['balance'] -= amount

      #Record transaction
      now = datetime.now()
      timestamp = datetime.timestamp(now)
      label= "Card transaction from " + str(source) + " to " + str(destination) + " the " + str(now)

      transaction = {
         'timestamp': int(timestamp),
         'label': label,
         'amount': amount
      }
      account_source['transaction-list'].append(transaction)
      print(account_source)
      return {}, 200
   
   elif data["currency"] not in accepted_currency:
      return "La devise n'est pas supportée.", 406
   
   else:
      return "Paramètres invalides", 400
   

############################################################################################################

@app.route("/transaction/check", methods=["POST"])
def transaction_check():
   data_tmp = request.get_json()
   data=json.loads(data_tmp)
   if not all(key in data for key in ('sourceAccount', 'destAccount', 'currency', 'amount')):
      return "Paramètres invalides", 400
   if isinstance(data['sourceAccount'], int) and isinstance(data['destAccount'], int) and isinstance(data['currency'], str) and (isinstance(data['amount'], float) or isinstance(data['amount'], int)) :
      source=data['sourceAccount']
      destination=data["destAccount"]
      currency=data["currency"]
      amount=data["amount"]
      
      #list all used_ids
      result=all_used_id()
      
      # Check if the source account exists
      if source not in result:
         return "Compte inconnu", 404
      
      
      #Get the account to better manipulate the entity
      account_source=get_account(source)


      if currency!=account_source['currency']:
         if currency=="EUR":
            amount*=rates_EUR[account_source['currency']]
         elif currency=="USD":
            amount*=rates_USD[account_source['currency']]
         elif currency=="GBP":
            amount*=rates_GBP[account_source['currency']]
      
      #not needed by swagger = assume the client can be indebted
      # # Check if the balance is sufficient
      # if account_source["balance"] < amount:
      #    return "La transaction est rejetée du fait d'un solde insuffisant.", 401
      
      # Update balance
      account_source['balance'] -= amount
      
      #Record transaction
      now = datetime.now()
      timestamp = datetime.timestamp(now)
      label= "Check transaction from " + str(source) + " to " + str(destination) + " the " + str(now)

      transaction = {
         'timestamp': int(timestamp),
         'label': label,
         'amount': amount
      }
      account_source['transaction-list'].append(transaction)
      print(account_source)
      return {}, 200
   elif data["currency"] not in accepted_currency:
      return "	La devise n'est pas supportée.", 406
   else :
      return "Paramètres invalides", 400
   

@app.route("/transaction/transfer", methods=["POST"])
def transaction_transfer():
   data_tmp = request.get_json()
   data=json.loads(data_tmp)
   if not all(key in data for key in ('sourceAccount', 'destAccount', 'currency', 'amount', 'label')):
      return "Paramètres invalides", 400
   if isinstance(data['sourceAccount'], int) and isinstance(data['destAccount'], int) and isinstance(data['currency'], str) and (isinstance(data['amount'], float) or isinstance(data['amount'], int)) and isinstance(data['label'], str) :
      source=data['sourceAccount']
      destination=data["destAccount"]
      currency=data["currency"]
      amount=data["amount"]
      label=data['label']
      
      #list all used_ids
      result=all_used_id()
      
      # Check if the source account exists
      if source not in result:
         return "Compte inconnu", 404
      
      
      #Get the account to better manipulate the entity
      account_source=get_account(source)

      if currency!=account_source['currency']:
         if currency=="EUR":
            amount*=rates_EUR[account_source['currency']]
         elif currency=="USD":
            amount*=rates_USD[account_source['currency']]
         elif currency=="GBP":
            amount*=rates_GBP[account_source['currency']]
      
      # Check if the balance is sufficient
      if account_source["balance"] < amount:
         return "La transaction est rejetée du fait d'un solde insuffisant.", 401
      
      # Update balance
      account_source['balance'] -= amount
      
      #Record transaction
      now = datetime.now()
      timestamp = datetime.timestamp(now)

      transaction = {
         'timestamp': int(timestamp),
         'label': label,
         'amount': amount
      }
      account_source['transaction-list'].append(transaction)
      print(account_source)
      return {}, 200
   elif data["currency"] not in accepted_currency:
      return "La devise n'est pas supportée.", 406
   else:
      return "Paramètres invalides", 400
   

app.run(host="127.0.0.1", port=5000)