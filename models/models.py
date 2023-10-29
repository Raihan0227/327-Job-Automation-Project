from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=True)  # Add the email field
    job_searches = db.relationship('JobSearch', backref='user', lazy=True)


class JobSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_type = db.Column(db.String(50))
    industry = db.Column(db.String(50))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    remote = db.Column(db.String(50))
    min_salary = db.Column(db.Integer, nullable=True)
    max_salary = db.Column(db.Integer, nullable=True)
    experience = db.Column(db.String(50), nullable=True)
    posting_date = db.Column(db.String(50), nullable=True)


class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(50))
    industry = db.Column(db.String(50))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    remote = db.Column(db.String(50))
    salary = db.Column(db.Integer)
    experience = db.Column(db.Integer)
    posting_date = db.Column(db.Date)
