from flask import Flask
from models.models import *
from controllers.controllers import get_matching_job_listings
from database import db
import unittest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)


class TestGetMatchingJobListings(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.db = db
        self.db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_matching_job_listings(self):
        # Create a User object and save it to the database
        user = User(username='testuser', password='testpassword')
        self.db.session.add(user)
        self.db.session.commit()


        job_search = JobSearch(user_id=user.id, job_type='Software Engineer')
        self.db.session.add(job_search)
        self.db.session.commit()


        job_search = JobSearch(user_id=user.id, job_type='Software Engineer')
        self.db.session.add(job_search)
        self.db.session.commit()

        job_listing = JobListing(job_type='Software Engineer')
        self.db.session.add(job_listing)
        self.db.session.commit()

        result = get_matching_job_listings(job_search)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, job_listing.id)

    def test_get_matching_job_listings_no_match(self):
        user = User(username='testuser', password='testpassword')
        self.db.session.add(user)
        self.db.session.commit()

        job_search = JobSearch(user_id=user.id, job_type='Software Engineer')
        self.db.session.add(job_search)
        self.db.session.commit()

        job_listing = JobListing(job_type='Data Scientist')
        self.db.session.add(job_listing)
        self.db.session.commit()

        result = get_matching_job_listings(job_search)

        self.assertEqual(len(result), 0)

    def test_get_matching_job_listings_multiple_matches(self):
        user = User(username='testuser', password='testpassword')
        self.db.session.add(user)
        self.db.session.commit()

        job_search = JobSearch(user_id=user.id, job_type='Software Engineer')
        self.db.session.add(job_search)
        self.db.session.commit()

        for _ in range(3):
            job_listing = JobListing(job_type='Software Engineer')
            self.db.session.add(job_listing)
        self.db.session.commit()

        result = get_matching_job_listings(job_search)

        self.assertEqual(len(result), 3)

    def test_get_matching_job_listings_multiple_fields(self):
        user = User(username='testuser', password='testpassword')
        self.db.session.add(user)
        self.db.session.commit()

        job_search = JobSearch(user_id=user.id, job_type='Software Engineer', industry='Tech')
        self.db.session.add(job_search)
        self.db.session.commit()

        job_listing = JobListing(job_type='Software Engineer', industry='Tech')
        self.db.session.add(job_listing)
        self.db.session.commit()

        result = get_matching_job_listings(job_search)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, job_listing.id)


if __name__ == '__main__':
    unittest.main()
