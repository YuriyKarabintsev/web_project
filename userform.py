from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, IntegerField, StringField, DateField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    id = IntegerField("Id", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    specialization = StringField("Область разработки", validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    hashed_password = PasswordField('Пароль', validators=[DataRequired()])
    modified_date = DateField("Дата", validators=[DataRequired()])
    submit = SubmitField("Отправить")