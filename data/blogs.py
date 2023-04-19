import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Blogs(SqlAlchemyBase):
    __tablename__ = 'blogs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    type = sqlalchemy.Column(sqlalchemy.String, default="note")
    likes = sqlalchemy.Column(sqlalchemy.Integer)
    users_liked = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relationship('User')