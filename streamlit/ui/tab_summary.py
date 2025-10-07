# streamlit/ui/tab_summary.py
from __future__ import annotations
import streamlit as st

def render(profile: dict) -> dict:
    st.subheader("Summary / About Me")
    rev = st.session_state.get("profile_rev", 0)

    current = str(profile.get("summary") or "").strip()

    with st.form(key=f"summary_form_{rev}", clear_on_submit=False):
        summary_text = st.text_area(
            "Short professional summary",
            current,
            height=180,
            key=f"summary_text_{rev}",
            placeholder="Example:\n"
                       "Backend Developer experienced with FastAPI, PostgreSQL, and AI-powered tools. "
                       "Focused on scalable APIs, clean architecture, and automation.",
            help="Keep it concise (3–6 lines). This text appears near the top of your PDF résumé.",
        )
        submitted = st.form_submit_button("Save summary")

    if submitted:
        new_val = summary_text.strip()
        if new_val != current:
            profile["summary"] = new_val
            st.session_state["profile_rev"] = rev + 1
            st.success("Summary updated.")
        else:
            st.info("No changes detected.")

    return profile
