from __future__ import annotations
import streamlit as st

def render_skills_languages() -> None:
    st.header("Skills & Languages")
    c3, c4 = st.columns(2)
    with c3:
        st.text_area("Skills (comma-separated or one per line)", key="skills_text", height=180)
    with c4:
        st.text_area(
            "Languages (comma-separated or one per line)",
            key="languages_text",
            height=180,
            placeholder="Arabic (Native), German - B1, English - B2",
        )
