import flask
from flask import *

#python3 api_pub.py
#curl http://127.0.0.1:5000/clients?account=7
#curl -X POST --data '{"balance":2}' -H "Content-Type: application/json" http://127.0.0.1:5000/account

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Quelques données tests pour l’annuaire sous la forme d’une liste de dictionnaires
clients = [
   {'account': 0, 
   'currency':"EUR",
	'balance': 100
	},
   {'account': 2, 
   'currency':"EUR",
	'balance': 100
   },
   {'account': 6, 
   'currency':"EUR",
	'balance': 100
	}
]

def get_account(account_number):
   index=0
   account_number_tester=clients[index]["account"]
   while account_number_tester!=account_number and index<len(clients):
      index+=1
      account_number_tester=clients[index]["account"]

   if index==len(clients) and account_number_tester!=account_number:
      return ("you piece of shit")
   else:
      return clients[index]

def all_used_id():
   result=[]
   for i in range(len(clients)):
         result.append(clients[i]['account'])
   return result

def last_id():
   return clients[-1]['account']


@app.route('/', methods=['GET'])
def home():
   return "<h1>API PUBLIQUE</h1><p>API publique mettant à disposition ces comptes bancaires des utilisateurs de MyLittleBank</p>"

@app.route('/account', methods=['GET', 'POST'])
def api_create_account():
   """fonction créant un compte avec une méthode POST"""
   if request.method == 'POST':
      id_user=last_id()+1
      solde=request.get_json()

      clients.append({'account': id_user, 'currency': "EUR", 'balance': solde["balance"]})
   return (clients)



@app.route('/clients', methods=['GET'])
def api_get_balance(): #?account=x
   if 'account' in request.args :
      compte = int(request.args['account'])
      if compte in all_used_id():
         selected_account=get_account(compte)
         account_number=selected_account["account"]
         account_balance=selected_account["balance"]
         account_currency=selected_account["currency"]
         
         return "Le solde du compte " + str(account_number) + " est de " + str(account_balance) + account_currency
      else :
         return "Erreur: le compte que vous recherchez n'existe pas chez nous. Veuillez réessayer."
   else:
      return "Erreur: Pas d'identifiant fourni. Veuillez spécifier un id."




@app.route('/clients/all', methods=['GET'])
def get_inof_all_accounts():
   
   return jsonify(clients)



@app.route('/api/v1/resources/clients/virement', methods=['POST'])
def virement():
    data = request.get_json()

    # Vérification des paramètres fournis
    if not all(key in data for key in ('account', 'currency', 'balance')):
        return jsonify({'error': 'Paramètres manquants'}), 400

    id_source = data['account']
    id_dest = data['currency']
    montant = data['balance']

    # Vérification des comptes source et destination
    client_source = next((c for c in clients if c['account'] == id_source), None)
    client_dest = next((c for c in clients if c['account'] == id_dest), None)

    if client_source is None or client_dest is None:
        return jsonify({'error': 'Un des comptes n\'existe pas'}), 404

    # Vérification du solde suffisant
    if client_source['balance'] < montant:
        return jsonify({'error': 'Solde insuffisant'}), 400

    # Effectuer le virement
    client_source['balance'] -= montant
    client_dest['balance'] += montant

    return jsonify({
        'message': 'Virement effectué avec succès',
        'nouveau_solde_source': client_source['balance'],
        'nouveau_solde_dest': client_dest['balance']
    }), 200

app.run()