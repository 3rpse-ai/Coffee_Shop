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



'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    selection = Drink.query.all()
    drinks = [drink.short() for drink in selection]


    return jsonify({
        'success' : True,
        'drinks' : drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    print(payload)
    selection = Drink.query.all()
    drinks = [drink.long() for drink in selection]


    return jsonify({
        'success' : True,
        'drinks' : drinks
    })


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
def create_drink(payload):
    content = request.json
    try:
        new_title = content['title']
        new_recipe = content['recipe']
    except:
        abort(400)

    if not isinstance(new_recipe, list):
        abort(400)

    drink = Drink(title = new_title, recipe = json.dumps(new_recipe))
    try:
        drink.insert()
    except exc.IntegrityError as error:
        abort(400)
    return jsonify({
        'success' : True,
        'drinks' : [drink.long()]
    })

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

@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    content = request.json
    try:
        new_title = content['title']
    except:
        new_title = None
    
    try:
        new_recipe = content['recipe']
    except:
        new_recipe = None

    if new_recipe is None and new_title is None:
        abort(400)

    if new_recipe is not None:
        if not isinstance(new_recipe, list):
            abort(400)
        drink.recipe = json.dumps(new_recipe)

    if new_title is not None:
        drink.title = new_title

    drink.update()
    return jsonify({
        'success' : True,
        'drinks' : [drink.long()]
    })


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
@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    
    drink.delete()
    return jsonify({
        'success' : True,
        'delete' : drink_id
    })

## Error Handling
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
        'success' : False,
        'error' : 404,
        'message' : 'Not Found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success' : False,
        'error' : 400,
        'message' : 'Bad request'
    }), 400

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def not_authenticated(error):
    return jsonify({
      'success' : False,
      'error' : 401,
      'message' : 'Not Authenticated'
    }), 401


@app.errorhandler(403)
def not_allowed(error):
    return jsonify({
      'success' : False,
      'error' : 403,
      'message' : 'Not Allowed'
    }), 403
