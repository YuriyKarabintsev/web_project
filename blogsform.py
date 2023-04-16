from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired


class BlogsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    user_id = IntegerField("ID создателя")
    type = StringField("Тип записи")
    submit = SubmitField('Готово')