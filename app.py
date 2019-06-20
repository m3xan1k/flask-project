from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


# Models
books = db.Table('books',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    books = db.relationship('Book', secondary=books, lazy='subquery', backref=db.backref('authors', lazy=True))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


# Forms
class RegistrationForm(Form):
    email = StringField('Email', [validators.InputRequired(), validators.Email()])

    username = StringField('Username', [validators.InputRequired(), validators.Length(min=4, max=30)])

    password = PasswordField('Password', [validators.InputRequired(), validators.Length(min=8, max=80), validators.EqualTo('confirm', message='Passwords must match')])

    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    username = StringField('Username', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])

class BookForm(Form):
    book_name = StringField('Book Name', [validators.InputRequired()])
    author_name = StringField('Author Name', [validators.InputRequired()])

class SearchForm(Form):
    query =  StringField('Search', [validators.InputRequired()])


# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            password=sha256_crypt.encrypt(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('You successfully registered', category='success')
        login_user(new_user)
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()

        if user and sha256_crypt.verify(form.password.data, user.password):
            login_user(user)
            flash('You successfully logged in', category='success')
            return redirect(url_for('index'))
        else:
            flash('Username or password is incorrect', category='danger')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You logged out', category='success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
