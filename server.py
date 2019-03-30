from datetime import *
from sqlite3 import *
from flask import (Flask, request, render_template_string, render_template,
                   flash, redirect, url_for, json)
from flask_sqlalchemy import SQLAlchemy
from flask_user import *
from flask_login import login_user, LoginManager
from werkzeug import generate_password_hash, check_password_hash
from urllib.parse import unquote
from forms import LoginForm, RegForm, AddCharForm, AddComment


class ConfigClass(object):  # настройки веб-приложения
    SECRET_KEY = 'madsalex-yandex-lyceum-project-3'  # секретный ключ
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)  # инициализируем
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object(__name__+'.ConfigClass')  # задаем настройки
session = {}
current_user = 'гость'
db = SQLAlchemy(app)  # создание базы данных


class User(db.Model):  # класс пользователя
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   unique=True)  # primary keys are required by SQLAlchemy
    password = db.Column(db.String(100))
    username = db.Column(db.String(25), unique=True)
    registration_date = db.Column(db.String(15))
    about = db.Column(db.String(1000))


class Character(db.Model):  # класс персонажа
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
    age = db.Column(db.String(10))
    va = db.Column(db.String(50))
    nicknames = db.Column(db.String(50))
    creation_date = db.Column(db.String(15))
    author_id = db.Column(db.Integer)
    author = db.Column(db.String(25))
    likes = db.Column(db.Integer(), default=0)  # рейтинг


class Like(db.Model):  # лайк
    __tablename__ = 'likes'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True,
                   unique=True)
    char = db.Column(db.Integer, db.ForeignKey('characters.id'))
    user = db.Column(db.Integer, db.ForeignKey('users.id'))


class Comment(db.Model):  # комментарий
    __tablename__ = 'comments'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True,
                   unique=True)
    char = db.Column(db.Integer, db.ForeignKey('characters.id'))
    user = db.Column(db.String, db.ForeignKey('users.username'))
    content = db.Column(db.String(500))


db.create_all()  # создание всех таблиц

if not User.query.filter(
                        User.username == 'admin'
                        ).first():  # создание администратора
    user = User(username='admin', password=generate_password_hash('9'),
                registration_date=str(date.today()))
    db.session.add(user)
    db.session.commit()


def dict_factory(cursor, row):  # вспомогательная функция
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def return_json(table):  # возвращение данных из БД в формате JSON
    connection = connect("basic_app.sqlite")
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM {}".format(table))
    results = cursor.fetchall()
    print(results)
    return results


def find_by_id(id, table):  # нахождение персонажа или пользователя по ID
    table_list = return_json(table)
    for j in table_list:
        if j['id'] == id:
            return j


@app.route('/')
def home_page():  # заглавная страница
    news_list = reversed(return_json('characters'))
    max_likes_func = db.session.query(db.func.max(Character.likes)).scalar()
    max_liked = db.session.query(Character).filter(
        Character.likes == max_likes_func).first()
    return render_template('index.html', name=current_user, news=news_list,
                           fav=max_liked)


@app.route('/add', methods=['GET', 'POST'])
@app.route('/add/', methods=['GET', 'POST'])  # добавление персонажа
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
                                     description=request.form.get(
                                         'description'),
                                     source=request.form.get('source'),
                                     image=request.form.get('image'),
                                     birthdate=request.form.get('birthdate'),
                                     role=request.form.get('role'),
                                     appearance=request.form.get('appearance'),
                                     height=request.form.get('height'),
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
def edit(id):  # изменение уже существующего персонажа
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
                          'va': request.form.get('va'),
                          'nicknames': request.form.get('nicknames'),
                          'creation_date': str(date.today())})
        db.session.commit()
        return redirect('/characters/{}'.format(id))
    else:
        return render_template('edit.html', form=form, name=current_user)


@app.route('/sign_up', methods=['GET', 'POST'])
@app.route('/sign_up/', methods=['GET', 'POST'])
def register():  # регистрация
    global session, current_user
    if current_user != 'гость':
        return redirect('/')
    form = RegForm()
    if form.validate_on_submit():
        try:
            assert request.form.get('password') == request.form.get(
                'password2')
            db.session.add(User(username=request.form.get('username'),
                                password=generate_password_hash(
                                    request.form.get('password')),
                                about=request.form.get('about'),
                                registration_date=str(date.today())))
            db.session.commit()
        except Exception:
            return render_template('sign_up.html', form=form,
                                   name=current_user, wrong=True)
        return redirect('/')
    return render_template('sign_up.html', form=form, name=current_user,
                           wrong=False)


@app.route('/delete_article/<int:id>')
@app.route('/delete_article/<int:id>/')
def delete(id):  # удаление
    if current_user != 'admin':
        return redirect('/login')
    character = Character.query.filter_by(id=id).first()
    db.session.delete(character)
    db.session.commit()
    news_list = return_json('characters')
    max_liked = db.session.query(Character).filter(
        Character.likes == max_likes_func).first()
    return render_template('index.html', name=current_user, news=news_list,
                           deleted=True, fav=max_liked)


@app.route('/logout')
@app.route('/logout/')
def logout():  # выход из аккаунта
    global session, current_user
    if current_user == 'гость':
        return redirect('/login')
    session.pop('username')
    current_user = 'гость'
    session.pop('id')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():  # вход в аккаунт
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
@app.route('/characters/page/<int:page>')
@app.route('/characters/page/<int:page>/')
def characters(page=1):  # страница со списком персонажей
    char_list = Character.query.order_by(Character.name.asc())
    char_list = char_list.paginate(page, 6, error_out=False).items
    return render_template('characters.html', characters=char_list,
                           name=current_user)


@app.route('/characters/<int:id>', methods=['GET', 'POST'])
@app.route('/characters/<int:id>/', methods=['GET', 'POST'])
def char_page(id):  # страница с информацией о персонаже
    data = find_by_id(id, 'characters')
    comments = Comment.query.filter_by(char=id).all()
    form = AddComment()
    if form.validate_on_submit() and current_user != 'гость':
        comment = request.form.get('content')
        if len(comment) > 0:
            db.session.add(Comment(content=comment, char=id,
                                   user=current_user))
            db.session.commit()
        return redirect('/characters/{}'.format(id))
    else:
        return render_template('character_page.html', char_info=data,
                               name=current_user, form=form, comments=comments)


@app.route('/user/<int:id>')
@app.route('/user/<int:id>/')
def user_page(id):  # страница пользователя
    data = find_by_id(id, 'users')
    return render_template('user.html', user_info=data,
                           name=current_user)


@app.route('/like/<int:id>')
@app.route('/like/<int:id>/')
def like_or_unlike(id):  # поставить или снять лайк
    if current_user == 'гость':
        return redirect('/login')
    if not Like.query.filter_by(user=session['id'], char=id).count() > 0:
        db.session.add(Like(user=session['id'], char=id))
        Character.query.filter_by(id=id).first().likes += 1
    else:
        Like.query.filter_by(user=session['id'], char=id).delete()
        Character.query.filter_by(id=id).first().likes -= 1
    db.session.commit()
    return redirect('/characters')


@app.route('/delete_comment/<int:id>')
@app.route('/delete_comment/<int:id>/')
def delete_comment(id):  # удаление комментария
    comm = find_by_id(id, 'comments')
    if current_user != 'admin' and session['username'] != comm['user']:
        print(session['id'], comm['user'])
        return redirect('/login')
    comment = Comment.query.filter_by(id=id).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect('characters/{}'.format(comm['char']))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
