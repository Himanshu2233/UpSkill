import pytest

from jobtrack import create_app
from jobtrack.extensions import db


@pytest.fixture
def app(tmp_path):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test-key', 'WTF_CSRF_ENABLED': False, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'test.sqlite')})
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, email='student@example.com'):
    return client.post('/auth/register', data={'email': email, 'password': 'StrongPass123!', 'confirm_password': 'StrongPass123!'}, follow_redirects=True)


@pytest.fixture
def logged_in(client):
    register(client)
    return client
