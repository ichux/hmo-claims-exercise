import unittest
from datetime import date, datetime

from flask import json
from sqlalchemy.exc import IntegrityError

from app import application, database
from app.models import Claim, Service, User
from instance.config import app_config


class UserGenderAgeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = application
        application.config.from_object(app_config["test"])
        self.app_context = self.app.app_context()
        self.app_context.push()
        database.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        database.session.remove()
        database.drop_all()
        self.app_context.pop()

    def test_user_model_constraints(self):
        # Test creating a user with required fields
        user = User(name="John Doe", salary=50000)
        database.session.add(user)
        database.session.commit()

        # Fetch the user to make sure it was added correctly
        fetched_user = User.query.filter_by(name="John Doe").first()
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.name, "John Doe")
        self.assertEqual(fetched_user.salary, 50000)

        # Test missing 'name' should raise an IntegrityError
        with self.assertRaises(Exception) as context:
            user = User(salary=50000)
            database.session.add(user)
            database.session.commit()
        self.assertIn("NOT NULL constraint failed", str(context.exception))

        # Test missing 'salary' should raise an IntegrityError
        with self.assertRaises(Exception) as context:
            user = User(name="Jane Doe")
            database.session.add(user)
            database.session.commit()
        self.assertIn("NOT NULL constraint failed", str(context.exception))

    def test_user_gender_age_route(self):
        # Create a user with all necessary fields
        user = User(
            name="John Doe", salary=50000, date_of_birth=date(1990, 1, 1), gender="Male"
        )
        database.session.add(user)
        database.session.commit()

        # Test POST request
        response = self.client.post(
            "/home/create_claim/patient_data/", data={"patient": "John Doe"}
        )

        # Check if the response status is OK
        self.assertEqual(response.status_code, 200)

        # Check the response data
        data = json.loads(response.data)
        self.assertEqual(data["age"], date.today().year - 1990)
        self.assertEqual(data["gender"], "Male")

    def test_user_model(self):
        # Test basic user creation
        user = User(name="John Doe", salary=50000)
        database.session.add(user)
        database.session.commit()

        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.salary, 50000)
        self.assertIsNotNone(user.id)
        self.assertTrue(isinstance(user.time_created, datetime))

        # Test unique constraint on name
        with self.assertRaises(IntegrityError):
            duplicate_user = User(name="John Doe", salary=60000)
            database.session.add(duplicate_user)
            database.session.commit()

    def test_service_model(self):
        # Create a claim first since 'claim_id' is a foreign key
        user = User(name="Mark Smith", salary=70000)
        database.session.add(user)
        database.session.commit()

        claim = Claim(
            user_id=user.id,
            diagnosis="Checkup",
            hmo="IJKL",
            service_charge=200,
            total_cost=250,
            final_cost=220,
        )
        database.session.add(claim)
        database.session.commit()

        # Test service creation
        service = Service(
            claim_id=claim.id,
            service_name="Consultation",
            type="Medical",
            provider_name="Clinic A",
            source="Appointment",
            cost_of_service=200,
        )
        database.session.add(service)
        database.session.commit()

        self.assertEqual(service.service_name, "Consultation")
        self.assertEqual(service.type, "Medical")
        self.assertEqual(service.provider_name, "Clinic A")
        self.assertEqual(service.source, "Appointment")
        self.assertTrue(isinstance(service.service_date, datetime))


if __name__ == "__main__":
    unittest.main()
