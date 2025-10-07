from __future__ import annotations
import streamlit as st

def render(profile: dict) -> dict:
    st.subheader("Summary / About Me")
    profile["summary"] = st.text_area(
        "Short professional summary",
        profile.get("summary") or "",
        height=180,
        key="summary_text",
    )
    return profile
