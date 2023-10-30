# Name : Imtiaz Ahmed
# ID : 2013552642
# Project : Job Related
# Language : Python
# Framework : Flask
# Database : SQLALCHEMY

from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, LoginManager
from flask_wtf import FlaskForm
import wtforms
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database1.db'
app.config['SECRET_KEY'] = 'imtiazcaspian'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(30), nullable=False)
    experience = db.Column(db.String(100), nullable=False)

class JobList(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(70), nullable=False, unique=True)
    job_location = db.Column(db.String(30), nullable=False)
    salary = db.Column(db.String(30), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=40)], render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=45)], render_kw={'placeholder': 'Password'})
    location = StringField(validators=[InputRequired(), Length(min=2, max=30)], render_kw={'placeholder': 'Location'})
    experience = StringField(validators=[InputRequired(), Length(min=2, max=90)], render_kw={'placeholder': 'Experience'})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError('Username already exists. Please choose a different one!')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=40)], render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=45)], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    title = StringField(validators=[Length(min=2, max=70)], render_kw={'placeholder': 'Search By Title'})
    location = StringField(validators=[Length(min=2, max=30)], render_kw={'placeholder': 'Search By Location'})
    search = SubmitField('Search')


@app.route('/')
@app.route('/homepage')
def homepage():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_pass, location=form.location.data,
                        experience=form.experience.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/whole_job', methods=['GET', 'POST'])
@login_required
def whole_job():
    job = JobList.query.all()
    for row in job:
        print(row.job_title)
        print(row.job_location)
        print(row.salary)
    return render_template('whole_job.html', inf=job)

@app.route('/search_job', methods=['GET', 'POST'])
@login_required
def search_job():
    form = SearchForm()
    print('Done!')

    if form.location.data != '' and form.title.data == '':
        job = JobList.query.filter_by(job_location=form.location.data).all()
        if job:
            print('Found!')
            return render_template('job_list.html', inf=job)
    elif form.title.data != '' and form.location.data == '':
        job = JobList.query.filter_by(job_title=form.title.data).all()
        if job:
            print('Found!')
            return render_template('job_list.html', inf=job)
    return render_template('search_job.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')




@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)