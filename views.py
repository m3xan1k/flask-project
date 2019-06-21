from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from passlib.hash import sha256_crypt
from flask_login import current_user, login_user, logout_user, login_required
from forms import *
from models import *

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
@login_required
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
@login_required
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
@login_required
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


@app.route('/about')
def about():
    return render_template('about.html')
    

@app.route('/search')
def search():
    q = request.args.get('q')
    authors = Author.query.filter(Author.name.like('%' + q + '%')).all()
    return render_template('index.html', authors=authors)


if __name__ == '__main__':
    pass