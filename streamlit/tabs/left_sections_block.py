from __future__ import annotations
import streamlit as st

def render_left_sections_block() -> None:
    st.text_area(
        "Left sections (format: [Title] and lines starting with -)",
        key="sections_left_text",
        height=160,
    )
