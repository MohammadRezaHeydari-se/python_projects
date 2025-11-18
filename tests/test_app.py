import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from application.app import app, _cached_df
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True  # ⚡ added for clearer error propagation
    with app.test_client() as client:
        yield client

def test_home_get(client):
    """GET / should open the home page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hitta information' in response.data  # check that the form is displayed

def test_home_post_missing_fields(client):
    """POST / with empty fields should redirect to the error page"""
    response = client.post('/', data={})
    assert response.status_code == 302  # redirect to /error
    assert '/error' in response.headers['Location']

def test_home_post_invalid_date(client):
    """POST / with an invalid date should trigger an error"""
    data = {'year': '2025', 'mounth': '13', 'day': '32', 'price': 'SE1'}
    response = client.post('/', data=data)
    assert response.status_code == 302
    assert '/error' in response.headers['Location']

def test_home_post_invalid_price(client):
    """POST / with an invalid price zone should trigger an error"""
    data = {'year': '2025', 'mounth': '10', 'day': '27', 'price': 'SE5'}
    response = client.post('/', data=data)
    assert response.status_code == 302
    assert '/error' in response.headers['Location']

def test_home_post_valid_data(client, monkeypatch):
    """POST / with valid data should generate an HTML table"""
    # Patch requests.get to simulate a valid API response
    def fake_get(url):
        class FakeResponse:
            status_code = 200
            def json(self):
                return [
                    {"SEK_per_kWh": 0.03, "EUR_per_kWh": 0.0028, "EXR": 11.42,
                     "time_start": "2025-10-27T00:00", "time_end": "2025-10-27T01:00"}
                ]
        return FakeResponse()
    monkeypatch.setattr("requests.get", fake_get)

    # POST request with valid data
    data = {'year': '2025', 'mounth': '10', 'day': '27', 'price': 'SE1'}
    response = client.post('/', data=data)
    assert response.status_code == 200
    assert b'SEK_per_kWh' in response.data  # check that the table was created

def test_diagram_no_data(client):
    # ensure the cached dataframe in the application module is cleared
    import application.app as application_app
    application_app._cached_df = None

    response = client.get('/diagram', follow_redirects=True)
    assert response.status_code == 404
    assert "Ingen data för diagrammet" in response.data.decode('utf-8')


def test_diagram_with_data(client, monkeypatch):
    """/diagram with existing data should return the chart"""
    global _cached_df

    # Patch requests.get to simulate API data
    def fake_get(url):
        class FakeResponse:
            status_code = 200
            def json(self):
                return [
                    {"SEK_per_kWh": 0.03, "EUR_per_kWh": 0.0028, "EXR": 11.42,
                     "time_start": "2025-10-27T00:00", "time_end": "2025-10-27T01:00"}
                ]
        return FakeResponse()
    monkeypatch.setattr("requests.get", fake_get)

    # POST request to set _cached_df
    client.post('/', data={'year': '2025', 'mounth': '10', 'day': '27', 'price': 'SE1'})

    response = client.get('/diagram')
    assert response.status_code == 200
    assert b'SEK per kWh' in response.data  # check the chart title

def test_error_page(client):
    """/error should work correctly"""
    response = client.get('/error?code=400&message=Test')
    assert response.status_code == 400
    assert b'Test' in response.data
