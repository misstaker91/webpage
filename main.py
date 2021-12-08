import calendar
import os
import smtplib
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from forms import CalculationForm, SpravciLoginForm, ReservationForm, InfooHostechForm
from dotenv import load_dotenv
from flask_migrate import Migrate

load_dotenv()
app = Flask(__name__)

##Will see what to do with this

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# db migration if new column added follow flak-migrate
#migrate = Migrate(app, db)


class Association(UserMixin, db.Model):
    __tablename__ = 'association'
    apartmans_id = db.Column(ForeignKey('apartmans.id'), primary_key=True)
    dates_id = db.Column(ForeignKey('dates.id'), primary_key=True)
    is_reserved = db.Column(db.Boolean)
    child = relationship("Apartmans", back_populates="parents")
    parent = relationship("Dates", back_populates="children")
    jmeno = db.Column(db.String(250))
    email = db.Column(db.String(250))
    telefon = db.Column(db.String(250))
    infobody = db.Column(db.String(250))


class Apartmans(UserMixin, db.Model):
    __tablename__ = 'apartmans'
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(250), unique=False)
    img_url = db.Column(db.String(250))
    parents = relationship("Association", back_populates="child")


class Dates(UserMixin, db.Model):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    month = db.Column(db.Integer)
    yearr = db.Column(db.Integer)
    children = relationship("Association", back_populates="parent")


class Spravci(UserMixin, db.Model):
    __tablename__ = 'spravci'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


# db.create_all()

@login_manager.user_loader
def load_user(spravci_id):
    return Spravci.query.get(spravci_id)


bmi_dict = {'Podvaha': [0.0, 18.5], 'Normalni': [18.5, 25.0], 'Nadvaha': [25.1, 30.0], 'Obezita': [30.1, 50]}


class Kalendar():
    def __init__(self):
        self.kalendar = calendar.Calendar(firstweekday=0)
        self.momentalne = datetime.now()

    def create_kalendar(self):
        this_year = self.momentalne.year
        this_month = self.momentalne.month
        for y in range(0, 16):
            if this_month == 13:
                this_month = 1
                this_year += 1

            for x in self.kalendar.itermonthdays(year=this_year, month=this_month):
                if x != 0:
                    # print(f'{x} {this_month} {this_year}')
                    if Dates.query.filter_by(day=x, yearr=this_year, month=this_month).all():
                        pass
                    else:
                        me = Dates(day=x, month=this_month, yearr=this_year)
                        db.session.add(me)
                        db.session.commit()
            this_month += 1


class Apartmany():
    def __init__(self):
        new_apartman = ["Apartmán pro 4 osoby se soc. zařízením (1)", "Apartmán pro 4 osoby se soc. zařízením (2)",
                        "Pokoj pro 4 osoby bez soc. zařízení (1)", "Pokoj pro 4 osoby bez soc. zařízení (2)",
                        "Pokoj pro 4 osoby bez soc. zařízení (3)", "Pokoj pro 2 osoby bez soc. zařízení",
                        "Pokoj pro 3 osoby bez soc. zařízení", "Pokoj pro 6 osob bez soc. zařízení",
                        "Pokoj pro 9 osob bez soc. zařízení"]
        for x in new_apartman:
            me = Apartmans(name=x)
            db.session.add(me)
            db.session.commit()


class UpdateAssociatonTable():
    def __init__(self):
        self.all_apartmens = Apartmans.query.all()
        self.Dates = Dates.query.all()

        for x in self.Dates:
            for y in self.all_apartmens:

                if Association.query.filter_by(dates_id=x.id, apartmans_id=y.id).all():
                    pass
                else:
                    me = Association(dates_id=x.id, apartmans_id=y.id, is_reserved=False)
                    db.session.add(me)
                    db.session.commit()


# b = Apartmany()


@app.route('/', methods=['GET', 'POST'])
def index():
    valuebmi = 0
    form = CalculationForm()
    if request.method == "POST":
        vys = float(request.form.get('vyska'))
        vah = float(request.form.get('vaha'))
        vypocet_bmi = (vah / (vys * vys)) * 10000
        rounded_bmi = round(vypocet_bmi, 1)
        return render_template("index.html", form=form, rounded_bmi=rounded_bmi)
    return render_template("index.html", form=form)


##### Code for Schedule calendar
keep_pokoj = 1
this_year = datetime.now().year
this_month = datetime.now().month


