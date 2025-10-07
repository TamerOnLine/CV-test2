# tests/test_profiles.py
from __future__ import annotations

from fastapi.testclient import TestClient
import json
import importlib
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """
    Redirect the PROFILES_DIR used by the API routes to a temporary directory.
    This ensures tests do not write into the real profiles folder.
    """
    # Reload the routes module with patched PROFILES_DIR
    profiles_mod = importlib.import_module("api.routes.profiles")
    monkeypatch.setattr(profiles_mod, "PROFILES_DIR", tmp_path, raising=True)
    profiles_mod.PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    importlib.reload(profiles_mod)

    # Reload main app to make sure the router uses the new directory
    if "api.main" in sys.modules:
        importlib.reload(sys.modules["api.main"])
    from api.main import app

    return TestClient(app)


def _good_profile():
    """Return a valid example profile used in multiple tests."""
    return {
        "header": {"name": "Tamer", "title": "Backend Developer"},
        "contact": {"email": "tamer@example.com", "github": "TamerOnLine"},
        "skills": ["FastAPI", "PostgreSQL", "Streamlit"],
        "projects": [],
        "languages": ["Arabic", "English"],
        "education": [],
    }


def test_save_and_get_profile(client):
    """Ensure saving and loading a profile works as expected."""
    payload = {"name": "my_profile", "profile": _good_profile()}
    r = client.post("/api/profiles/save", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["file"] == "my_profile.json"

    # Retrieve it back using GET /api/profiles/{name}
    r2 = client.get("/api/profiles/my_profile")
    assert r2.status_code == 200, r2.text
    returned = r2.json()
    assert returned["header"]["name"] == "Tamer"
    assert returned["contact"]["github"] == "TamerOnLine"


def test_list_profiles(client):
    """Ensure listing returns all saved profiles."""
    for name in ("p1", "p2"):
        r = client.post("/api/profiles/save", json={"name": name, "profile": _good_profile()})
        assert r.status_code == 200

    r = client.get("/api/profiles/list")
    assert r.status_code == 200
    names = r.json()
    assert isinstance(names, list)
    assert set(names) >= {"p1.json", "p2.json"} or set(names) >= {"p1", "p2"}


@pytest.mark.parametrize(
    "bad_name",
    [
        "../../etc/passwd",
        r"..\\..\\Windows\\System32",
        "good/../evil",
        "good\\..\\evil",
        "../trick",
        "././../x",
    ],
)
def test_invalid_name_rejected(client, bad_name):
    """Profiles with invalid names (path traversal attempts) must be rejected."""
    bad = {"name": bad_name, "profile": _good_profile()}
    r = client.post("/api/profiles/save", json=bad)
    assert r.status_code in (400, 422)


def test_delete_profile(client):
    """Ensure deleting a profile removes it and subsequent reads fail."""
    client.post("/api/profiles/save", json={"name": "delme", "profile": _good_profile()})
    r = client.delete("/api/profiles/delme")
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # Now it must return 404
    r2 = client.get("/api/profiles/delme")
    assert r2.status_code == 404


@pytest.mark.parametrize(
    "bad_email",
    ["not-an-email", "missing-at.example.com", "a@b", "a@b.", "@nope", "name@domain,com"],
)
def test_validation_error_on_invalid_email(client, bad_email):
    """Invalid email addresses should trigger a Pydantic validation error."""
    bad_profile = _good_profile()
    bad_profile["contact"]["email"] = bad_email
    r = client.post("/api/profiles/save", json={"name": "badmail", "profile": bad_profile})
    assert r.status_code == 422
    detail = r.json().get("detail", [])
    assert "email" in json.dumps(detail).lower()


def test_overwrite_existing_profile(client):
    """Saving the same profile name twice should overwrite the existing one."""
    # First version
    p1 = _good_profile()
    p1["header"]["title"] = "Backend Dev v1"
    r1 = client.post("/api/profiles/save", json={"name": "same", "profile": p1})
    assert r1.status_code == 200

    # Overwrite with version 2
    p2 = _good_profile()
    p2["header"]["title"] = "Backend Dev v2"
    r2 = client.post("/api/profiles/save", json={"name": "same", "profile": p2})
    assert r2.status_code == 200

    # Read it back and confirm updated content
    r3 = client.get("/api/profiles/same")
    assert r3.status_code == 200
    returned = r3.json()
    assert returned["header"]["title"] == "Backend Dev v2"


def test_unicode_name_and_content_roundtrip(client):
    """Ensure Unicode profile names and content round-trip correctly."""
    prof = _good_profile()
    prof["header"]["name"] = "تامر حمّاد فاعور"
    prof["contact"]["email"] = "tamer@example.com"

    r = client.post("/api/profiles/save", json={"name": "سيرتي", "profile": prof})
    assert r.status_code == 200, r.text

    r2 = client.get("/api/profiles/سيرتي")
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["header"]["name"] == "تامر حمّاد فاعور"
