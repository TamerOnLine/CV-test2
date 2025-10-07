# api/routers/profiles.py
from fastapi import APIRouter, HTTPException
from typing import List
from pathlib import Path
import json

from api.models.profile import Profile

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

BASE_DIR = Path(__file__).resolve().parents[2]  # عدّل لو مسارك مختلف
PROFILES_DIR = (BASE_DIR / "profiles")
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

def _path_for(name: str) -> Path:
    safe = "".join(c for c in name.strip() if c.isalnum() or c in "-_ .").strip()
    if not safe:
        raise HTTPException(status_code=400, detail="Invalid profile name")
    return PROFILES_DIR / f"{safe}.json"

@router.get("/", response_model=List[str])
def list_profiles():
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))

@router.get("/{name}", response_model=Profile)
def get_profile(name: str):
    p = _path_for(name)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Profile not found")
    try:
        data = json.loads(p.read_text("utf-8"))
        return Profile.model_validate(data)  # يعيد مع التحقق
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Corrupt file: {e}")

@router.post("/{name}", response_model=Profile)
def save_profile(name: str, profile: Profile):
    p = _path_for(name)
    data = profile.model_dump(exclude_none=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return profile

@router.delete("/{name}")
def delete_profile(name: str):
    p = _path_for(name)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Profile not found")
    p.unlink()
    return {"ok": True}
