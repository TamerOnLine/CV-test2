from __future__ import annotations

import streamlit as st

from core.io_utils import to_lines

def render(profile: dict) -> dict:
    """
    Render the Languages tab in the Streamlit UI.

    Args:
        profile (dict): The user's profile data.

    Returns:
        dict: Updated profile dictionary with parsed languages.
    """
    st.subheader("Languages")
    rev = st.session_state.get("profile_rev", 0)

    key = f"languages_text_{rev}"
    default = "\n".join(profile.get("languages") or [])
    st.session_state.setdefault(key, default)

    langs_text = st.text_area(
        "One per line (e.g., Arabic — Native)",
        key=key,
        height=150,
    )

    profile["languages"] = to_lines(langs_text)
    return profile
