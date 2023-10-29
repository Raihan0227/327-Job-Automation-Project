from faker import Faker
import random

def generate_job_listings(num_listings):
    fake = Faker()
    job_listings = []
    job_types = ['Full Time', 'Part Time']
    industries = ['IT', 'Healthcare', 'Finance', 'Education']
    countries = ['Bangladesh']
    cities = ['Dhaka', 'Chittagong', 'Rajshahi', 'Khulna', 'Barisal']
    remote_options = ['Yes', 'No']

    for _ in range(num_listings):
        job_listing = {
            'job_type': random.choice(job_types),
            'industry': random.choice(industries),
            'country': random.choice(countries),
            'city': random.choice(cities),
            'remote': random.choice(remote_options),
            'salary': random.randint(5000, 100000),
            'experience': random.randint(1, 10),
            'posting_date': fake.date_between(start_date='-1y', end_date='today')
        }
        job_listings.append(job_listing)

    return job_listings
