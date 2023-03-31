import flask
import flask_login
from flask import Flask
from flask import render_template, request, jsonify
from loginform import LoginForm
#from jobsform import JobsForm
from userform import UserForm
from data.users import User
from data import db_session
from flask_login import login_user, login_required, logout_user
from flask import redirect
from flask_login import LoginManager
#from data.jobs import Jobs
#from data import jobs_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route("/")
def index():
    db_sess = db_session.create_session()
    return render_template("index.html", title="Main page")


@app.route("/registration", methods=["GET","POST"])
def register():
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    registration = False
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data): # атрибуты для задачи
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('autorization.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('autorization.html', title='Авторизация', form=form, registration=registration)


if __name__ == "__main__":
    db_session.global_init("db/users.sqlite")
    app.run()