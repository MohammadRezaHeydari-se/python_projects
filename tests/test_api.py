import json
import types
import builtins
import flask
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from backend.app import app
from backend.app import create_app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_search_ok(client, monkeypatch):
    # mocka utils.fetch_gutendx till ett litet svar
    import api

    def fake_fetch(params, max_pages=3):
        return [{
            "results": [{
                "id": 1,
                "title": "Test Book",
                "authors": [{"name":"John Doe","birth_year":1900,"death_year":1970}],
                "languages": ["en"],
                "subjects": ["X"],
                "bookshelves": ["Y"],
                "formats": {"image/jpeg": None, "text/plain": "http://x"},
                "download_count": 42
            }],
            "next": None
        }]
    # Patch the function in the api module where it's actually used
    monkeypatch.setattr("backend.api.fetch_gutendex", fake_fetch)

    resp = client.get("/api/search?search=test&pages=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "books" in data and "languages" in data and "authors" in data
    assert data["count"] == 1