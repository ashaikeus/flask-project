import datetime
from flask import (Flask, request, render_template_string, render_template,
                   flash, redirect, url_for, json)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import *
from flask_user import *
from flask_login import login_user, LoginManager
from werkzeug import generate_password_hash, check_password_hash
from urllib.parse import unquote


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


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
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    password = db.Column(db.String(100))
    username = db.Column(db.String(25), unique=True)

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Tag():  # db.Model):
    pass

db.create_all()

# if not User.query.filter(User.username == 'admin').first():
#    user = User(username='admin',
#                password=generate_password_hash('-+password+-'))
#    user.roles.append(Role(name='Admin'))
#    db.session.add(user)
#    db.session.commit()

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    with open("news.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    return render_template('index.html', name=current_user, news=news_list)

@app.route('/add')
@app.route('/add/')
def add_character():
    return render_template('add_character.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    global session, current_user
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            current_user = session['username'] = user.username
            print(current_user)
        else:
            return render_template('login.html', form=form, wrong=True)
        return redirect('/')
    else:
        return render_template('login.html', form=form)

@app.route('/characters')
@app.route('/characters/')
def characters():
    with open("news.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    print(news_list)
    return render_template('characters.html', characters=news_list)

@app.route('/characters/<name>')
@app.route('/characters/<name>/')
@app.route('/characters/<source>/<name>')
@app.route('/characters/<source>/<name>/')
def char_page(name, **source):
    with open("news.json", "rt", encoding="utf8") as f:
        value = json.loads(f.read())
        name = unquote(name)
        data = None
    for j in value:
        for i in value[j]:
            if i['name'] == name:
                data = i
                break
    print(data)
    return render_template('character_page.html', char_info=data)

# Start development web server
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
