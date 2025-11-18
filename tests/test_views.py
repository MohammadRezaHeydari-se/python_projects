import pytest
from backend.app import create_app  # Import the app factory function

@pytest.fixture
def client():
    """Create a Flask test client for making requests"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route exists and returns status code 200"""
    resp = client.get("/")
    assert resp.status_code == 200
    # Check that expected text is present in the response
    assert b"Welcome" in resp.data or b"Book Explorer" in resp.data

def test_search_route(client):
    """Test that the search route exists and returns status code 200"""
    resp = client.get("/search")
    assert resp.status_code == 200

def test_authors_route(client):
    """Test that the authors route exists and returns status code 200"""
    resp = client.get("/authors")
    assert resp.status_code == 200

def test_languages_route(client):
    """Test that the languages route exists and returns status code 200"""
    resp = client.get("/languages")
    assert resp.status_code == 200

def test_enrich_route(client):
    """Test that the enrich route exists and returns status code 200"""
    resp = client.get("/enrich")
    assert resp.status_code == 200
