# api/routes/profiles.py
from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json

router = APIRouter()

APP_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = APP_ROOT / "profiles"
PROFILES_DIR.mkdir(exist_ok=True)

class Profile(BaseModel):
    header: Dict[str, str] = Field(default_factory=dict)
    contact: Dict[str, str] = Field(default_factory=dict)
    summary: Optional[str] = ""
    skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    projects: List[List[str]] = Field(default_factory=list)      # [[title, desc, url], ...]
    education: List[List[str]] = Field(default_factory=list)     # [[title, school, start, end, details, url], ...]
    social: Dict[str, str] = Field(default_factory=dict)
    avatar_b64: Optional[str] = None

def _read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))

def _write_json(p: Path, data: Dict[str, Any]) -> None:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

@router.get("/profiles", response_model=List[str])
def list_profiles():
    return [p.stem for p in PROFILES_DIR.glob("*.json")]

@router.get("/profiles/{name}", response_model=Profile)
def get_profile(name: str):
    fp = PROFILES_DIR / f"{name}.json"
    if not fp.exists():
        raise HTTPException(404, f"profile '{name}' not found")
    return _read_json(fp)

@router.post("/profiles/{name}", response_model=Profile)
def save_profile(name: str, payload: Profile):
    fp = PROFILES_DIR / f"{name}.json"
    _write_json(fp, payload.model_dump())
    return payload
