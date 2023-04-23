from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired


class BlogsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    user_id = IntegerField("ID создателя")
    type = SelectField("Тип записи", choices=["Project", "Question", "Note", "Vacancy"])
    submit = SubmitField('Готово')