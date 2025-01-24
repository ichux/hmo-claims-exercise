import unittest
from unittest.mock import patch
from datetime import datetime
from app import application as app, database
from app.models import User, Claim, Service


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

    @patch("flask.render_template")
    def test_all_users(self, mock_render_template):
        with app.test_request_context():
            from app.home.views import all_users

            all_users()
            # self.assertEqual(response.status_code, 200)
            mock_render_template.assert_called_once_with(
                "home/home.html", users=mock_render_template.ANY, title="Users"
            )

    @patch("flask.render_template")
    def test_view_user(self, mock_render_template):
        with app.test_request_context():
            from app.home.views import view_user

            response = view_user(self.user.id)
            # self.assertEqual(response.status_code, 200)
            mock_render_template.assert_called_once_with(
                "home/user_data.html", user_data=self.user
            )

    def test_view_non_existent_user(self):
        with app.test_request_context():
            from app.home.views import view_user

            response = view_user(9999)
            self.assertEqual(response.status_code, 404)

    def test_edit_user(self):
        with app.test_request_context(
            method="POST",
            data={
                "name": "Updated User",
                "gender": "female",
                "salary": 60000,
                "date_of_birth": "1991-02-02",
            },
        ):
            from app.home.views import edit_user

            # response = edit_user(self.user.id)
            # self.assertEqual(response.status_code, 200)
            # self.assertIn(b"User updated successfully.", response.data)

            # Verify the user is updated in the database
            updated_user = User.query.get(self.user.id)
            self.assertEqual(updated_user.name, "Updated User")
            self.assertEqual(updated_user.gender, "female")
            self.assertEqual(updated_user.salary, 60000)
            self.assertEqual(
                updated_user.date_of_birth.strftime("%Y-%m-%d"), "1991-02-02"
            )

    def test_add_user(self):
        with app.test_request_context(
            method="POST",
            data={
                "name": "New User",
                "gender": "female",
                "salary": 70000,
                "date_of_birth": "1992-03-03",
            },
        ):
            from app.home.views import add_user

            response = add_user()
            # self.assertEqual(response.status_code, 200)
            self.assertIn(b"User created successfully.", response.data)

            # Verify the new user is in the database
            new_user = User.query.filter_by(name="New User").first()
            self.assertIsNotNone(new_user)
            self.assertEqual(new_user.gender, "female")
            self.assertEqual(new_user.salary, 70000)
            self.assertEqual(new_user.date_of_birth.strftime("%Y-%m-%d"), "1992-03-03")

    def test_delete_user(self):
        with app.test_request_context(method="POST"):
            from app.home.views import delete_user

            response = delete_user(self.user.id)
            self.assertEqual(response.status_code, 200)
            self.assertIn(
                b"User and all associated claims and services deleted successfully.",
                response.data,
            )

            # Verify the user is deleted from the database
            deleted_user = User.query.get(self.user.id)
            self.assertIsNone(deleted_user)

    @patch("flask.render_template")
    def test_claim(self, mock_render_template):
        with app.test_request_context():
            from app.home.views import claim

            response = claim()
            self.assertEqual(response.status_code, 200)
            mock_render_template.assert_called_once_with(
                "home/claim.html", claims=mock_render_template.ANY, title="Claims"
            )

    def test_create_claim(self):
        with app.test_request_context(
            method="POST",
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
        ):
            from app.home.views import create_claim

            response = create_claim()
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

    @patch("flask.render_template")
    def test_view_claim(self, mock_render_template):
        with app.test_request_context():
            from app.home.views import view_claim

            response = view_claim()
            self.assertEqual(response.status_code, 200)
            mock_render_template.assert_called_once_with(
                "home/view_claims.html", claims=mock_render_template.ANY
            )

    def test_user_gender_age(self):
        with app.test_request_context(method="POST", data={"patient": "Test User"}):
            from app.home.views import user_gender_age

            response = user_gender_age()
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'"age":', response.data)
            self.assertIn(b'"gender":', response.data)


if __name__ == "__main__":
    unittest.main()
