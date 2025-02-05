import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Quelques données tests pour l’annuaire sous la forme d’une liste de dictionnaires
clients = [
   {'id': 0,
	'nom': 'Dupont',
	'prenom': 'Jean',
	'solde': 100,
	},
   {'id': 1,
	'nom': 'Durand',
	'prenom': 'Elodie',
	'solde': 10000,
   },
   {'id': 2,
	'nom': 'Luca',
	'prenom': 'Anna',
	'solde': 1500,
	}
]

def used_id(list=clients):
   result=[]
   for i in range len(clients):
      for key, value in i:
         result.append(value)
   return result

# Route permettant de récupérer toutes les données de l’annuaire
@app.route('/', methods=['GET'])
def home():
   return "<h1>API PUBLIQUE</h1><p>Prototype dune API publique mettant à disposition ces comptes bancaires des utilisateurs de MyLittleBank</p>"

@app.route('/create_account', methods=['POST'])
def create_account(list_clients=clients):
   if request.method == 'POST':
      id_user=list_clients[len()]
      first_name = request.form['firstname']
      last_name = request.form['lastname']
      solde = 0

      if id_user in users :
         clients.append()
         return (id_user, first_name, last_name, solde)
      else:
         return '<h1>invalid credentials!</h1>'
    else:
        return render_template('login.html')

@app.route('/api/v1/resources/clients', methods=['GET'])
def api_get_id():
    # Vérifie si un ID est fourni dans une URL.
    # Si un ID est fourni, il est affecté à une variable.
    # Si aucun ID n’est fourni, un message d’erreur est affiché dans le navigateur.
    if 'id' in request.args:
        id = int(request.args['id'])
        return jsonify(clients[id])
    else:
        return "Erreur: Pas d'identifiant fourni. Veuillez spécifier un id."

@app.route('/api/v1/resources/clients/', methods=['GET'])
def api_all():
    return jsonify(clients)

app.run()