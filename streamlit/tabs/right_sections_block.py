from __future__ import annotations
import streamlit as st

def render_right_sections_block() -> None:
    st.text_area(
        "Right sections (format: [Title] and lines starting with -)",
        key="sections_right_text",
        height=160,
    )
