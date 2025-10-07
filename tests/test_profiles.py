# tests/test_profiles.py
from fastapi.testclient import TestClient
import json
import importlib

import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """
    نحول مجلد الحفظ PROFILES_DIR إلى tmp_path أثناء الاختبار.
    ثم نُعيد تحميل الراوتر لضمان استخدام القيمة المحدثة.
    """
    # استيراد الراوتر وتعديل PROFILES_DIR
    profiles_mod = importlib.import_module("api.routes.profiles")
    monkeypatch.setattr(profiles_mod, "PROFILES_DIR", tmp_path, raising=True)
    profiles_mod.PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    # إعادة تحميل الموديون لضمان عمل التغيير في الدوال
    importlib.reload(profiles_mod)

    # الآن حمّل التطبيق
    from api.main import app
    return TestClient(app)


def _good_profile():
    # ملف بروفايل صالح وفق Pydantic (كل الحقول optional تقريبًا)
    return {
        "header": {"name": "Tamer", "title": "Backend Developer"},
        "contact": {"email": "tamer@example.com", "github": "TamerOnLine"},
        "skills": ["FastAPI", "PostgreSQL", "Streamlit"],
        "projects": [],
        "languages": ["Arabic", "English"],
        "education": [],
    }


def test_save_and_get_profile(client):
    payload = {
        "name": "my_profile",
        "profile": _good_profile(),
    }
    r = client.post("/api/profiles/save", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["file"] == "my_profile.json"

    # read back
    r2 = client.get("/api/profiles/my_profile")
    assert r2.status_code == 200, r2.text
    returned = r2.json()  # GET يُعيد JSON نصي؛ TestClient يحوله dict
    assert returned["header"]["name"] == "Tamer"
    assert returned["contact"]["github"] == "TamerOnLine"


def test_list_profiles(client):
    # احفظ اثنين
    for name in ("p1", "p2"):
        r = client.post("/api/profiles/save", json={"name": name, "profile": _good_profile()})
        assert r.status_code == 200

    r = client.get("/api/profiles/list")
    assert r.status_code == 200
    names = r.json()
    assert set(names) >= {"p1", "p2"}


def test_delete_profile(client):
    # احفظ ثم احذف
    client.post("/api/profiles/save", json={"name": "delme", "profile": _good_profile()})
    r = client.delete("/api/profiles/delme")
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # الآن يجب أن يكون 404
    r2 = client.get("/api/profiles/delme")
    assert r2.status_code == 404


def test_invalid_name_rejected(client):
    # أسماء غير آمنة يجب أن تُرفض (Path Traversal)
    bad = {"name": "../../etc/passwd", "profile": _good_profile()}
    r = client.post("/api/profiles/save", json=bad)
    assert r.status_code == 400


def test_validation_error_on_invalid_email(client):
    bad_profile = _good_profile()
    bad_profile["contact"]["email"] = "not-an-email"
    r = client.post("/api/profiles/save", json={"name": "badmail", "profile": bad_profile})
    assert r.status_code == 422
    # اختيارياً: تأكد أن التفاصيل من Pydantic موجودة
    detail = r.json().get("detail", [])
    assert any("email" in json.dumps(detail).lower() for _ in [0])
