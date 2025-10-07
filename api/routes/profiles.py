# api/routes/profiles.py
from fastapi import APIRouter, HTTPException, Response
from pathlib import Path
from pydantic import ValidationError
from api.models.profile import Profile
import re
import json

router = APIRouter(tags=["profiles"])  # لا نضع prefix هنا لأن main.py يضيف "/api"

# ─────────────────────────────
# 🗂️ إعداد مجلد التخزين
# ─────────────────────────────
PROFILES_DIR = Path(__file__).resolve().parents[1] / "profiles"
SAFE_SUFFIX = ".json"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────
# 🔒 دوال مساعدة للتحقق من الأمان
# ─────────────────────────────
def _sanitize_name(name: str) -> str:
    """
    يتحقق من أن الاسم صالح: أحرف/أرقام/شرطات فقط.
    يرفض أي محاولة لاختراق المسار مثل ../ أو رموز غير مسموحة.
    """
    s = (name or "").strip()
    if not s:
        raise ValueError("Empty profile name not allowed")

    # فقط الحروف، الأرقام، الشرطات
    if not re.fullmatch(r"[A-Za-z0-9_-]+", s):
        raise ValueError("Invalid characters in profile name")

    # حظر النقاط أو الشرطات الخلفية أو الأمامية
    if any(x in s for x in ("..", "/", "\\", ".")):
        raise ValueError("Invalid profile name")

    return s


def _safe_profile_path(name: str) -> Path:
    """يُعيد مسارًا آمنًا داخل مجلد profiles فقط."""
    base = _sanitize_name(name)
    p = (PROFILES_DIR / f"{base}{SAFE_SUFFIX}").resolve()
    if PROFILES_DIR.resolve() not in p.parents:
        raise ValueError("Invalid path")
    return p


# ─────────────────────────────
# 📦 نقاط الـ API
# ─────────────────────────────

@router.post("/profiles/save")
def save_profile(item: dict):
    """
    يحفظ ملف بروفايل آمن بعد التحقق من صحته بـ Pydantic.
    JSON المتوقع:
      {
        "name": "my_profile",
        "profile": { ... هيكل Profile ... }
      }
    """
    try:
        profile = Profile(**(item.get("profile") or {}))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    name = item.get("name") or "profile"
    try:
        path = _safe_profile_path(name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 🔧 dump بشكل متوافق مع Pydantic v2
    data_dict = profile.model_dump(exclude_none=True)
    path.write_text(json.dumps(data_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"ok": True, "file": path.name}


# 🗂️ ضع المسار الثابت أولاً حتى لا يلتقطه {name}
@router.get("/profiles/list")
def list_profiles():
    """يعيد قائمة بكل ملفات البروفايلات المخزنة."""
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


@router.get("/profiles/{name}")
def load_profile(name: str):
    """يقرأ بروفايل JSON موجود."""
    try:
        path = _safe_profile_path(name.replace(".json", ""))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not path.exists():
        raise HTTPException(status_code=404, detail="Profile not found")

    data = path.read_text(encoding="utf-8")
    return Response(content=data, media_type="application/json; charset=utf-8")


@router.delete("/profiles/{name}")
def delete_profile(name: str):
    """يحذف بروفايل بأمان."""
    try:
        path = _safe_profile_path(name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not path.exists():
        raise HTTPException(status_code=404, detail="Profile not found")

    path.unlink()
    return {"ok": True, "deleted": path.name}
