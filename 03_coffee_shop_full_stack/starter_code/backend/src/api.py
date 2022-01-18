import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

SHORT_DESC = 0
LONG_DESC = 1

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()


def get_drinks_from_db(desc_type):
    drinks = Drink.query.order_by(Drink.id).all()
    if desc_type == SHORT_DESC:
        formatted_drinks = [drink.short() for drink in drinks]
    else:
        formatted_drinks = [drink.long() for drink in drinks]

    return formatted_drinks

# ROUTES


@app.route('/')
def hello():
    return jsonify({'message': 'Hello World from CoffeeShop Application!'})


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks or appropriate status code
        indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_all_drinks():

    drinks = get_drinks_from_db(SHORT_DESC)

    count = len(drinks)

    if count == 0:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks or appropriate status code
        indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_all_drinks_long(jwt):

    drinks = get_drinks_from_db(LONG_DESC)

    count = len(drinks)

    if count == 0:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_newdrink(jwt):

    newDrinkReq = request.get_json()
    title = newDrinkReq['title']
    recipe = str(newDrinkReq['recipe'])

    newDrink = Drink(
        title=title,
        recipe=recipe.replace("\'", "\""))

    try:
        newDrink.insert()
    except:
        print(sys.exc_info())
        abort(422)

    formattedNewDrink = newDrink.long()

    return jsonify({
        "success": True,
        "drinks": [formattedNewDrink]
    }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_specific_drink(jwt, id):

    newDrinkReq = request.get_json()

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)
    else:

        try:
            if 'title' in newDrinkReq:
                title = newDrinkReq['title']
                drink.title = title

            if 'recipe' in newDrinkReq:
                recipe = str(newDrinkReq['recipe'])
                drink.recipe = recipe.replace("\'", "\"")

            drink.update()
        except:
            abort(500)

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_specific_drink(jwt, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)
    else:
        try:
            drink.delete()
        except:
            abort(500)

        return jsonify({
            "success": True,
            "delete": id
        })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable_error(error):
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
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource Not Found'

    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def not_found_error(error):
    return jsonify(error.error), error.status_code


@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401


@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Forbidden'
    }), 403


@app.errorhandler(400)
def badrequest_error(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400


if __name__ == "__main__":
    app.debug = True
    app.run()
