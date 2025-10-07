from __future__ import annotations
import streamlit as st
from core.io_utils import to_lines

def render(profile: dict) -> dict:
    st.subheader("Languages")
    langs_text = st.text_area(
        "One per line (e.g., Arabic — Native)",
        "\n".join(profile.get("languages") or []),
        height=150,
        key="languages_text",
    )
    profile["languages"] = to_lines(langs_text)
    return profile
