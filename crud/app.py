from flask_cors import CORS
from crud.utils import query_all, query_one_filtered
from crud.models import setup_db, Person
from crud.schemas import RegisterSchema, QuerySchema
from flask import Flask, jsonify, request, abort
from pydantic import ValidationError


def create_app():
    app = Flask(__name__)
    with app.app_context():
        setup_db(app)
    CORS(app)

    @app.route("/api")
    def get_all_persons():
        try:
            persons = query_all(Person)
        except Exception as e:
            return jsonify({"status": "500", "error": "something went wrong"}), 500

        return (
            jsonify(
                {
                    "message": "success",
                    "persons": [person.format() for person in persons]
                    if persons
                    else [],
                }
            ),
            200,
        )

    @app.route("/api", methods=["POST"])
    def create_person():
        data = request.get_json()
        try:
            data = RegisterSchema(**data)
            person = Person(data.name)
            person.insert()

            return (
                jsonify({"message": "success", "name": person.name, "id": person.id}),
                201,
            )
        except ValidationError as e:
            msg = ""
            for err in e.errors():
                msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
            return (
                jsonify({"error": "Bad Request", "message": msg}),
                400,
            )
        except Exception as e:
            print(e)
            abort(500)

    @app.route("/api/<int:user_id>", methods=["GET"])
    def get_person(user_id):
        query = QuerySchema(user_id=user_id)
        try:
            person = query_one_filtered(Person, id=query.user_id)
            if person is None:
                return (
                    jsonify(
                        {
                            "error": "Resource not found",
                            "message": "Person does not exist",
                        }
                    ),
                    404,
                )

            return jsonify({"message": "success", "person": person.format()}), 200
        except ValidationError as e:
            msg = ""
            for err in e.errors():
                msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
            return (
                jsonify({"error": "Bad Request", "message": msg}),
                400,
            )
        except Exception as e:
            print(e)
            abort(500)

    @app.route("/api/<int:user_id>", methods=["PATCH"])
    def update_person(user_id):
        try:
            query = QuerySchema(user_id=user_id)
            data = RegisterSchema(**request.get_json())
            person = query_one_filtered(Person, id=query.user_id)
            if person is None:
                return (
                    jsonify(
                        {
                            "error": "Resource not found",
                            "message": "Person does not exist",
                        }
                    ),
                    404,
                )
            person.name = data.name
            person.update()
            return (
                jsonify(
                    {"message": "name updated", "id": person.id, "name": person.name}
                ),
                200,
            )
        except ValidationError as e:
            msg = ""
            for err in e.errors():
                msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
            return (
                jsonify({"error": "Bad Request", "message": msg}),
                400,
            )
        except Exception as e:
            print(e)
            abort(500)

    @app.route("/api/<int:user_id>", methods=["DELETE"])
    def delete_person(user_id):
        try:
            query = QuerySchema(user_id=user_id)
            person = query_one_filtered(Person, id=query.user_id)
            if person is None:
                return (
                    jsonify(
                        {
                            "error": "Resource not found",
                            "message": "Person does not exist",
                        }
                    ),
                    404,
                )
            person.delete()
            return jsonify({"message": "deleted", "id": user_id}), 200
        except ValidationError as e:
            msg = ""
            for err in e.errors():
                msg += f"{str(err.get('loc')).strip('(),')}:{err.get('msg')}, "
            return (
                jsonify({"error": "Bad Request", "message": msg}),
                400,
            )
        except Exception as e:
            print(e)
            abort(500)

    @app.errorhandler(404)
    def Not_Found(err):
        return jsonify({"error": err.name, "message": err.description}), err.code

    @app.errorhandler(405)
    def method_not_allowed(err):
        return jsonify({"error": err.name, "message": err.description}), err.code

    @app.errorhandler(500)
    def server_error(err):
        return jsonify({"error": err.name, "message": err.description}), err.code

    return app
