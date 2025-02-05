# Import de bibliothèques
import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True
# Quelques données tests pour l’annuaire sous la forme d’une liste de dictionnaires
employees = [
   {'id': 0,
	'Nom': 'Dupont',
	'Prenom': 'Jean',
	'Fonction': 'Développeur',
	'Ancienneté': '5'},
   {'id': 1,
	'Nom': 'Durand',
	'Prenom': 'Elodie',
	'Fonction': 'Directrice Commerciale',
	'Ancienneté': '4'},
   {'id': 2,
	'Nom': 'Lucas',
	'Prenom': 'Jeremie',
	'Fonction': 'DRH',
	'Ancienneté': '4'}
]

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Annuaire Internet</h1> <p>Ce site est le prototype d’une API mettant à disposition des données sur les employés d’une entreprise.</p>'''
 
 
@app.route('/api/v1/resources/employees/all', methods=['GET'])
def api_all():
    return jsonify(employees)
 
 
@app.route('/api/v1/resources/employees', methods=['GET'])
def api_id():
    # Vérifie si un ID est fourni dans une URL.
    # Si un ID est fourni, il est affecté à une variable.
    # Si aucun ID n’est fourni, un message d’erreur est affiché dans le navigateur.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Erreur: Pas d’identifiant fourni. Veuillez spécifier un id."
 
    # Crée une liste vide pour stocker les résultats
    results = []
 
    # Boucle sur les données pour obtenir les résultats correspondant à l’ID fourni.
    # Les IDs sont uniques, mais les autres champs peuvent renvoyer plusieurs résultats
    for employee in employees:
        if employee['id'] == id:
            results.append(employee)

    return jsonify(results)
 
app.run()