@app.route('/schedule/', methods=['GET', 'POST'])
def schedule():
    global keep_pokoj
    global this_year
    global this_month
    global popisek_dne

    form = ReservationForm()
    form2 = InfooHostechForm()

    if request.args.get('rk') is not None:
        this_year = int(request.args.get('rk'))
    if request.args.get('msc') is not None:
        this_month = int(request.args.get('msc'))
    if request.args.get('appart') is not None:
        keep_pokoj = int(request.args.get('appart'))

    list_roku = []
    list_mesicu = []
    vyber_roka = Dates.query.order_by(Dates.yearr)
    vyber_mesicu = Dates.query.order_by(Dates.month)
    for x in vyber_roka:
        if x.yearr not in list_roku:
            list_roku.append(x.yearr)

    for y in vyber_mesicu:
        if y.month not in list_mesicu:
            list_mesicu.append(y.month)
    # for dropdown menu
    all_apartmens = Apartmans.query.all()
    # query apartmens and days
    apartments_query = Apartmans.query.filter_by(id=keep_pokoj).first()
    actual_days = Dates.query.filter_by(yearr=this_year, month=this_month).all()
    # konec query
    reservation_control = None

    if request.args.get("daynum") is not None:
        reservation_control = Association.query.join(Apartmans).filter_by(id=keep_pokoj).join(Dates).filter_by(
            yearr=this_year,
            month=this_month, day=int(request.args.get("daynum"))).first()

        if reservation_control.is_reserved:
            reservation_control.is_reserved = False
            db.session.commit()
            print(
                f'{current_user.name} {request.args.get("daynum")}/{this_month}/{this_year} - {apartments_query.name} Bez rezervace')
        else:
            reservation_control.is_reserved = True
            db.session.commit()
            print(
                f'{current_user.name} {request.args.get("daynum")}/{this_month}/{this_year} - {apartments_query.name} Zarezervovano')

    # vytvoreni zaznamu o hostech form

    if request.args.get("formnumber") == 'form2':
        print(f'validated')
        od = request.form.get('od')
        do = request.form.get('do')
        jmeno = request.form.get('name')
        email = request.form.get('email')
        telefon = request.form.get('telefon')
        popisek_dne = request.form.get('popisek_dne')
        pokoj = request.form.get('pokoj')
        parsed_od_list = od.split("-")
        parsed_do_list = do.split("-")
        od_year = int(parsed_od_list[0])
        od_month = int(parsed_od_list[1])
        od_day = int(parsed_od_list[2])
        do_year = int(parsed_do_list[0])
        do_month = int(parsed_do_list[1])
        do_day = int(parsed_do_list[2])

        rezervacni_filter = Association.query.join(Apartmans).join(Dates).filter(Apartmans.name == pokoj).filter(
            Dates.yearr.between(od_year, do_year)).filter(Dates.month.between(od_month, do_month)).filter(
            Dates.day.between(od_day, do_day)).all()

        for x in rezervacni_filter:
            x.is_reserved = True
            x.jmeno = jmeno
            x.email = email
            x.telefon = telefon
            x.infobody = popisek_dne
            db.session.commit()

    # rezervace form
    if form.validate_on_submit() and request.method == 'POST' and request.args.get("formnumber") == 'form1':
        print(f'validated')
        email = request.form.get('email')
        zprava = request.form.get('zprava')
        telefon = request.form.get('telefon')
        name = request.form.get('name')

        print(email, zprava, name, telefon)
        host = "smtp.gmail.com"
        with smtplib.SMTP(host) as connection:
            connection.starttls()
            connection.login(user=os.getenv('OWN_EMAIL'), password=os.getenv('OWN_PASSWORD'))
            connection.sendmail(from_addr=os.getenv('OWN_EMAIL'), to_addrs=os.getenv('OWN_EMAIL'),
                                msg=f"Subject:{name} {email} {telefon} \n\n {zprava}".encode('utf-8'))
        flash("Zpráva byla odeslána")

    return render_template("schedule.html", list_mesicu=list_mesicu, list_roku=list_roku, actual_days=actual_days,
                           this_year=this_year, this_month=this_month, all_apartmens=all_apartmens,
                           apartments_query=apartments_query, reservation_control=reservation_control,
                           keep_pokoj=keep_pokoj, form=form, form2=form2)


# prihlaseni pro spravce
"""
spravce = Spravci(name='Jan', email='petrik.janyk@gmail.com', password='.Misstaker91')
db.session.add(spravce)
db.session.commit()
"""

db_updated = False


@app.route('/spravci/login', methods=['GET', 'POST'])
def login_spravce():
    global db_updated
    form = SpravciLoginForm()
    if form.validate_on_submit() and request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        spravce = Spravci.query.filter_by(email=email).first()
        if not spravce:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login_spravce'))
        # Password incorrect
        elif not spravce.password == password:
            flash('Password incorrect, please try again.')
            return redirect(url_for('login_spravce'))
        # Email exists and password correct
        else:
            login_user(spravce)
            return redirect(url_for('index'))
    if request.args.get('template_update_db') is not None:
        kalendar_update = Kalendar()
        kalendar_update.create_kalendar()
        update_associationg_table = UpdateAssociatonTable()
        update_associationg_table
        db_updated = True

    return render_template("login_spravci.html", form=form, db_updated=db_updated)


@login_required
@app.route('/spravci/info/<hosti_id>/<hosti_id2>', methods=['GET', 'POST'])
def infohosti(hosti_id, hosti_id2):
    filterino = Association.query.filter_by(apartmans_id=hosti_id, dates_id=hosti_id2).first()

    return render_template('infoohostetech.html', filterino=filterino)


@login_required
@app.route('/spravci/deleteinfo', methods=['GET', 'POST'])
def deleteinfo():
    hosti_id = request.args.get('deleteapartment')
    hosti_id2 = request.args.get('deletedate')
    filterino = Association.query.filter_by(apartmans_id=hosti_id, dates_id=hosti_id2).first()
    """
    db.session.delete(filterino.jmeno)
    db.session.delete(filterino.email)
    db.session.delete(filterino.telefon)
    db.session.delete(filterino.infobody)
    filterino.is_reserved = False
    """
    print(filterino.jmeno, filterino.email, filterino.telefon, filterino.infobody)
    filterino.jmeno = None
    filterino.email = None
    filterino.telefon = None
    filterino.infobody = None
    filterino.is_reserved = False
    db.session.commit()
    return redirect(url_for('schedule'))


@app.route('/spravci/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
