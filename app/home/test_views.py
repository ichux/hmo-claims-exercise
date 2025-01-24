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

    @patch("flask.render_template")
    def test_all_users(self, mock_render_template):
        response = self.client.get("/home/all/users")
        self.assertEqual(response.status_code, 200)
        mock_render_template.assert_called_once_with(
            "home/home.html", users=mock_render_template.ANY, title="Users"
        )

    @patch("flask.render_template")
    def test_view_user(self, mock_render_template):
        response = self.client.get(f"/home/user/{self.user.id}")
        self.assertEqual(response.status_code, 200)
        mock_render_template.assert_called_once_with(
            "home/user_data.html", user_data=self.user
        )

    def test_view_non_existent_user(self):
        response = self.client.get("/home/user/9999")
        self.assertEqual(response.status_code, 404)

    def test_edit_user(self):
        response = self.client.post(
            f"/home/user/{self.user.id}/edit",
            data={
                "name": "Updated User",
                "gender": "female",
                "salary": 60000,
                "date_of_birth": "1991-02-02",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User updated successfully.", response.data)

        # Verify the user is updated in the database
        updated_user = User.query.get(self.user.id)
        self.assertEqual(updated_user.name, "Updated User")
        self.assertEqual(updated_user.gender, "female")
        self.assertEqual(updated_user.salary, 60000)
        self.assertEqual(updated_user.date_of_birth.strftime("%Y-%m-%d"), "1991-02-02")

    def test_add_user(self):
        response = self.client.post(
            "/home/users/add",
            data={
                "name": "New User",
                "gender": "female",
                "salary": 70000,
                "date_of_birth": "1992-03-03",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User created successfully.", response.data)

        # Verify the new user is in the database
        new_user = User.query.filter_by(name="New User").first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.gender, "female")
        self.assertEqual(new_user.salary, 70000)
        self.assertEqual(new_user.date_of_birth.strftime("%Y-%m-%d"), "1992-03-03")

    def test_delete_user(self):
        response = self.client.post(
            f"/home/user/{self.user.id}/delete", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"User and all associated claims and services deleted successfully.",
            response.data,
        )

        # Verify the user is deleted from the database
        deleted_user = User.query.get(self.user.id)
        self.assertIsNone(deleted_user)

    def test_claim(self):
        response = self.client.get("/home/claim")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Claims", response.data)

    def test_create_claim(self):
        response = self.client.post(
            "/home/create_claim",
            data={
                "user": "Test User",
                "diagnosis": "Test Diagnosis",
                "hmo": "Test HMO",
                "age": 30,
                "total_cost": 1000,
                "service_charge": 100,
                "final_cost": 900,
                "service_name": ["Test Service"],
                "type": ["Test Type"],
                "provider_name": ["Test Provider"],
                "source": ["Test Source"],
                "cost_of_service": [500],
                "service_date": ["2024-12-12"],
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Claim created successfully.", response.data)

        # Verify the claim is in the database
        new_claim = Claim.query.filter_by(diagnosis="Test Diagnosis").first()
        self.assertIsNotNone(new_claim)
        self.assertEqual(new_claim.total_cost, 1000)

        # Verify the associated service is in the database
        associated_service = Service.query.filter_by(claim_id=new_claim.id).first()
        self.assertIsNotNone(associated_service)
        self.assertEqual(associated_service.service_name, "Test Service")

    def test_view_claim(self):
        response = self.client.get("/home/view_claim")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Claims", response.data)

    def test_user_gender_age(self):
        response = self.client.post(
            "/home/create_claim/patient_data/", data={"patient": "Test User"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"age":', response.data)
        self.assertIn(b'"gender":', response.data)


if __name__ == "__main__":
    unittest.main()
