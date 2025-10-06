from __future__ import annotations
import streamlit as st

def render_education_block() -> None:
    st.text_area(
        "Education (blocks separated by a blank line)",
        key="education_text",
        height=160,
    )
