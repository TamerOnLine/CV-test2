from __future__ import annotations

import streamlit as st

from core.io_utils import to_lines

def render(profile: dict) -> dict:
    """
    Render the skills editing interface in a Streamlit app.

    Args:
        profile (dict): A dictionary containing profile information.

    Returns:
        dict: Updated profile dictionary with modified skills.
    """
    st.subheader("Skills")
    rev = st.session_state.get("profile_rev", 0)

    key = f"skills_text_{rev}"
    default = "\n".join(profile.get("skills") or [])
    st.session_state.setdefault(key, default)

    skills_text = st.text_area(
        "One per line (e.g., Python, FastAPI, Docker...)",
        key=key,
        height=180,
    )

    profile["skills"] = to_lines(skills_text)
    return profile
