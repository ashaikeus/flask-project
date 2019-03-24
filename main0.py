import sqlite3
from flask import *
from flask_wtf import *
from wtforms import *
from wtforms.validators import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
session = {'username': None}


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

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    


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


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
