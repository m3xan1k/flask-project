from wtforms import Form, StringField, PasswordField, validators, TextAreaField

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

if __name__ == '__main__':
    pass