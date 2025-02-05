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
	'nom': 'Lucas',
	'prenom': 'Anna',
	'solde': 1500,
	}
]


# Route permettant de récupérer toutes les données de l’annuaire
@app.route('/', methods=['GET'])
def home():
   return "<h1>Annuaire Internet</h1><p>Prototype dune API publique mettant à disposition ces comptes bancaires des utilisateurs de MyLittleBank</p>"

@app.route('/api/v1/resources/clients/', methods=['GET'])
def api_all():
    return jsonify(clients)

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