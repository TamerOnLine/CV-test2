from __future__ import annotations

import json
import os
import re
from pathlib import Path

import streamlit as st
from utils import (
    atomic_write_json,
    encode_photo_to_b64,
    decode_photo_from_b64,
)

# ── Helpers ─────────────────────────────────────────────────────────────
_SEPS = re.compile(r"[;\n\r\u2022\-\u2013\u2014]+")

def _as_list(v):
    if not v:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in _SEPS.split(str(v)) if x.strip()]

def _normalize_simple_to_profile(simple: dict) -> dict:
    """
    Converts a flat or simplified JSON input into the standard profile structure.

    Args:
        simple (dict): Simplified profile dictionary.

    Returns:
        dict: Normalized profile dictionary.
    """
    name = simple.get("name") or simple.get("full_name") or ""
    title = simple.get("title") or simple.get("headline") or "Backend Developer"
    email = simple.get("email") or ""
    phone = simple.get("phone") or ""
    loc = simple.get("location") or simple.get("city") or ""

    projects = simple.get("projects")
    if not (isinstance(projects, list) and projects and isinstance(projects[0], list)):
        projects = [[ln, "", ""] for ln in _as_list(simple.get("projects") or simple.get("projects_text"))]

    social = []
    if simple.get("github"):
        social.append(["GitHub", str(simple["github"])])
    if simple.get("linkedin"):
        social.append(["LinkedIn", str(simple["linkedin"])])
    if simple.get("website"):
        social.append(["Website", str(simple["website"])])

    profile = {
        "header": {"name": name, "title": title},
        "contact": {"email": email, "phone": phone, "location": loc},
        "summary": _as_list(simple.get("summary") or simple.get("about") or simple.get("summary_text")),
        "skills": _as_list(simple.get("skills") or simple.get("skills_text")),
        "languages": _as_list(simple.get("languages") or simple.get("languages_text")),
        "projects": projects or [["Project", "Description", ""]],
        "education": _as_list(simple.get("education") or simple.get("education_text")),
        "social_links": social,
    }
    return profile

def _build_profile_from_session() -> dict:
    """
    Constructs profile dictionary from Streamlit session state values.

    Returns:
        dict: Profile dictionary built from session.
    """
    simple = {
        "name": st.session_state.get("name"),
        "title": st.session_state.get("title"),
        "email": st.session_state.get("email"),
        "phone": st.session_state.get("phone"),
        "location": st.session_state.get("location"),
        "github": st.session_state.get("github"),
        "linkedin": st.session_state.get("linkedin"),
        "summary_text": st.session_state.get("sections_right_text") or st.session_state.get("summary_text"),
        "skills_text": st.session_state.get("skills_text"),
        "languages_text": st.session_state.get("languages_text"),
        "projects_text": st.session_state.get("projects_text"),
        "education_text": st.session_state.get("education_text"),
    }
    return _normalize_simple_to_profile(simple)

# ── UI ──────────────────────────────────────────────────────────────────
def render_sidebar(profiles_dir: Path) -> None:
    """
    Renders the Streamlit sidebar UI for loading and saving profile JSON.

    Args:
        profiles_dir (Path): Directory path to save/load profiles.
    """
    with st.sidebar:
        st.subheader("API")
        st.text_input("API Base URL", key="api_base", help="Example: http://127.0.0.1:8000")

        st.subheader("Profile JSON")
        uploaded_json = st.file_uploader("Browse JSON", type=["json"], key="json_uploader")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Load uploaded"):
                if uploaded_json:
                    try:
                        data = json.load(uploaded_json)

                        for k in [
                            "name", "title", "location", "phone", "email", "github", "linkedin", "birthdate",
                            "skills_text", "languages_text", "projects_text", "education_text",
                            "sections_left_text", "sections_right_text", "rtl_mode", "website"
                        ]:
                            if k in data:
                                st.session_state[k] = data[k]

                        photo_b64 = data.get("photo_b64")
                        photo_mime = data.get("photo_mime")
                        photo_name = data.get("photo_name")
                        if photo_b64:
                            st.session_state.photo_bytes = decode_photo_from_b64(photo_b64, photo_mime)
                            st.session_state.photo_mime = photo_mime or "image/png"
                            st.session_state.photo_name = photo_name or "photo.png"

                        if isinstance(data, dict) and isinstance(data.get("profile"), dict):
                            st.session_state["profile_data"] = data["profile"]
                        else:
                            st.session_state["profile_data"] = _normalize_simple_to_profile(data)

                        st.success("JSON loaded.", icon="✅")
                    except Exception as e:
                        st.error(f"Invalid JSON: {e}")
                else:
                    st.warning("No file selected.")

        with col2:
            if st.button("Save current"):
                b64, mime, name = encode_photo_to_b64(
                    st.session_state.get("photo_bytes"),
                    st.session_state.get("photo_mime"),
                    st.session_state.get("photo_name"),
                )
                payload = {
                    "name": st.session_state.get("name"),
                    "title": st.session_state.get("title"),
                    "location": st.session_state.get("location"),
                    "phone": st.session_state.get("phone"),
                    "email": st.session_state.get("email"),
                    "github": st.session_state.get("github"),
                    "linkedin": st.session_state.get("linkedin"),
                    "birthdate": st.session_state.get("birthdate"),
                    "skills_text": st.session_state.get("skills_text"),
                    "languages_text": st.session_state.get("languages_text"),
                    "projects_text": st.session_state.get("projects_text"),
                    "education_text": st.session_state.get("education_text"),
                    "sections_left_text": st.session_state.get("sections_left_text"),
                    "sections_right_text": st.session_state.get("sections_right_text"),
                    "rtl_mode": bool(st.session_state.get("rtl_mode")),
                    "photo_b64": b64, "photo_mime": mime, "photo_name": name,
                    "profile": st.session_state.get("profile_data") or _build_profile_from_session(),
                }
                from datetime import datetime
                profiles_dir.mkdir(exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                out = profiles_dir / f"profile-{ts}.json"
                atomic_write_json(out, payload)
                st.success(f"Saved: {out.name}")
