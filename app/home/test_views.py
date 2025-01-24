import unittest
from datetime import datetime
from unittest.mock import patch

from app import application as app
from app import database
from app.models import Claim, Service, User


class TestViews(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        database.create_all()

        # Add a test user
        self.user = User(
            name="Test User",
            gender="male",
            salary=50000,
            date_of_birth=datetime.strptime("01-01-1999", "%d-%m-%Y"),
        )
        database.session.add(self.user)
        database.session.commit()

    def tearDown(self):
        database.session.remove()
        database.drop_all()
        self.app_context.pop()

    def test_user_gender_age(self):
        response = self.client.post(
            "/home/create_claim/patient_data/", data={"patient": "Test User"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"age":', response.data)
        self.assertIn(b'"gender":', response.data)


if __name__ == "__main__":
    unittest.main()
