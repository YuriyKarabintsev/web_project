from data import db_session
from data.blogs import Blogs
from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from parsing_resources import parser


def abort_if_blogs_not_found(id):
    session = db_session.create_session()
    blogs = session.query(Blogs).get(id)
    if not blogs:
        abort(404, message=f"Blogs {id} not found")


class BlogsResources(Resource):
    def get(self, blog_id):
        abort_if_blogs_not_found(blog_id)
        session = db_session.create_session()
        blogs = session.query(Blogs).get(blog_id)
        return jsonify({'blogs': blogs.to_dict(
            only=("id", "title", "content", "created_date",
                  "user_id", "type", "likes", "users_liked", "user", "img_name"))})

    def delete(self, blog_id):
        abort_if_blogs_not_found(blog_id)
        session = db_session.create_session()
        blogs = session.query(Blogs).get(blog_id)
        session.delete(blogs)
        session.commit()
        return jsonify({'success': 'OK'})


class BlogsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        blogs = session.query(Blogs).all()
        return jsonify({'blogs': [item.to_dict(
            only=("id", "title", "content", "created_date",
                  "user_id", "type", "likes", "users_liked", "user", "img_name")) for item in blogs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        blogs = Blogs(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            type=args["type"],
            likes=args["likes"],
            users_liked=args["users_liked"],
            img_name=args["img_name"]
        )
        session.add(blogs)
        session.commit()
        return jsonify({'success': 'OK'})