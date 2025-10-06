from __future__ import annotations
import streamlit as st

def render_basic_info() -> None:
    st.header("Basic Info")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Full name", key="name")
        st.text_input("Location (City, Country)", key="location")
        st.text_input("Phone", key="phone")
        st.text_input("Email", key="email")
    with c2:
        st.text_input("GitHub (handle or URL)", key="github")
        st.text_input("LinkedIn (handle or URL)", key="linkedin")
        st.text_input("Birthdate", key="birthdate")
        st.checkbox("Enable RTL for right-side sections", key="rtl_mode")
