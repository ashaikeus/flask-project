import datetime
from flask import (Flask, request, render_template_string, render_template,
                   flash, redirect, url_for, )
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import *
from flask_user import *
from flask_login import login_user, LoginManager
from werkzeug import generate_password_hash, check_password_hash


class ConfigClass(object):  # настройки веб-приложения 
    SECRET_KEY = 'madsalex-yandex-lyceum-project-3'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning
    USER_EMAIL_SENDER_NAME = 'Wikicharia'
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


def create_app():
    app = Flask(__name__)
    login_manager = LoginManager()
    login_manager.init_app(app)    
    app.config.from_object(__name__+'.ConfigClass')


    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)

    class User(db.Model, UserMixin):
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


    user_manager = UserManager(app, db, User)
    db.create_all()

    if not User.query.filter(User.username == 'admin').first():
        user = User(username='admin',
                    password=user_manager.hash_password('-+password+-'))
        user.roles.append(Role(name='Admin'))
        db.session.add(user)
        db.session.commit()

    # The Home page is accessible to anyone
    @app.route('/')
    def home_page():
        if current_user.is_authenticated:
            name = current_user()
        else:
            name = 'гость'
        return render_template('index.html', name=name)

    @app.route('/add')
    @login_required
    def add_character():
        return render_template('add_character.html')

    # The Admin page requires an 'Admin' role.
    @app.route('/admin')
    @roles_required('Admin')    # Use of @roles_required decorator
    def admin_page():
        return render_template_string("""
                {% extends "flask_user_layout.html" %}
                {% block content %}
                    <h2>Admin Page</h2>
                    <p><a href={{ url_for('user.register') }}>Register</a></p>
                    <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                    <p><a href={{ url_for('home_page') }}>Home Page</a> (accessible to anyone)</p>
                    <p><a href={{ url_for('member_page') }}>Member Page</a> (login_required: member@example.com / Password1)</p>
                    <p><a href={{ url_for('admin_page') }}>Admin Page</a> (role_required: admin@example.com / Password1')</p>
                    <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
                {% endblock %}
                """)

    @app.route('/login', methods=['GET', 'POST'])
    def login_post():
        form = LoginForm()
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            user = User.query.filter_by(username=username).first()
            if not user:
                flash('<div class="alert alert-danger" role="alert">Неверное имя пользователя или пароль</div>')
                return redirect('/login')
            login_user(user)
            return redirect('/')
        return render_template('login.html', form=form)

    return app


# Start development web server
if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=8080)
