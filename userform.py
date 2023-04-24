from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, IntegerField, StringField, DateField, SelectField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    specialization = SelectField("Область разработки", choices=["Frontender", "Backender",
    "Fullstack", "Machine learner", "Electronics engineer", "Other"])
    email = EmailField('Почта', validators=[DataRequired()])
    hashed_password = PasswordField('Пароль', validators=[DataRequired()])
    modified_date = DateField("Дата", validators=[DataRequired()])
    submit = SubmitField("Отправить")