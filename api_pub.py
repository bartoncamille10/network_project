import flask
from flask import *
import urllib.parse

#python3 api_pub.py
#curl http://127.0.0.1:5000/clients?account=7
#curl -X POST --data '{"balance":2}' -H "Content-Type: application/json" http://127.0.0.1:5000/account

app = flask.Flask(__name__)
app.config["DEBUG"] = True

#bdd TEST
clients = [
   {'account': 0, 
   'currency':"EUR",
	'balance': 100,
   'transaction-list':[
      {'client_source': 0, 
      'client_dest':2,
      'amount': 100,
      'date_transaction': 1739791517}, 

      {'client_source': 2, 
      'client_dest':20,
      'amount': 10,
      'date_transaction': 1736507753},

      {'client_source': 0, 
      'client_dest':2,
      'amount': 2,
      'date_transaction': 1731237353}]
	},
   {'account': 2, 
   'currency':"EUR",
	'balance': 100,
   'transaction-list':[
      {'client_source': 0, 
      'client_dest':2,
      'amount': 100,
      'date_transaction': 1737458153}, 

      {'client_source': 2, 
      'client_dest':20,
      'amount': 10,
      'date_transaction': 1735643753},

      {'client_source': 0, 
      'client_dest':2,
      'amount': 2,
      'date_transaction': 1728555353}]
   },
   {'account': 6, 
   'currency':"EUR",
	'balance': 100,
   'transaction-list':[
      {'client_source': 0, 
      'client_dest':2,
      'amount': 100,
      'date_transaction': 1737976553}, 

      {'client_source': 2, 
      'client_dest':20,
      'amount': 10,
      'date_transaction': 1736680553},

      {'client_source': 0, 
      'client_dest':2,
      'amount': 2,
      'date_transaction': 1736507753},

      {'client_source': 0, 
      'client_dest':2,
      'amount': 2,
      'date_transaction': 1765192553},

      {'client_source': 0, 
      'client_dest':2,
      'amount': 2,
      'date_transaction': 1764587753}]
	}
]


def get_account(account_number):
   index=0
   try :
      account_number_tester=clients[index]["account"]
   except:
      while account_number_tester!=account_number and index<len(clients):
         index+=1
         account_number_tester=clients[index]["account"]

   if index==len(clients) and account_number_tester!=account_number:
      return "Erreur: le compte que vous recherchez n'existe pas chez nous. Veuillez réessayer."
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
   result=all_used_id()
   return result
   #return "<h1>API PUBLIQUE</h1><p>API publique mettant à disposition ces comptes bancaires des utilisateurs de MyLittleBank</p>"


@app.route('/account', methods=['POST'])
def api_create_account():
   """fonction créant un compte avec une méthode POST"""
   if request.method == 'POST':
      id_user=last_id()+1
      solde=request.get_json()

      clients.append({'account': id_user, 'currency': "EUR", 'balance': solde["balance"]}, '')
   return (clients)



@app.route('/account/<account>/balance', methods=['GET'])
def api_get_balance(account): #?account=x
   """fonction permettant d'obtenir le solde d'un compte spécifique"""
   result=all_used_id()
   try:
      compte=int(account)
   except:
      return "<title>400 Not Found</title><h1>404 Not Found</h1><p>Identifiant invalide</p>"
   
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
      return result
   else :
      return "<title>404 Not Found</title><h1>404 Not Found</h1><p>Compte introuvable</p>"
   



@app.route('/api/v1/resources/clients/balance', methods=['GET'])
def balance():
    if 'account' in request.args:
        compte = int(request.args['account'])
        selected_account = next((c for c in clients if c['account'] == compte), None)
        if selected_account:
            response = {
                "account": selected_account["account"],
                "currency": selected_account["currency"],
                "balance": selected_account["balance"],
                #"operations": selected_account["operations"]
            }
            return jsonify(response)
        else:
            return jsonify({'error': 'Compte non trouvé'}), 404
    else:
        return jsonify({"error": "Erreur: Pas d'identifiant fourni. Veuillez spécifier un id."}), 400


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