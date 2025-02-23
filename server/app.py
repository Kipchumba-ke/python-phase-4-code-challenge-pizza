#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = [r.to_dict(only=("id", "name", "address")) for r in Restaurant.query.all()]
        response = make_response(jsonify(restaurants), 200,)
        return response
    
api.add_resource(Restaurants, "/restaurants")

class Restaurant_byId(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            return make_response(jsonify(restaurant.to_dict(rules=("restaurant_pizzas",))), 200)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            RestaurantPizza.query.filter_by(restaurant_id=id).delete()
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    
api.add_resource(Restaurant_byId, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        pizza = [p.to_dict() for p in Pizza.query.all()]
        response = make_response(pizza, 200,)
        return response
    

    
api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:
            new_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"],
            )
            db.session.add(new_pizza)
            db.session.commit()

            response_data = new_pizza.to_dict(rules=("pizza", "restaurant"))
            return make_response(jsonify(response_data), 201)

        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")






if __name__ == "__main__":
    app.run(port=5555, debug=True)
