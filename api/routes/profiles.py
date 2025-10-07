# api/routes/profiles.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
import json, re

router = APIRouter(prefix="/profiles", tags=["profiles"])

# âœ”ï¸ڈ ط§ط¬ط¹ظ„ ط§ظ„طھط®ط²ظٹظ† ط¯ط§ط¦ظ…ط§ظ‹ ظپظٹ ط¬ط°ط± ط§ظ„ظ…ط´ط±ظˆط¹: <root>/profiles
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR  = PROJECT_ROOT / "profiles"
PROFILE_DIR.mkdir(exist_ok=True)

def _clean_name(name: str) -> str:
    n = (name or "").strip().lower()
    n = re.sub(r"[^\w\-]+", "-", n).strip("-")
    if n.endswith(".json"):
        n = n[:-5]
    return n or "profile"

class SavePayload(BaseModel):
    name: str
    profile: dict

@router.get("/list")
def list_profiles() -> list[str]:
    return sorted(p.stem for p in PROFILE_DIR.glob("*.json"))

@router.get("/load")
def load_profile(name: str = Query(..., min_length=1)) -> dict:
    n = _clean_name(name)
    path = PROFILE_DIR / f"{n}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"profile '{n}' not found")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"read error: {e}")

@router.post("/save")
def save_profile(payload: SavePayload) -> dict:
    n = _clean_name(payload.name)
    path = PROFILE_DIR / f"{n}.json"
    try:
        path.write_text(json.dumps(payload.profile, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "name": n}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"write error: {e}")

