import pytest
import json
from app import create_app, db as _db


@pytest.fixture
def app():
    application = create_app()
    application.config['TESTING'] = True
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_token(client):
    client.post('/api/auth/register', json={
        'username': 'testuser', 'email': 'test@test.com', 'password': 'pass1234'
    })
    r = client.post('/api/auth/login', json={
        'email': 'test@test.com', 'password': 'pass1234'
    })
    return r.get_json()['access_token']


def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'


def test_register(client):
    r = client.post('/api/auth/register', json={
        'username': 'alice', 'email': 'alice@test.com', 'password': 'pass1234'
    })
    assert r.status_code == 201
    assert 'user' in r.get_json()


def test_login(client):
    client.post('/api/auth/register', json={
        'username': 'bob', 'email': 'bob@test.com', 'password': 'pass1234'
    })
    r = client.post('/api/auth/login', json={
        'email': 'bob@test.com', 'password': 'pass1234'
    })
    assert r.status_code == 200
    assert 'access_token' in r.get_json()


def test_create_referral(client, auth_token):
    r = client.post('/api/referrals/',
        json={'campaign': 'twitter-promo'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert r.status_code == 201
    data = r.get_json()['referral']
    assert 'code' in data
    assert 'referral_url' in data


def test_click_tracking(client, auth_token):
    r = client.post('/api/referrals/',
        json={'campaign': 'test'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    code = r.get_json()['referral']['code']

    # Hit the referral link
    r = client.get(f'/api/referrals/r/{code}')
    assert r.status_code in (302, 200)

    # Check analytics
    r = client.get('/api/analytics/summary',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert r.get_json()['total_clicks'] == 1


def test_conversion_webhook(client, auth_token):
    r = client.post('/api/referrals/',
        json={'campaign': 'test'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    code = r.get_json()['referral']['code']

    r = client.post('/api/webhooks/conversion', json={
        'referral_code':    code,
        'conversion_type':  'signup',
        'idempotency_key':  'test-idem-001',
    })
    assert r.status_code == 201

    # Idempotency — same key should not double-count
    r = client.post('/api/webhooks/conversion', json={
        'referral_code':   code,
        'conversion_type': 'signup',
        'idempotency_key': 'test-idem-001',
    })
    assert r.status_code == 200
    assert 'idempotent' in r.get_json()['message']
