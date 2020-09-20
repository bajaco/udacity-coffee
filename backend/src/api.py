import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# uncomment following line to drop all records and recreate database
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def retrieve_drinks():

    drink_query = Drink.query.all()
    drinks = []
    for drink in drink_query:
        drinks.append(drink.short())
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    print(payload)
    drink_query = Drink.query.all()
    drinks = [drink.long() for drink in drink_query]
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        data = request.get_json()
        new_title = data.get('title')
        new_recipe = json.dumps(data.get('recipe'))
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
            }), 200
    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
    try:
        drink = Drink.query.get_or_404(drink_id)
        data = request.get_json()
        drink.title = data.get('title')
        drink.recipe = json.dumps(data.get('recipe'))
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
            }), 200
    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    try:
        drink = Drink.query.get_or_404(drink_id)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
            }), 200
    except:
        abort(422)


# Error Handling


@app.errorhandler(AuthError)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
