import calendar
import os
import smtplib
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from forms import CalculationForm, SpravciLoginForm, ReservationForm, InfooHostechForm, Hledac
from dotenv import load_dotenv
# google
from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_migrate import Migrate
import time

load_dotenv()
app = Flask(__name__)

##Will see what to do with this

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
####google code
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


# end google code
# db migration if new column added follow flak-migrate
# migrate = Migrate(app, db)


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


#db.create_all()

@login_manager.user_loader
def load_user(spravci_id):
    return Spravci.query.get(spravci_id)


class Kalendar():
    def __init__(self):
        self.kalendar = calendar.Calendar(firstweekday=0)
        self.momentalne = datetime.now()

    def create_kalendar(self):
        this_year = self.momentalne.year
        this_month = self.momentalne.month
        for y in range(0, 16):
            print(y)
            if this_month == 13:
                this_month = 1
                this_year += 1

            for x in self.kalendar.itermonthdays(year=this_year, month=this_month):
                if x != 0:
                    print(f'{x} {this_month} {this_year}')
                    if Dates.query.filter_by(day=x, yearr=this_year, month=this_month).all():
                        pass
                    else:
                        me = Dates(day=x, month=this_month, yearr=this_year)
                        db.session.add(me)
                        db.session.commit()
            this_month += 1


#kalendar_update = Kalendar()
#kalendar_update.create_kalendar()
"""
new_apartman = ["Apartmán pro 4 osoby se soc. zařízením (3)", "Apartmán pro 4 osoby se soc. zařízením (4)",
                        "Pokoj pro 4 osoby bez soc. zařízení (1)", "Pokoj pro 4 osoby bez soc. zařízení (2)",
                        "Pokoj pro 4 osoby bez soc. zařízení (8)", "Pokoj pro 2 osoby bez soc. zařízení (7)",
                        "Pokoj pro 3 osoby bez soc. zařízení (9)", "Pokoj pro 6 osob bez soc. zařízení (6)",
                        "Pokoj pro 8 osob bez soc. zařízení (5)"]
for x in new_apartman:
    print(x)
    me = Apartmans(name=x)
    db.session.add(me)
    db.session.commit()

"""
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

#tableup = UpdateAssociatonTable()

