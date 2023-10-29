from flask import render_template, request, redirect, url_for, session, flash
from database import db
from app import app
from models.models import User, JobSearch, JobListing
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64


def send_email(credentials, to, subject, message):
    service = build('gmail', 'v1', credentials=credentials)
    try:
        message = (service.users().messages().send(userId="me", body={
            "raw": base64.urlsafe_b64encode(
                f"To: {to}\r\nSubject: {subject}\r\n\r\n{message}".encode("utf-8")
            ).decode("utf-8")
        }).execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')


def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_matching_job_listings(job_search):
    query = JobListing.query

    # Applying filters based on the job search preferences
    if job_search.job_type:
        query = query.filter(JobListing.job_type == job_search.job_type)
    if job_search.industry:
        query = query.filter(JobListing.industry == job_search.industry)
    if job_search.country:
        query = query.filter(JobListing.country == job_search.country)
    if job_search.city:
        query = query.filter(JobListing.city == job_search.city)
    if job_search.remote:
        query = query.filter(JobListing.remote == job_search.remote)
    if job_search.min_salary:
        query = query.filter(JobListing.salary >= job_search.min_salary)
    if job_search.max_salary:
        query = query.filter(JobListing.salary <= job_search.max_salary)
    if job_search.experience:
        query = query.filter(JobListing.experience == job_search.experience)
    if job_search.posting_date:
        query = query.filter(JobListing.posting_date == job_search.posting_date)

    # Executing query and returning the matching job listings
    matching_job_listings = query.all()
    return matching_job_listings


@app.route('/')
def job_search():
    return render_template('index.html')


@app.route('/job_listings')
def job_listings():
    # Getting recent job search for the current user
    job_search = JobSearch.query.filter_by(user_id=session['user_id']).order_by(JobSearch.id.desc()).first()

    matching_job_listings = get_matching_job_listings(job_search)

    # Rendering the job listings page with the matching job listings
    return render_template('job_listings.html', job_listings=matching_job_listings)


@app.route('/job_listings/<int:job_search_id>')
def job_listings_by_search(job_search_id):
    job_search = JobSearch.query.get(job_search_id)
    if job_search:
        matching_job_listings = get_matching_job_listings(job_search)
        return render_template('job_listings.html', job_listings=matching_job_listings)
    else:
        return redirect(url_for('job_preferences'))

@app.route('/form_validation', methods=['POST'])
def form_validation():
    # Getting the form values
    job_type = request.form.get('jobType')
    industry = request.form.get('industry')
    country = request.form.get('country')
    city = request.form.get('city')
    remote = request.form.get('remote')
    salary = request.form.get('salary')
    experience = request.form.get('experience')
    posting_date = request.form.get('postingDate')

    # Checking if any of the form fields is "null"
    if job_type == "null" or industry == "null" or country == "null" or city == "null" or remote == "null" or salary == "null":
        flash("All fields must be selected.")
        return redirect(url_for('job_search'))

    # Checking if any of the form fields is "default"
    if job_type == "default":
        job_type = None
    if industry == "default":
        industry = None
    if country == "default":
        country = None
    if city == "default":
        city = None
    if remote == "default":
        remote = None

    # Checking if the salary is 'default'
    if salary == 'default':
        min_salary = max_salary = None
    else:
        min_salary, max_salary = map(int, salary.split('-'))

    # Checking if 'experience' is not an integer and not an empty string
    if experience and not experience.isdigit():
        flash("Experience must be a valid integer or left empty.")
        return redirect(url_for('job_search'))

    # If 'experience' is an empty string, set it to None
    if not experience:
        experience = None

    if not posting_date:
        posting_date = None

    session['job_search'] = {
        'job_type': job_type,
        'industry': industry,
        'country': country,
        'city': city,
        'remote': remote,
        'min_salary': min_salary,
        'max_salary': max_salary,
        'experience': experience,
        'posting_date': posting_date
    }

    # Creating a new JobSearch object and save it in the database
    user = User.query.filter_by(id=session['user_id']).first()
    job_search = JobSearch(user_id=user.id, **session['job_search'])
    db.session.add(job_search)
    db.session.commit()

    # Redirect to the login page
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Predefined user's credentials
    username = 'admin'
    password = 'admin'

    if request.method == 'POST':
        # Getting the submitted username, password, and email
        submitted_username = request.form.get('username')
        submitted_password = request.form.get('password')
        submitted_email = request.form.get('email')

        # Checking if the username and password fields are not empty
        if submitted_username and submitted_password:
            # Checking if the submitted credentials match the predefined user's credentials
            if submitted_username == username and submitted_password == password:
                user = User.query.filter_by(username=username).first()
                user.email = submitted_email
                db.session.commit()

                session['user_id'] = user.id

                # Redirect to the job search page
                return redirect(url_for('job_listings'))
            else:
                # If the credentials don't match, flash an error message and render the login page again
                flash('Invalid username or password.')

    # If the request method is 'GET' or the username and password fields are empty, render the login page
    return render_template('login.html')


@app.route('/job_preferences')
def job_preferences():
    # Getting all job searches for the current user
    job_searches = JobSearch.query.filter_by(user_id=session['user_id']).all()

    # Rendering the job preferences page with the job search data
    return render_template('job_preferences.html', job_searches=job_searches)


@app.route('/send_notifications/<int:job_search_id>')
def send_notifications(job_search_id):
    job_search = JobSearch.query.get(job_search_id)
    if job_search:
        matching_job_listings = get_matching_job_listings(job_search)
        user = User.query.filter_by(id=session['user_id']).first()
        credentials = get_credentials()
        send_email(credentials, user.email, "Job Notifications", "\n".join(str(job) for job in matching_job_listings))
        return redirect(url_for('job_preferences'))
    else:
        return redirect(url_for('job_preferences'))
