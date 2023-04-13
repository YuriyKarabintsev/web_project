import flask
import flask_login
from flask import Flask
from flask import render_template, request, jsonify
from flask_bootstrap import Bootstrap
from loginform import LoginForm
# from jobsform import JobsForm
from userform import UserForm
from data.users import User
from data import db_session
from flask_login import login_user, login_required, logout_user
from flask import redirect
from flask_login import LoginManager

import flask
import flask_login
from flask import Flask
from flask import render_template, request, jsonify
from loginform import LoginForm
#from jobsform import JobsForm
from userform import UserForm
from data.users import User
from data.news import News
from data import db_session
from flask_login import login_user, login_required, logout_user
from flask import redirect
from flask_login import LoginManager
import users_resource
from flask_restful import Api

import os
import random
from data import db_session
from datetime import datetime

from data import __all_models

from flask import Flask, request, make_response
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = str(random.randint(100000000000000000, 100000000000000000000))
print('SECRET_KEY:', app.config['SECRET_KEY'])
bootstrap = Bootstrap(app)
db_session.global_init("db/users.sqlite")
users = {}
db_session.global_init("db/users.sqlite")


def chec_cooke_user_data():
    global users
    for i in users.keys():
        ip, out, time = users[i]
        now = datetime.now()
        if not time.year == now.year and now.month == time.month:
            users.pop(i)




def cookie_get_login():
    uid = request.cookies.get('uid')
    chec_cooke_user_data()
    global users
    try:
        id, ip, time = users[uid]
    except IndexError:
        return None

    if ip != request.remote_addr:
        users.pop(uid)
        return None
    return id


@app.route("/")
def root():
    return '132'


@app.route("/client_ip")
def client_ip():
    return request.remote_addr


@app.route("/login")
def login():
    registration = False
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data): # атрибуты для задачи
            login_user(user, remember=form.remember_me.data)

            global users
            uid = random.randint(100000000000000000, 100000000000000000000)
            with uid in users.keys():
                uid = random.randint(100000000000000000, 100000000000000000000)

            users[uid] = [user.id, request.remote_addr, datetime.now()]  # логин юзера
            out = make_response('uid', uid, max_age=60 * 60 * 24 * 3)
            out.set_cookie()
            return redirect("/")
        return render_template('autorization.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('autorization.html', title='Авторизация', form=form, registration=registration)





@app.route("/singup")
def singupget():
    form = UserForm()
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = User(
            id=form.id.data,
            surname=form.surname.data,
            name=form.name.data,
            specialization=form.specialization.data,
            email=form.email.data,
            modified_date=form.modified_date.data
        )
        user.set_password(form.hashed_password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template("registration.html", form=form, title="Registration")


@app.route("/nev_posdt")
def nev_posdt():
    db_sess = db_session.create_session()
    news = News(title="Первая новость", content="Привет блог!", user_id=1)
    db_sess.add ( news )
    db_sess.commit ()
    return '54'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
