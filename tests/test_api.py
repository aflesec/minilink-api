from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_shorten_returns_code():
    r = client.post("/shorten", json={"url": "https://example.com/a"})
    assert r.status_code == 200
    data = r.json()
    assert "code" in data
    assert data["original_url"] == "https://example.com/a"


def test_resolve_not_found():
    r = client.get("/resolve/inexistant")
    assert r.status_code == 404
