import flask
from flask import request, jsonify

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

def used_id():
   result=[]
   for i in range(len(clients)):
         result.append(clients[i]['account'])
   return result

def last_id():
   return clients[-1]['account']

# Route permettant de récupérer toutes les données de l’annuaire
@app.route('/', methods=['GET'])
def home():
   return "<h1>API PUBLIQUE</h1><p>Prototype dune API publique mettant à disposition ces comptes bancaires des utilisateurs de MyLittleBank</p>"

@app.route('/create_user', methods=['POST'])
def create_account():
   """fonction créant un compte avec une méthode POST"""

   id_user=last_id()+1
   solde=request.json()
   clients.append({'account': id_user, 'currency': "EUR", 'solde': solde})

   return (clients)

@app.route('/api/v1/resources/clients', methods=['GET'])
def api_get_id():
    # Vérifie si un ID est fourni dans une URL.
    # Si un ID est fourni, il est affecté à une variable.
    # Si aucun ID n’est fourni, un message d’erreur est affiché dans le navigateur.
    if 'account' in request.args:
        account = int(request.args['account'])
        return jsonify(clients[account])
    else:
        return "Erreur: Pas d'identifiant fourni. Veuillez spécifier un id."

@app.route('/api/v1/resources/clients/', methods=['GET'])
def api_all():
    return jsonify(clients)

app.run()