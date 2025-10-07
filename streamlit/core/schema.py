from __future__ import annotations
import json
from typing import Any, Dict

DEFAULT_PROFILE: Dict[str, Any] = {
    "header": {"name": "", "title": ""},
    "contact": {"email": "", "phone": "", "website": "", "github": "", "linkedin": "", "location": ""},
    "skills": [],
    "languages": [],
    "projects": [],
    "education": [],
    "summary": "",
}

def ensure_profile_schema(p: dict | None) -> dict:
    """Normalize incoming 'profile' into our DEFAULT_PROFILE structure."""
    base = json.loads(json.dumps(DEFAULT_PROFILE))  # simple deep copy
    if not isinstance(p, dict):
        return base

    if "profile" in p and isinstance(p["profile"], dict):
        p = p["profile"]

    for k in ("header", "contact"):
        src = p.get(k) or {}
        if isinstance(src, dict):
            base[k].update(src)

    if isinstance(p.get("skills"), list): base["skills"] = p["skills"]
    if isinstance(p.get("languages"), list): base["languages"] = p["languages"]
    if isinstance(p.get("education"), list): base["education"] = p["education"]
    if "summary" in p and isinstance(p.get("summary"), (str, list, dict)):
        base["summary"] = p["summary"]

    prj = p.get("projects")
    if isinstance(prj, list):
        norm = []
        for row in prj:
            if isinstance(row, (list, tuple)):
                title = (str(row[0]) if len(row) > 0 and row[0] is not None else "").strip()
                desc  = (str(row[1]) if len(row) > 1 and row[1] is not None else "").strip()
                url   = (str(row[2]) if len(row) > 2 and row[2] is not None else "").strip()
            elif isinstance(row, dict):
                title = str(row.get("title", "")).strip()
                desc  = str(row.get("description", "")).strip()
                url   = str(row.get("url", "")).strip()
            else:
                title = str(row).strip()
                desc = url = ""
            if title or desc or url:
                norm.append([title, desc, url])
        base["projects"] = norm

    return base
