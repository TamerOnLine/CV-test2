from __future__ import annotations
from typing import Any, Dict, List

def _as_list(x: Any) -> List[str]:
    if x is None: return []
    if isinstance(x, (list, tuple, set)): return [str(i) for i in x if i is not None]
    return [str(x)]

def _as_projects(items: Any) -> List[List[str]]:
    out: List[List[str]] = []
    if not items: return out
    for it in (items or []):
        if isinstance(it, (list, tuple)):
            name = str(it[0]) if len(it) > 0 else ""
            desc = str(it[1]) if len(it) > 1 else ""
            url  = str(it[2]) if len(it) > 2 and it[2] is not None else ""
            if name or desc or url: out.append([name, desc, url])
        elif isinstance(it, dict):
            name = str(it.get("name","") or it.get("title",""))
            desc = str(it.get("desc","") or it.get("description",""))
            url  = str(it.get("url",""))
            if name or desc or url: out.append([name, desc, url])
        else:
            s = str(it).strip()
            if s: out.append([s, "", ""])
    return out

def map_education_rows_to_items(edu_rows: List[List[str]]) -> List[str]:
    items: List[str] = []
    for row in edu_rows or []:
        title, school, start, end, details, url = (row + [""]*6)[:6]
        lines = [x for x in [title.strip(), school.strip(),
                             (f"{start.strip()} – {end.strip()}").strip(" –"),
                             details.strip(), url.strip()] if x]
        if lines: items.append("\n".join(lines))
    return items

def profile_to_overrides(profile: Dict[str, Any]) -> Dict[str, Any]:
    p = profile or {}
    ov: Dict[str, Any] = {}

    # header_name
    hdr = p.get("header") or {}
    if hdr.get("name") or hdr.get("title"):
        ov["header_name"] = {"data": {"name": hdr.get("name",""), "title": hdr.get("title","")}}

    # contact_info - MUST be {"items": {...}}
    contact = p.get("contact") or {}
    if contact:
        ov["contact_info"] = {"data": {"items": dict(contact)}}

    # key_skills expects "skills"
    skills = p.get("skills") or []
    if skills:
        ov["key_skills"] = {"data": {"skills": list(skills)}}

    # languages expects "languages"
    languages = p.get("languages") or []
    if languages:
        ov["languages"] = {"data": {"languages": list(languages)}}

    # projects expects "items": [[title,desc,url], ...]
    projs = _as_projects(p.get("projects"))
    if projs:
        ov["projects"] = {"data": {"items": projs}}

    # summary -> text_section:summary
    summary = (p.get("summary") or "").strip()
    if summary:
        ov["text_section:summary"] = {"data": {"section": "summary", "text": summary}}

    # social_links يمكن استخدام contact كمدخل
    if contact:
        # يَسمح البلوك بإدخال مباشر لمفاتيح مثل github/linkedin/website...
        ov["social_links"] = {"data": dict(contact)}

    # avatar_b64 -> avatar_circle.photo_b64
    if p.get("avatar_b64"):
        ov["avatar_circle"] = {"data": {"photo_b64": p["avatar_b64"], "max_d_mm": 42}}

    # education -> list of multiline strings
    edu = p.get("education") or []
    ed_items = map_education_rows_to_items(edu)
    if ed_items:
        ov["education"] = {"data": {"items": ed_items}}

    return ov
