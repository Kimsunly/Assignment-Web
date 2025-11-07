import unittest
from main import create_app, db
from models.models import User
from werkzeug.security import generate_password_hash


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        # In-memory DB for tests
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create test user
            user = User(username="testuser", password=generate_password_hash(
                "testpass"), role="student")
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_login_success(self):
        response = self.client.post(
            "/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
        # Check if redirected to dashboard
        self.assertIn(b"dashboard", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            "/login", data={"username": "testuser", "password": "wrongpass"}, follow_redirects=True)
        self.assertIn(b"Invalid credentials", response.data)

    def test_login_nonexistent_user(self):
        response = self.client.post(
            "/login", data={"username": "nouser", "password": "nopass"}, follow_redirects=True)
        self.assertIn(b"Invalid credentials", response.data)


if __name__ == "__main__":
    unittest.main()
