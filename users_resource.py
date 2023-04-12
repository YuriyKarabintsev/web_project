from data import db_session
from data.users import User
from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from parsing_resources import parser


def abort_if_users_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"Users {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'user': users.to_dict(
            only=("id", "name", "surname", "age", "position", "speciality", "address", "email", "hashed_password", "modified_date"))})