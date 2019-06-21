from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, PasswordField, validators, TextAreaField
from passlib.hash import sha256_crypt
from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Models
books = db.Table('books',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True),
)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    books = db.relationship('Book', secondary=books, lazy='subquery', backref=db.backref('authors', lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

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
    book_description = TextAreaField('Book Description', [validators.InputRequired()])

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
    authors = Author.query.all()
    return render_template('index.html', authors=authors)


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


@app.route('/book/add', methods=['GET', 'POST'])
def book_add():
    form = BookForm(request.form)
    if request.method == 'POST' and form.validate():
        author = Author.query.filter_by(name=form.author_name.data).first()

        if author:
            books = list(map(lambda book: book.name, author.books))

            if form.book_name.data not in books:

                new_book = Book(name=form.book_name.data, description=form.book_description.data)
                author.books.append(new_book)
                author.save()

                flash(f'{new_book.name} successfully added for {author.name}')
                return redirect(url_for('index'))
            else:
                flash('This author already has this book')
                return render_template('book_add.html', form=form)

        else:
            author = Author(name=form.author_name.data)
            book = Book(name=form.book_name.data, description=form.book_description.data)
            author.books.append(book)
            
            author.save()
            book.save()
        
        flash(f'{book.name} successfully added for {author.name}')
        return redirect(url_for('index'))

    return render_template('book_add.html', form=form)


@app.route('/book/detail/<int:id>')
def book_detail(id):
    book = Book.query.get(id)
    return render_template('book_detail.html', book=book)


@app.route('/book/edit/<int:id>', methods=['GET', 'POST'])
def book_edit(id):
    form = BookForm(request.form)
    book = Book.query.get(id)
    authors = ', '.join([author.name for author in book.authors])
    context = {
        'form': form,
        'book': book,
        'authors': authors
    }
    if request.method == 'POST' and form.validate():
        if form.author_name.data == authors:
            updated_book = Book.query.filter_by(id=id).update({ Book.name: form.book_name.data, Book.description: form.book_description.data})
            db.session.commit()
        else:
            book.authors = []
            new_authors = form.author_name.data.split(', ')
            for author in new_authors:
                new_author = Author.query.filter_by(name=author).first()
                if not new_author:
                    new_author = Author(name=author)
                    new_author.save()
                    book.authors.append(new_author)
                    book.description = form.book_description.data
                elif not new_author in book.authors:
                    book.authors.append(new_author)

            book.save()
        
        flash(f'Book updated', category='success')
        return redirect(url_for('index'))
            
    return render_template('book_edit.html', context=context)


@app.route('/book/delete/<int:id>', methods=['POST'])
def book_delete(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    flash(f'{book.name} has been deleted', category='success')
    return redirect(url_for('index'))

@app.route('/author/<id>')
def author_detail(id):
    author = Author.query.get(id)
    return render_template('author_detail.html', author=author)

    
if __name__ == '__main__':
    app.run(debug=True)
