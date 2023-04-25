from flask import Flask
from flask import render_template, request
from loginform import LoginForm
import os
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
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)
api.add_resource(users_resource.UsersResource, '/api/users/<int:user_id>')
secure_filename('/uploads')

login_manager = LoginManager()
login_manager.init_app(app)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route("/")
def index():
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).all()
    blogs = sorted(blogs, key=lambda b: b.likes, reverse=True)
    return render_template("index.html", title="Main page", blogs=blogs, iden=current_user.id)


@app.route("/registration", methods=["GET","POST"])
def register(): # регистрация
    form = UserForm()
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = User(
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
def login(): # вход в аккаунт
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
def logout(): # выход из аккаунта
    logout_user()
    return redirect("/")

@app.route('/per_acc/<int:iden>', methods=['GET'])
def per_acc(iden): # отображение профиля какого-либо пользователя
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).filter(Blogs.user_id == iden)
    return render_template('per_acc.html', title="Личный кабинет", blogs=blogs, iden=iden)


@app.route('/add_blog',  methods=['GET', 'POST'])
@login_required
def add_blogs(): # добавление блога
    form = BlogsForm()
    if request.method == "POST":
        db_sess = db_session.create_session()
        blog = Blogs()
        blog.title = form.title.data
        blog.content = form.content.data
        blog.user_id = current_user.id
        blog.type = form.type.data
        blog.likes = 0
        current_user.blogs.append(blog)
        db_sess.merge(current_user)
        db_sess.commit()
        b = db_sess.query(Blogs).filter(Blogs.user_id == current_user.id)
        b = sorted(b, key=lambda x: x.id)
        b = [i.id for i in b]
        id_needed = max(b)
        if request.files:
            f = request.files['file']
            exp = f.filename.split(".")[-1]
            if os.path.exists("users_images/" + str(current_user.id)):
                f.save("users_images/" + str(current_user.id) + "/" + str(id_needed) + ".png")# + exp)
            else:
                os.mkdir("users_images/" + str(current_user.id))
                f.save("users_images/" + str(current_user.id) + "/" + str(id_needed) + ".png")# + exp)
            blog_needed = db_sess.get(Blogs, id_needed)
            blog_needed.img_name = str(id_needed) + '.png' #+ exp
            db_sess.commit()
            return redirect("/per_acc/" + str(current_user.id))
    return render_template('add_blog.html', title='Добавление блога',
                           form=form)

@app.route('/correct/<int:id>',  methods=['GET', 'POST'])
@login_required
def correct(id): # редактирование блога
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
    if request.method == "POST":
        db_sess = db_session.create_session()
        blogs = db_sess.query(Blogs).filter(Blogs.id == id,
                                          Blogs.user == current_user
                                          ).first()
        if blogs:
            blogs.title = form.title.data
            blogs.content = form.content.data
            blogs.type = form.type.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
        b = db_sess.query(Blogs).filter(Blogs.user_id == current_user.id)
        b = sorted(b, key=lambda x: x.id)
        b = [i.id for i in b]
        id_needed = max(b)
        if request.files:
            f = request.files['file']
            exp = f.filename.split(".")[-1]
            if os.path.exists("users_images/" + str(current_user.id)):
                f.save("users_images/" + str(current_user.id) + "/" + str(id_needed) + "." + exp)
            else:
                os.mkdir("users_images/" + str(current_user.id))
                f.save("users_images/" + str(current_user.id) + "/" + str(id_needed) + "." + exp)
            blog_needed = db_sess.get(Blogs, id_needed)
            blog_needed.img_name = str(id_needed) + '.png' #+ exp
            db_sess.commit()
            return redirect("/per_acc/" + str(current_user.id))
    return render_template('correct.html', title='Редактирование блога',
                           form=form)

@app.route('/blogs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def blogs_delete(id): # удаление блога
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).filter(Blogs.id == id,
                                      Blogs.user == current_user
                                      ).first()
    if blogs:
        if blogs.img_name and os.path.exists(f"users_images/{current_user.id}/{blogs.img_name}"):
            os.remove(f"users_images/{current_user.id}/{blogs.img_name}")
        db_sess.delete(blogs)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/per_acc/" + str(current_user.id))

@app.route("/plus_like/<int:id>", methods=["GET", "POST"])
@login_required
def plus_like(id): # функция обработки лайков
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).filter(Blogs.id == id).first()
    l = blogs.users_liked
    if l == None:
        l = ""
    if current_user.id != blogs.user_id and str(current_user.id) not in l:
        if not l:
            l = str(current_user.id) + ","
            blogs.users_liked = l
            db_sess.commit()
        blogs.likes += 1
        db_sess.commit()
    return redirect("/")


if __name__ == "__main__":
    db_session.global_init("db/data_of_site.db")
    db_sess = db_session.create_session()
    app.run()