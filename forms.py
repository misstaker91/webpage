from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, TextAreaField, DateField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm Calculating BMI
class CalculationForm(FlaskForm):
    vyska = IntegerField("vyska", validators=[DataRequired()])
    vaha = IntegerField("vaha", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


##Form for spravci login
class SpravciLoginForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    submit = SubmitField("Prihlasit se")


# Reservation form
class ReservationForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    telefon = IntegerField("Tel. číslo", validators=[DataRequired()])
    zprava = TextAreaField("", validators=[DataRequired()])
    submit = SubmitField("")


class InfooHostechForm(FlaskForm):
    od = DateField("Od", format='%Y-%m-%d', validators=[DataRequired()])
    do = DateField("Do", format='%Y-%m-%d', validators=[DataRequired()])
    jmeno = StringField("Jméno", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    telefon = IntegerField("Tel. číslo", validators=[DataRequired()])
    popisek_dne = TextAreaField("", validators=[DataRequired()])
    pokoj = StringField('pokoj', validators=[DataRequired()])
    submit = SubmitField("")


class Hledac(FlaskForm):
    od = DateField("Od", format='%Y-%m-%d', validators=[DataRequired()])
    do = DateField("Do", format='%Y-%m-%d', validators=[DataRequired()])

    submit = SubmitField("")
