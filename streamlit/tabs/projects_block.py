from __future__ import annotations
import streamlit as st

def render_projects_block() -> None:
    st.text_area(
        "Projects (each project as a block: first line = title, following lines = bullets, optional link line, then a blank line)",
        key="projects_text",
        height=200,
        placeholder="My App\n- bullet 1\n- bullet 2\nhttps://github.com/...\n\nProject 2\nDetails...",
    )
