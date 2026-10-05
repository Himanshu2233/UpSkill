from datetime import date, timedelta
import re

import pytest

from jobtrack.extensions import db
from jobtrack.models import Application, User
from conftest import register


def application_data(**changes):
    data = {'company': 'Orbit Labs', 'title': 'Python Developer', 'application_date': date.today().isoformat(), 'deadline': '', 'posting_url': '', 'status': 'Applied', 'notes': 'Follow up next week'}
    data.update(changes)
    return data


def test_authentication(client, app):
    assert client.get('/').status_code == 302
    result = register(client)
    assert b'Your account is ready' in result.data
    with app.app_context():
        user = db.session.scalar(db.select(User))
        assert user.password_hash != 'StrongPass123!'
        assert user.check_password('StrongPass123!')
    assert client.get('/auth/logout').status_code == 405
    client.post('/auth/logout')
    assert b'already exists' in register(client, 'STUDENT@example.com').data
    assert b'incorrect' in client.post('/auth/login', data={'email': 'student@example.com', 'password': 'wrong'}, follow_redirects=True).data
    assert client.post('/auth/login?next=https://evil.example', data={'email': 'STUDENT@example.com', 'password': 'StrongPass123!'}).headers['Location'] == '/'


def test_registration_validation(client, app):
    result = client.post('/auth/register', data={'email': 'not-an-email', 'password': 'short', 'confirm_password': 'other'})
    assert b'Invalid email' in result.data
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(User.id))) == 0


def test_crud_and_delete_confirmation(logged_in, app):
    result = logged_in.post('/applications/new', data=application_data(), follow_redirects=True)
    assert b'Orbit Labs' in result.data
    with app.app_context():
        application_id = db.session.scalar(db.select(Application.id))
    path = '/applications/{}'.format(application_id)
    assert logged_in.get(path + '/edit').status_code == 200
    result = logged_in.post(path + '/edit', data=application_data(status='Interviewing', notes='Interview Monday'), follow_redirects=True)
    assert b'Interview Monday' in result.data
    assert b'Yes, delete application' in logged_in.get(path + '/delete').data
    assert logged_in.get(path).status_code == 200
    assert b'Application deleted' in logged_in.post(path + '/delete', follow_redirects=True).data
    assert logged_in.get(path).status_code == 404


@pytest.mark.parametrize('changes', [{'company': '   '}, {'title': ''}, {'application_date': 'invalid'}, {'deadline': '2026-02-30'}, {'posting_url': 'javascript:alert(1)'}, {'posting_url': 'https://'}, {'posting_url': 'https://example.com:bad'}, {'status': 'Unknown'}, {'notes': 'a' * 10001}])
def test_validation(logged_in, app, changes):
    assert logged_in.post('/applications/new', data=application_data(**changes)).status_code == 200
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(Application.id))) == 0


def test_valid_optional_fields_and_escaping(logged_in):
    result = logged_in.post('/applications/new', data=application_data(posting_url='https://example.com/jobs?x=1', notes='<script>alert(1)</script>'), follow_redirects=True)
    assert b'Open job posting' in result.data
    assert b'&lt;script&gt;' in result.data
    assert b'<script>alert(1)</script>' not in result.data


def test_other_user_cannot_access_records(logged_in, app):
    logged_in.post('/applications/new', data=application_data())
    with app.app_context():
        application_id = db.session.scalar(db.select(Application.id))
    logged_in.post('/auth/logout')
    register(logged_in, 'other@example.com')
    assert b'Orbit Labs' not in logged_in.get('/').data
    for suffix in ('', '/edit', '/delete'):
        path = '/applications/{}{}'.format(application_id, suffix)
        assert logged_in.get(path).status_code == 404
        if suffix:
            assert logged_in.post(path, data=application_data(company='Stolen')).status_code == 404
    with app.app_context():
        assert db.session.get(Application, application_id).company == 'Orbit Labs'


def test_search_filter_counts_and_deadline_boundaries(logged_in, app):
    today = date.today()
    for company, status, days in [('DueToday', 'Applied', 0), ('DueSeven', 'Interviewing', 7), ('TooLate', 'Applied', 8), ('PastDue', 'Applied', -1), ('OfferClosed', 'Offered', 2), ('RejectedClosed', 'Rejected', 3)]:
        logged_in.post('/applications/new', data=application_data(company=company, deadline=(today+timedelta(days=days)).isoformat(), status=status))
    result = logged_in.get('/').data.decode()
    aside = result.split('<aside')[1]
    assert 'DueToday' in aside and 'DueSeven' in aside
    assert all(name not in aside for name in ('TooLate', 'PastDue', 'OfferClosed', 'RejectedClosed'))
    assert 'Total applications</span><strong>6</strong>' in result
    assert 'Applied</span><strong>3</strong>' in result
    result = logged_in.get('/?q=toolate&status=Applied').data.decode()
    assert '1 results' in result and 'TooLate' in result
    assert 'Total applications</span><strong>6</strong>' in result
    assert b'No matching applications' in logged_in.get('/?q=doesnotexist').data
    assert b'0 results' in logged_in.get('/?q=%25').data
    assert logged_in.get('/?status=Unknown').status_code == 400


def test_csrf_protection(client, app):
    app.config['WTF_CSRF_ENABLED'] = True
    assert client.post('/auth/register', data={}).status_code == 400
    page = client.get('/auth/register').data.decode()
    token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page).group(1)
    result = client.post('/auth/register', data={'csrf_token': token, 'email': 'safe@example.com', 'password': 'StrongPass123!', 'confirm_password': 'StrongPass123!'})
    assert result.status_code == 302
    assert client.post('/applications/new', data=application_data()).status_code == 400
    assert client.post('/auth/logout').status_code == 400
    assert client.get('/').status_code == 200


def test_empty_states_and_pages(logged_in):
    assert b'Add your first application' in logged_in.get('/').data
    assert b'caught up' in logged_in.get('/').data
    assert logged_in.get('/applications/new').status_code == 200
    assert logged_in.get('/missing').status_code == 404


def test_seed_is_repeatable(app):
    runner = app.test_cli_runner()
    assert runner.invoke(args=['init-db']).exit_code == 0
    assert runner.invoke(args=['seed-demo']).exit_code == 0
    assert 'already exists' in runner.invoke(args=['seed-demo']).output
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(Application.id))) == 6
        assert db.session.scalar(db.select(db.func.count(User.id))) == 1
