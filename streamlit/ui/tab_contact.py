from __future__ import annotations
import streamlit as st

def render(profile: dict) -> dict:
    st.subheader("Contact Info")
    profile.setdefault("contact", {})
    c1, c2 = st.columns(2)
    with c1:
        profile["contact"]["email"] = st.text_input("Email", profile["contact"].get("email", ""), key="email")
        profile["contact"]["website"] = st.text_input("Website", profile["contact"].get("website", ""), key="website")
    with c2:
        profile["contact"]["phone"] = st.text_input("Phone", profile["contact"].get("phone", ""), key="phone")
        profile["contact"]["github"] = st.text_input("GitHub", profile["contact"].get("github", ""), key="github")
        profile["contact"]["linkedin"] = st.text_input("LinkedIn", profile["contact"].get("linkedin", ""), key="linkedin")

    # optional location
    profile["contact"]["location"] = st.text_input("Location (optional)", profile["contact"].get("location", ""), key="location")
    return profile
