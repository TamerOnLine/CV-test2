from __future__ import annotations
import streamlit as st
from core.io_utils import to_lines

def render(profile: dict) -> dict:
    st.subheader("Skills")
    skills_text = st.text_area(
        "One per line",
        "\n".join(profile.get("skills") or []),
        height=180,
        key="skills_text",
    )
    profile["skills"] = to_lines(skills_text)
    return profile
