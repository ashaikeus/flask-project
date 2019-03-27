from datetime import *
from sqlite3 import *
from flask import (Flask, request, render_template_string, render_template,
                   flash, redirect, url_for, json)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, BooleanField,
                     SubmitField, FileField, DateField, IntegerField)
from wtforms.validators import *
from flask_user import *
from flask_login import login_user, LoginManager
from werkzeug import generate_password_hash, check_password_hash
from urllib.parse import unquote


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    # remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddCharForm(FlaskForm):
    image = FileField('Изображение', default=None)
    name = StringField('Имя', validators=[DataRequired()])
    description = TextAreaField('Описание', default='')
    source = StringField('Откуда этот персонаж?', default='')
    role = StringField('Роль в сюжете', default='неизвестно')
    appearance = TextAreaField('Когда впервые появляется в сюжете?',
                               default='неизвестно')
    birthdate = StringField('Дата рождения', default='неизвестно')
    height = StringField('Рост в сантиметрах', default='неизвестно')
    weight = StringField('Вес в килограммах', default='неизвестно')
    va = StringField('Актер озвучки', default='неизвестно')
    nicknames = StringField('Также известен как', default='неизвестно')
    submit = SubmitField('Добавить')


class ConfigClass(object):  # настройки веб-приложения 
    SECRET_KEY = 'madsalex-yandex-lyceum-project-3'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)    
app.config.from_object(__name__+'.ConfigClass')
session = {}
current_user = 'гость'

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   unique=True) # primary keys are required by SQLAlchemy
    password = db.Column(db.String(100))
    username = db.Column(db.String(25), unique=True)
    registration_date = db.Column(db.String(15))


class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True,
                   unique=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(2500))
    image = db.Column(db.String(500))
    source = db.Column(db.String(50))
    birthdate = db.Column(db.String(10))
    role = db.Column(db.String(50))
    appearance = db.Column(db.String(250))
    height = db.Column(db.String(10))
    weight = db.Column(db.String(5))
    va = db.Column(db.String(50))
    nicknames = db.Column(db.String(50))
    creation_date = db.Column(db.String(15))
    author_id = db.Column(db.Integer)
    author = db.Column(db.String(25))


db.create_all()

if not User.query.filter(User.username == 'admin').first():
    user = User(username='admin', password=generate_password_hash('9'),
                registration_date=str(date.today()))
    db.session.add(user)
    db.session.commit()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
 
def return_json(table):
    connection = connect("basic_app.sqlite")
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM {}".format(table))
    # fetch all or one we'll go for all.
    results = cursor.fetchall()
    return results

def find_by_id(id, table):
    table_list = return_json(table)
    for j in table_list:
        if j['id'] == id:
            return j

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    news_list = return_json('characters')
    return render_template('index.html', name=current_user, news=news_list)

@app.route('/add', methods=['GET', 'POST'])
@app.route('/add/', methods=['GET', 'POST'])
def add_character():
    try:
        if session['username']:
            pass
    except KeyError:
        return redirect('/login')
    form = AddCharForm()
    if form.validate_on_submit():
        try:
            db.session.add(Character(name=request.form.get('name'),
                                    description=request.form.get('description'),
                                    source=request.form.get('source'),
                                    birthdate=request.form.get('birthdate'),
                                    role=request.form.get('role'),
                                    appearance=request.form.get('appearance'),
                                    height=request.form.get('height'),
                                    weight=request.form.get('weight'),
                                    va=request.form.get('va'),
                                    nicknames=request.form.get('nicknames'),
                                    creation_date=str(date.today()),
                                    author_id=session['id'],
                                    author=session['username']))
            db.session.commit()
        except Exception:
            return render_template('add_character.html', form=form,
                                   name=current_user, wrong=True)
        return redirect('/characters')
    else:
        return render_template('add_character.html', form=form,
                               name=current_user)

@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@app.route('/edit_article/<int:id>/', methods=['GET', 'POST'])
def edit(id):
    if current_user == 'гость':
        return redirect('/login')
    form = AddCharForm()
    character = Character.query.filter_by(id=id)
    if form.validate_on_submit():
        character.update({'name': request.form.get('name'),
                          'description': request.form.get('description'),
                          'source': request.form.get('source'),
                          'birthdate': request.form.get('birthdate'),
                          'role': request.form.get('role'),
                          'appearance': request.form.get('appearance'),
                          'height': request.form.get('height'),
                          'weight': request.form.get('weight'),
                          'va': request.form.get('va'),
                          'nicknames': request.form.get('nicknames'),
                          'creation_date': str(date.today())})
        db.session.commit()
        return redirect('/characters/{}'.format(id))
    else:
        return render_template('edit.html', form=form, name=current_user)

@app.route('/sign_up', methods=['GET', 'POST'])
@app.route('/sign_up/', methods=['GET', 'POST'])
def register():
    pass

@app.route('/delete_article/<int:id>')
@app.route('/delete_article/<int:id>/')
def delete(id):
    if current_user != 'admin':
        return redirect('/login')
    character = Character.query.filter_by(id=id).first()
    db.session.delete(character)
    db.session.commit()
    news_list = return_json('characters')
    return render_template('index.html', name=current_user, news=news_list,
                           deleted=True)

@app.route('/logout')
@app.route('/logout/')
def logout():
    global session, current_user
    if current_user == 'гость':
        return redirect('/login')
    session.pop('username')
    current_user = 'гость'
    session.pop('id')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    global session, current_user
    try:
        if session['username']:
            return redirect('/')
    except KeyError:
        pass
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            current_user = session['username'] = user.username
            session['id'] = user.id
        else:
            return render_template('login.html', form=form, wrong=True,
                                   name=current_user)
        return redirect('/')
    else:
        return render_template('login.html', form=form, name=current_user)

@app.route('/characters')
@app.route('/characters/')
def characters():
    char_list = return_json('characters')
    return render_template('characters.html', characters=char_list,
                           name=current_user)

@app.route('/characters/<int:id>')
@app.route('/characters/<int:id>/')
def char_page(id):
    data = find_by_id(id, 'characters')
    return render_template('character_page.html', char_info=data,
                           name=current_user)

@app.route('/user/<int:id>')
@app.route('/user/<int:id>/')
def user_page(id):
    data = find_by_id(id, 'users')
    return render_template('user.html', user_info=data,
                           name=current_user)

# Start development web server
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
