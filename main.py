import flask
import flask_login
from flask import Flask
from flask import render_template, request, jsonify
from loginform import LoginForm
#from jobsform import JobsForm
from userform import UserForm
from data.users import User
from data import db_session
from flask_login import login_user, login_required, logout_user, current_user
from flask import redirect
from flask_login import LoginManager
import users_resource
from flask_restful import Api, abort
from data.blogs import Blogs
from blogsform import BlogsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
api.add_resource(users_resource.UsersResource, '/api/users/<int:user_id>')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route("/")
def index():
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).all()
    return render_template("index.html", title="Main page", blogs=blogs)


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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/per_acc', methods=['GET'])
def per_acc():
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).all()
    print(blogs, "ALL BLOGS")
    return render_template('per_acc.html', title="Личный кабинет", blogs=blogs)

@app.route('/add_blog',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = BlogsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        blog = Blogs()
        blog.title = form.title.data
        blog.content = form.content.data
        blog.user_id = form.user_id.data
        blog.type = form.type.data
        blog.likes = 0
        current_user.blogs.append(blog)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/per_acc')
    return render_template('add_blog.html', title='Добавление блога',
                           form=form)

@app.route('/correct/<int:id>',  methods=['GET', 'POST'])
@login_required
def correct(id):
    form = BlogsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        blogs = db_sess.query(Blogs).filter(Blogs.id == id,
                                          Blogs.user == current_user
                                          ).first()
        if blogs:
            form.title.data = blogs.title
            form.content.data = blogs.content
            form.user_id.data = blogs.user_id
            form.type.data = blogs.type
        else:
            abort(404)
    print(form.validate_on_submit(), "состояние формы")
    if form.validate_on_submit():
        print("ОТПРАВЛЕНО")
        db_sess = db_session.create_session()
        blogs = db_sess.query(Blogs).filter(Blogs.id == id,
                                          Blogs.user == current_user
                                          ).first()
        if blogs:
            print("РЕДАКТИРОВАНИЕ")
            blogs.title = form.title.data
            blogs.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('correct.html', title='Редактирование блога',
                           form=form)

@app.route('/blogs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def blogs_delete(id):
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).filter(Blogs.id == id,
                                      Blogs.user == current_user
                                      ).first()
    if blogs:
        db_sess.delete(blogs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/per_acc')

@app.route("/plus_like/<int:id>", methods=["GET", "POST"])
@login_required
def plus_like(id):
    db_sess = db_session.create_session()
    print(id, "ID OF BLOG")
    blogs = db_sess.query(Blogs).filter(Blogs.id == id).first()
    l = blogs.users_liked
    print(current_user.id, blogs.user_id, l)
    if current_user.id != blogs.user_id and str(current_user.id) not in l:
        print("PLUS LIKES")
        if not l:
            l = str(current_user.id) + ","
            blogs.users_liked = l
        print(l, "THEY LIKE!")
        blogs.likes += 1
        db_sess.commit()
    return redirect("/")


if __name__ == "__main__":
    db_session.global_init("db/data.db")

    '''blog = Blogs()
    blog.id = 1
    blog.title = "Автоматическая система по уходу за растениями"
    blog.content = "Проект, осуществляющий полный уход за растениями: полив, подача удобрений, освещение, защита от " \
                   "солнца, передача данных о состоянии окружающей среды в интернет. Проект разработан с помощью" \
                   "плат Arduino Mega и Wemos."
    blog.user_id = 1
    blog.type = "project"
    db_sess = db_session.create_session()
    db_sess.add(blog)
    db_sess.commit()'''
    db_sess = db_session.create_session()
    for blog in db_sess.query(Blogs):
        print(blog.id, blog.content, blog.type, blog.likes)
    b = db_sess.query(Blogs).filter(Blogs.id == 1).first()
    b.users_liked = ""
    db_sess.commit()


    app.run()