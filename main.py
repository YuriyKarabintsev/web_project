import flask
import flask_login
from flask import Flask
from flask import render_template, request, jsonify, flash, url_for
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

def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    blogs = db_sess.query(Blogs).filter(Blogs.user_id == current_user.id)
    print(blogs, "ALL BLOGS")
    return render_template('per_acc.html', title="Личный кабинет", blogs=blogs)

@app.route('/add_blog',  methods=['GET', 'POST'])
@login_required
def add_blogs():
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
    if request.method == "POST":#form.validate_on_submit():
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
    print("HERE IS THE END")
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
    print(current_user.id, blogs.user_id, "users like", l)
    if l == None:
        l = ""
    if current_user.id != blogs.user_id and str(current_user.id) not in l:
        print("PLUS LIKES")
        if not l:
            l = str(current_user.id) + ","
            blogs.users_liked = l
            db_sess.commit()
        print(l, "THEY LIKE!")
        blogs.likes += 1
        db_sess.commit()
    return redirect("/")

@app.route('/photo', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # проверим, передается ли в запросе файл
        if 'file' not in request.files:
            # После перенаправления на страницу загрузки
            # покажем сообщение пользователю
            flash('Не могу прочитать файл')
            return redirect(request.url)
        file = request.files['file']
        # Если файл не выбран, то браузер может
        # отправить пустой файл без имени.
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # безопасно извлекаем оригинальное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл
            print(file, filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # если все прошло успешно, то перенаправляем
            # на функцию-представление `download_file`
            # для скачивания файла
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Загрузить новый файл</title>
    <h1>Загрузить новый файл</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    '''


if __name__ == "__main__":
    db_session.global_init("db/data.db")
    db_sess = db_session.create_session()
    for blog in db_sess.query(Blogs):
        print(blog.id, blog.content, blog.type, blog.likes)

    app.run()