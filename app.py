from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Article
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
# from functools import wraps
import os


app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']
app.config['MYSQL_CURSORCLASS']=   os.environ['MYSQL_CURSORCLASS']

mysql = MySQL(app)
article = Article()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    return render_template('articles.html', articles=article)


@app.route('/article/<string:id>/')
def get_article(id):
    return render_template('article.html', id=id)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password does not match')])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",
                    (name, email, username, password))
        mysql.connection.commit()
        cur.close()
        flash('You are registerd', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_hash = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s",[username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_hash,password):
                # app.logger.info('Passed')
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logge in','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Password'
                return render_template('login.html',error=error)
        else:
            error = 'Username not found'
            return render_template('login.html',error=error)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = StringField('Body', [validators.Length(min=30)])

@app.route('/add_article',methods=['GET','POST'])
def add_article():
    form = ArticleForm(request.form)
    if request.method=='POST' and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO articles(title,body,author) VALUES(%s,%s,%s)',(title,body,session['username']))
        mysql.connection.commit()
        cur.close()
        flash('Article created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html',form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = os.environ['SECRET_KEY']
    app.run(debug=True)
