from data import db_session
from data.news import News
from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from parsing_resources import parser


def abort_if_users_not_found(user_id):
    session = db_session.create_session()
    users = session.query(News).get(user_id)
    if not users:
        abort(404, message=f"News {user_id} not found")


class BlogsResources(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(News).get(user_id)
        return jsonify({'blogs': users.to_dict(
            only=("id", "title", "name", "content", "created_date", "user_id", "user"))})