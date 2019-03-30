from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, BooleanField,
                     SubmitField, FileField, DateField, IntegerField)
from wtforms.validators import *


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    # remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Подтверждение пароля',
                              validators=[DataRequired()])
    about = TextAreaField('Пару слов о себе',
                          default='Этот пользователь ничего не написал о себе')
    submit = SubmitField('Зарегистрироваться')


class AddCharForm(FlaskForm):
    image = StringField('Ссылка на изображение', default=None)
    name = StringField('Имя', validators=[DataRequired()])
    description = TextAreaField('Описание', default='')
    source = StringField('Откуда этот персонаж?', default='')
    role = StringField('Роль в сюжете', default='неизвестно')
    appearance = TextAreaField('Когда впервые появляется в сюжете?',
                               default='неизвестно')
    birthdate = StringField('Дата рождения', default='неизвестно')
    height = StringField('Рост в сантиметрах', default='неизвестно')
    va = StringField('Актер/актер озвучки', default='неизвестно')
    nicknames = StringField('Также известен как', default='неизвестно')
    submit = SubmitField('Добавить')


class AddComment(FlaskForm):
    content = TextAreaField('Введите комментарий', validators=[DataRequired()])
    submit = SubmitField('Добавить комментарий')
