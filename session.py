from flask import Flask, session, render_template, redirect, request, flash
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
        self.password_hash = password
        print('setter')


    def password_valid(self, password):
        return check_password_hash(self.password_hash, password)


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


class ChangePassword(FlaskForm):
    old = PasswordField('Старый пароль: ',
                        validators=[DataRequired()]
                        )
    new = PasswordField('Новый пароль: ',
                        validators=[DataRequired()]
                        )



@app.route('/')
def home():
    if session.get('user'):
        return render_template('page_home.html',
                               id=session['user']['id'],
                               username=session['user']['username']
                               )
    return redirect('/login')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if session.get('user'):
        session.pop('user')
    return redirect('/login')


@app.route('/admins', methods=['POST', 'GET'])
def all_admin():
    if session.get('user') and request.method == 'POST':
        admins = User.query.order_by(User.id).all()
        return render_template('info_admin.html', admins=admins)
    return redirect('/login')


@app.route('/register_admin', methods=['POST', 'GET'])
def register():
    if not session.get('user'):
        return render_template('page_login.html',

                               )
    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template('register_admin.html',
                               form=form
                               )
    if request.method == 'POST':
        superuser = User.query.filter_by(username=form.username.data).first()
        if not superuser:
            password = generate_password_hash(form.password.data)
            new_admin = User(username=form.username.data, password_hash=password)
            db.session.add(new_admin)
            db.session.commit()
            return redirect('/admins')
        form.username.errors = 'Такое имя уже зарегистрировано.'
        return render_template('register_admin.html',
                               form=form
                               )
    return render_template('page_login.html',
                           form=LoginForm()
                           )


@app.route('/settings_profile', methods=['POST', 'GET'])
def change_user():
    if not session.get('user'):
        return redirect('/')
    user = User.query.get(session['user']['id'])
    form = ChangePassword()
    if not form.validate_on_submit():
        return render_template('settings_profile.html',
                               form=form
                               )
    if request.method == 'POST':
        if not user.password_valid(form.old.data):
            form.old.errors = 'Пароль не верен.'
            return render_template('settings_profile.html',
                                   form=form
                                   )
        if form.old.data == form.new.data:
            form.old.errors = 'Пароли не должны совпадать.'
            return render_template('settings_profile.html',
                                   form=form
                                   )
        user.password_hash = generate_password_hash(form.new.data)
        db.session.commit()
        flash('Пароль изменен.')
        return redirect('/')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('user'):
        return redirect('/')
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('page_login.html',
                               form=form
                               )

    if request.method == 'POST':
        superuser = User.query.filter_by(username=form.username.data).first()
        if not superuser or not superuser.password_valid(form.password.data):
            form.username.errors = 'Неправильное имя или пароль.'
            return render_template('page_login.html', form=form)
        session['user'] = {'id': superuser.id,
                           'username': superuser.username,
                           'role': superuser.role
                           }
        return redirect('/')
    return render_template('page_login.html',
                           form=form
                           )


app.run(debug=True)