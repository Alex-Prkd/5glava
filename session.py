from flask import Flask, session, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'random_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,
                   primary_key=True
                   )
    username = db.Column(db.String(32),
                         unique=True,
                         nullable=False
                         )
    password_hash = db.Column(db.String(128),
                         nullable=False
                         )

    role = db.Column(db.String(32),
                     nullable=False,
                     default='Участник.'
                     )


    @property
    def password(self):
        raise AttributeError('Нельзя обратиться напрямую.')


    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


class LoginForm(FlaskForm):
    username = StringField('Имя: ',
                           validators=[DataRequired()
                                       ]
                           )
    password = PasswordField('Пароль: ',
                             validators=[DataRequired()
                                         ]
                             )


class RegisterForm(FlaskForm):
    username = StringField('Имя: ',
                           validators=[DataRequired()]
                           )
    password = PasswordField('Пароль: ',
                             validators=[DataRequired()]
                             )


@app.route('/')
def home():
    if session.get('user_id'):
        return render_template('page_home.html',
                               username=session['username']
                               )
    return redirect('/login')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if session.get('user_id'):
        session.pop('user_id')
        session.pop('username')
    return redirect('/login')


@app.route('/admins', methods=['POST', 'GET'])
def all_admin():
    if session.get('user_id') and request.method == 'POST':
        admins = User.query.order_by(User.id).all()
        return render_template('info_admin.html', admins=admins)
    return redirect('/login')


@app.route('/register_admin', methods=['POST', 'GET'])
def register():
    if not session.get('user_id'):
        return render_template('page_login.html',
                               form=LoginForm()
                               )
    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template('register_admin.html',
                               form=form
                               )
    if request.method == 'POST':
        superuser = User.query.filter_by(username=form.username.data).first()
        if not superuser:
            new_admin = User(username=form.username.data, password=form.password.data)
            db.session.add(new_admin)
            db.session.commit()
            return redirect('/admins')
        form.username.errors = 'Такое имя уже зарегистрировано.'
        return render_template('register_admin.html', form=form)
    return render_template('page_login.html',
                           form=LoginForm()
                           )


@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('user_id'):
        return redirect('/')
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('page_login.html',
                               form=form
                               )

    if request.method == 'POST':
        superuser = User.query.filter_by(username=form.username.data).first()
        if not superuser or superuser.password != form.password.data:
            form.username.errors = 'Неправильное имя или пароль.'
            return render_template('page_login.html', form=form)
        session['user_id'] = superuser.id
        session['username'] = superuser.username
        return redirect('/')
    return render_template('page_login.html',
                           form=form
                           )


