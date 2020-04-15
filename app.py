from classes.user import User, to_class
from flask import Flask, render_template, url_for, request, session, redirect, flash
from forms import LoginForm, RegistrationForm
import pymongo
import bcrypt
import config

app = Flask(__name__)
app.secret_key = 'mysecret'
app.config['SECRET_KEY'] = config.secret_key
app.config['MONGO_DBNAME'] = config.mongoname

mongo = pymongo.MongoClient(
    config.mongoclient)


@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    flash("Create an account or login firstly", 'warning')
    return redirect(url_for('login'))


@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        user = to_class(session['user'])
        if request.form['keyword'] in user.keywords:
            flash("This word is already in your dictionary", 'danger')
        else:
            user.add_keyword(request.form['keyword'])
            flash("This word is added to your dictionary", 'success')
    return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        del session['user']
    flash("You have logged out", "danger")
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        users = mongo.db.users
        hashpass = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        users.insert({'name': form.username.data, 'email': form.email.data, 'password': hashpass, 'keywords': []})
        session['user'] = form.username.data
        flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = mongo.db.users
        login_user = users.find_one({'name': form.username.data})

        if login_user:
            if bcrypt.hashpw(form.password.data.encode('utf-8'), login_user['password']) == login_user['password']:
                session['user'] = form.username.data
                flash(f"You have logged in as {form.username.data}!", 'success')
                return redirect(url_for('index'))
        flash('Incorrect password or/and username', 'danger')
    return render_template('login.html', title='Register', form=form)


if __name__ == '__main__':
    app.run(debug=True)
