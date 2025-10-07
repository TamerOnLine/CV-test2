from __future__ import annotations
import streamlit as st

def render(profile: dict) -> dict:
    st.subheader("Basic Info")
    c1, c2 = st.columns(2)
    with c1:
        profile.setdefault("header", {})
        profile["header"]["name"] = st.text_input("Full Name", profile["header"].get("name", ""), key="name")
    with c2:
        profile.setdefault("header", {})
        profile["header"]["title"] = st.text_input("Title", profile["header"].get("title", ""), key="title")
    return profile
