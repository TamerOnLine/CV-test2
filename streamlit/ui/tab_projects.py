from __future__ import annotations
import streamlit as st
import pandas as pd
from core.io_utils import projects_df_to_list

def render(profile: dict) -> dict:
    st.subheader("Projects")
    existing = profile.get("projects") or []
    df = pd.DataFrame(existing, columns=["Title", "Description", "URL"]) if existing else pd.DataFrame(
        [{"Title": "", "Description": "", "URL": ""}]
    )
    edited = st.data_editor(df, num_rows="dynamic", key="projects_editor", width="stretch")
    profile["projects"] = projects_df_to_list(edited)
    return profile
