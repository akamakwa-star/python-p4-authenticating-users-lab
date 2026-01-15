# server/testing/app_test.py
import pytest
from server.app import create_app, db, User

@pytest.fixture(scope='function')
def test_client():
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'testkey'
    }

    app = create_app(config)

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            # Add a test user
            user = User(username='testuser')
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


def test_logs_user_in(test_client):
    response = test_client.post('/login', json={'username': 'testuser'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['logged_in'] is True
    assert data['user'] == 'testuser'

def test_logs_user_out(test_client):
    test_client.post('/login', json={'username': 'testuser'})
    response = test_client.delete('/logout')
    assert response.status_code == 204
    # Check session
    response = test_client.get('/check_session')
    assert response.status_code == 401
    data = response.get_json()
    assert data['logged_in'] is False

def test_checks_session(test_client):
    # Not logged in
    response = test_client.get('/check_session')
    assert response.status_code == 401
    assert response.get_json()['logged_in'] is False

    # Log in
    test_client.post('/login', json={'username': 'testuser'})
    response = test_client.get('/check_session')
    assert response.status_code == 200
    data = response.get_json()
    assert data['logged_in'] is True
    assert data['user'] == 'testuser'
