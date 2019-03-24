import sqlite3
from flask import *
from flask_wtf import *
from wtforms import *
from wtforms.validators import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
session = {}


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddCharacterForm(FlaskForm):
    name = StringField('Имя персонажа', validators=[DataRequired()])
    content = TextAreaField('Описание и биография')
    submit = SubmitField('Добавить')


class DB:
    def __init__(self):
        conn = sqlite3.connect('data.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


@app.route('/')
@app.route('/index/')
def main_page(s=session):
    # with open("news.json", "rt", encoding="utf8") as f:
    #    news_list = json.loads(f.read())
    # print(news_list)    
    return render_template('index.html'.format(s['username']))

@app.route('/add')
def add_character():
    return render_template('add_character.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session['username']:
            return redirect('/')
    except KeyError:
        pass
    global username
    form = LoginForm()
    flag = True
    if request.method == 'GET':
        return render_template('login.html', title='Авторизация', form=form,
                               success=flag)
    elif request.method == 'POST':
        user_name = form.username.data
        session['username'] = user_name
        password = form.password.data
        exists = users.exists(user_name, password)
        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect('/index')
        else:
            return render_template('login.html', title='Авторизация', 
                                   form=form, success=False)

@app.route('/logout')
def logout():
    try:
        if session['username']:
            pass
    except KeyError:
        return redirect('/')
    session.pop('username', 0)
    session.pop('user_id', 0)


class UserModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (:user_name,:password_hash)''',
                       {"user_name": str(user_name), "password_hash": str(password_hash)})
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": int(user_id)})
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)


class Library:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS library
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            title VARCHAR(100),
                            content VARCHAR(1000),
                            label VARCHAR(1000)
                            )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, label, book_count):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO library 
                                  (title, content, label, count) 
                                  VALUES (:title,:content,:label,:book_count)''',
                       {"title": str(title), "content": str(content), "label": str(label), "book_count": int(book_count)})
        cursor.close()
        self.connection.commit()

    def get(self, title):
        cursor = self.connection.cursor()
        cursor.execute("SELECT title, content, label, id, count FROM library WHERE title = :title", {"title": str(title)})
        row = cursor.fetchone()
        return row

    def get_all(self, view_all=True):
        cursor = self.connection.cursor()
        if view_all:
            cursor.execute("SELECT title, content, label, id, count FROM library ORDER BY title")
        else:
            cursor.execute("SELECT title, content, label, id, count FROM library WHERE count > 0  ORDER BY title")
        rows = cursor.fetchall()
        return rows


class Books:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             library_id INTEGER,
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO articles 
                          (title, content, user_id) 
                          VALUES (?,?,?)''', (title, content, str(user_id),))
        cursor.close()
        self.connection.commit()

    def get(self, character_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id = :character_id", {"character_id": int(character_id)})
        row = cursor.fetchone()
        return row

    def get_all(self, character_id=None):
        cursor = self.connection.cursor()
        if character_id:
            cursor.execute('''SELECT library.title, library.content, library.label, books.id FROM books 
                            LEFT JOIN library ON books.library_id = library.id  
                            WHERE user_id = :character_id ORDER BY library.title''',
                           {"character_id": int(character_id)})
        else:
            cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        return rows

    def delete(self, character_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM articles WHERE id = ?''', (str(character_id)))
        cursor.close()
        self.connection.commit()

    def remove(self, character_id):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT library_id FROM books WHERE id = :character_id''', {"character_id": int(character_id)})
        rows = cursor.fetchone()
        cursor.execute('''UPDATE library SET count = count + 1 WHERE id = :library_id''', {"library_id": int(rows[0])})
        self.delete(character_id)
        cursor.close()
        self.connection.commit()


db = DB()
connect = db.get_connection()
users = UserModel(connect)
users.init_table()

books = Books(connect)
books.init_table()

library = Library(connect)
library.init_table()

users.insert('id1', 'burntbreadburntdread')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