@app.route('/', methods=['GET', 'POST'])
def index():
    title = "Penzion u Königsmarků"
    content = "Rodinný penzion U Königsmarků, ubytování v Hořejším Vrchlabí hned vedle lyžařského areálu " \
              "Herlíkovice-Bubákov "
    volne_apartmany_list = []
    form = Hledac()
    form2 = ReservationForm()
    od = None
    do = None
    if form.validate_on_submit() and request.method == "POST" and request.args.get("formnumber") == 'form3':
        od = request.form.get('od')
        do = request.form.get('do')

        parsed_od_list = od.split("-")
        parsed_do_list = do.split("-")
        od_year = int(parsed_od_list[0])
        od_month = int(parsed_od_list[1])
        od_day = int(parsed_od_list[2])
        do_year = int(parsed_do_list[0])
        do_month = int(parsed_do_list[1])
        do_day = int(parsed_do_list[2])

        for mm in range(1, 10):
            pid1res = 0
            rezervacni_filter = Association.query.join(Apartmans).join(Dates).filter(Apartmans.id == mm).filter(
                Dates.yearr.between(od_year, do_year)).filter(Dates.month.between(od_month, do_month)).filter(
                Dates.day.between(od_day, do_day)).all()
            # print(od, do, od_day, do_day)
            # print(rezervacni_filter)

            for x in rezervacni_filter:
                if x.is_reserved:
                    pid1res += 1
                    # print(f'pid1res +=1 {pid1res} {mm}')

            if pid1res == 0:
                # print(f'pid1res == 0 {pid1res} {mm}')

                volne_apartmany = Apartmans.query.filter_by(id=mm).first()
                volne_apartmany_list.append(volne_apartmany.name)

    if request.method == 'POST' and request.args.get("formnumber") == 'form4':
        email = request.form.get('email')
        zprava = request.form.get('zprava')
        telefon = request.form.get('telefon')
        name = request.form.get('name')

        # print(email, zprava, name, telefon)

        emailMsg = f'{zprava}'
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] = 'Konigsmarkovi@penzionvrchlabi.cz'
        mimeMessage['subject'] = f'{name} {email} {telefon} '
        mimeMessage.attach(MIMEText(emailMsg, 'plain'))
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

        message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        # print(f'hello world')
        flash("Zpráva byla odeslána")
        return redirect(url_for('index'))

    # print(form.errors)
    # print(volne_apartmany_list)
    return render_template("index.html", form=form, form2=form2, volne_apartmany_list=volne_apartmany_list, od=od,
                           do=do,
                           title=title, content=content)


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
    title = "Penzion u Königsmarků - Ubytování"
    content = "Prohlédněte si volné termíny ubytování a naplánujte vaši dovolenou, školu v přírodě, lyžařský kurz, " \
              "svatbu nebo firemní akci na horách v rodinném penzionu U Königsmarků"

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
            # print( f'{current_user.name} {request.args.get("daynum")}/{this_month}/{this_year} - {
            # apartments_query.name} Bez rezervace')
        else:
            reservation_control.is_reserved = True
            db.session.commit()
            # print( f'{current_user.name} {request.args.get("daynum")}/{this_month}/{this_year} - {
            # apartments_query.name} Zarezervovano')

    # vytvoreni zaznamu o hostech form

    if request.method == 'POST' and request.args.get("formnumber") == 'form2':
        # print(f'validated')
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

    # print(form.errors)
    # rezervace form
    if form.validate_on_submit() and request.method == 'POST' and request.args.get("formnumber") == 'form1':
        email = request.form.get('email')
        zprava = request.form.get('zprava')
        telefon = request.form.get('telefon')
        name = request.form.get('name')

        # print(email, zprava, name, telefon)

        emailMsg = f'{zprava}'
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] = 'Konigsmarkovi@penzionvrchlabi.cz'
        mimeMessage['subject'] = f'{name} {email} {telefon} '
        mimeMessage.attach(MIMEText(emailMsg, 'plain'))
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

        message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        flash("Zpráva byla odeslána")
        return redirect(url_for('index'))

    return render_template("schedule.html", list_mesicu=list_mesicu, list_roku=list_roku, actual_days=actual_days,
                           this_year=this_year, this_month=this_month, all_apartmens=all_apartmens,
                           apartments_query=apartments_query, reservation_control=reservation_control,
                           keep_pokoj=keep_pokoj, form=form, form2=form2, title=title, content=content)


# prihlaseni pro spravce
"""
spravce = Spravci(name='j', email='j@j', password='j')
db.session.add(spravce)
db.session.commit()
"""
# delete all reserved data
"""
delete_all_reserved_data = Association.query.all()
print(delete_all_reserved_data)
for delete_data in delete_all_reserved_data:
    delete_data.is_reserved = False
    db.session.commit()
"""
delete_all_reserved_data = Association.query.all()
print(len(delete_all_reserved_data))
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
    # print(filterino.jmeno, filterino.email, filterino.telefon, filterino.infobody)
    filterino.jmeno = None
    filterino.email = None
    filterino.telefon = None
    filterino.infobody = None
    filterino.is_reserved = False
    db.session.commit()
    return redirect(url_for('schedule'))


@app.route('/svatby')
def svatby():
    title = "Penzion u Königsmarků - Svatby a Firemní akce"
    content = "Svatby a firemní akce na horách v rodinném penzionu U Königsmarků."
    return render_template("svatby.html", title=title, content=content)


@app.route('/fotogalerie')
def fotogalerie():
    title = "Penzion u Königsmarků - Fotogalerie"
    content = "Prohlédněte si naši fotogalerii - Rodinný penzion U Königsmarků, ubytování v Hořejším Vrchlabí hned " \
              "vedle lyžařského areálu Herlíkovice-Bubákov "
    return render_template("fotogalerie.html", title=title, content=content)


@app.route('/cenik')
def cenik():
    title = "Penzion u Königsmarků - Ceník"
    content = "Ceník ubytování v rodinném penzionu U Königsmarků"
    return render_template("cenik.html", title=title, content=content)


@app.route('/spravci/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))




if __name__ == "__main__":
    app.run(debug=True)
