import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

# Login-Link
# https://kprod.auth0.com/authorize?audience=Image&response_type=token&client_id=8k1wVdOVM0hW1TCimy1iCnWVq3m6JE7N&redirect_uri=http://localhost:5432/login-results


app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def get_drinks():

    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    drinks_short = [drink.short() for drink in drinks]

    return jsonify({"success": True, "drinks": drinks_short})


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            abort(404)

        drinks_long = [drink.long() for drink in drinks]
        return jsonify({"success": True, "drinks": drinks_long})
    except Exception as e:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        body = request.get_json()
        recipe = json.dumps(body['recipe'])
        title = body['title']
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({"success": True, "drinks": [drink.long()]})

    except Exception as e:
        abort(400)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):

    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            abort(404)

        body = request.get_json()

        if 'title' in body:
            drink.title = body['title']

        if 'recipe' in body:
            drink.recipe = json.dump(body['recipe'])

        drink.update()

        return jsonify({"success": True, "drinks": [drink.long()]})

    except Exception as e:
        abort(400)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            abort(404)

        drink.delete()
        return jsonify({"success": True, "delete": id})

    except Exception as e:
        abort(400)

# Error Handling
@app.errorhandler(HTTPException)
def http_exception(error):
    return jsonify(
        {"success": False,
         "error": error.code,
         "message": error.description})


@app.errorhandler(AuthError)
def auth_error_handler(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
