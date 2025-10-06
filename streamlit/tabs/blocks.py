from __future__ import annotations
import streamlit as st

from .projects_block import render_projects_block
from .education_block import render_education_block
from .left_sections_block import render_left_sections_block
from .right_sections_block import render_right_sections_block


def render_blocks() -> None:
    st.header("Free-text Blocks")

    sub_tabs = st.tabs(["Projects", "Education", "Left Sections", "Right Sections"])
    with sub_tabs[0]:
        render_projects_block()
    with sub_tabs[1]:
        render_education_block()
    with sub_tabs[2]:
        render_left_sections_block()
    with sub_tabs[3]:
        render_right_sections_block()
