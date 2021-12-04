from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm Calculating BMI
class CalculationForm(FlaskForm):
    vyska = IntegerField("vyska", validators=[DataRequired()])
    vaha = IntegerField("vaha", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


##Form for spravci login
class SpravciLoginForm(FlaskForm):
    name = StringField("Jmeno", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    submit = SubmitField("Prihlasit se")

