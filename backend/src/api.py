import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from jose import jwt
from flask_cors import CORS
from sqlalchemy.sql.expression import null

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    print(drinks)
    short_formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': short_formatted_drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    long_formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': long_formatted_drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    data = request.get_json()
    # print(data)
    # title_new = data.get("title")
    # recipe_new = data.get("recipe")
    # recipe_new = data["recipe"]
    # print(drinks.title)

    if 'title' not in data or data['title'] == '':
        abort(422)

    drinks = Drink.query.filter(Drink.title==data['title']).all()

    if drinks:
        abort(422)

    if 'recipe' not in data or data.get('recipe') is None:
        abort(422)

    title_new = data["title"]
    recipe_new = data.get('recipe')

    print(recipe_new)

    # drink_new = Drink(title=title_new, recipe=jsonify(recipe_new.serialize()))
    drink_new = Drink(title = title_new, recipe = json.dumps(recipe_new))

    drink_new.insert()
    # drink = [drink_new.long()]

    return jsonify({
        'success': True,
        'drinks': drink_new.long()
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    drink = Drink.query.get(id)
    # print(drink)
    
    if drink is None:
        abort(404)
    data = request.get_json()
    # print(data)
    # print(json.dumps(data['recipe']))
    # print(json.dumps(data.get('recipe')))

    # print(data['recipe'])
    # print(data('recipe'))

    drink.title = data["title"]
    if json.dumps(data.get('recipe')) != 'null':
        drink.recipe = json.dumps(data.get("recipe"))
    # else:
        # drink.recipe = drink.recipe
        # drink.recipe = data["recipe"]
    # drink.update().long()
    drink.update()
    # print(drink)
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    drink.delete()
    return jsonify({
        'success': True,
        'drink' : id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def handle_error(err):
    return jsonify({
        "sucess": False,
        "error": err.error['code'],
        "description": err.error['description'],
        "status_code": err.status_code
    }), err.status_code