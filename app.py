from flask import Flask
from models.models import *
from fake_web_scrapper.mock_data import generate_job_listings
from database import db

app = Flask(__name__, template_folder='views/templates', static_folder='views/static')
app.secret_key = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)


from controllers.controllers import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(username='admin', password='admin')
            db.session.add(user)
            db.session.commit()

        # Generating job listings and add them to the database only if they don't exist
        if JobListing.query.first() is None:
            job_listings = generate_job_listings(30)
            for job_listing_data in job_listings:
                job_listing = JobListing(**job_listing_data)
                db.session.add(job_listing)
            db.session.commit()

    app.run(debug=True)
