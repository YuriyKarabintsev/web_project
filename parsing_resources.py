from flask_restful import reqparse


parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('name', required=True, type=str)
parser.add_argument('specialization', required=True, type=str)
parser.add_argument("email", required=True, type=str)
parser.add_argument("hashed_password", required=True, type=str)
parser.add_argument("modified_date", required=True, type=str)