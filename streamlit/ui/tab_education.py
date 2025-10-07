from __future__ import annotations
import streamlit as st
import pandas as pd

EDU_COLUMNS = ["Title / Program", "School", "Start", "End", "Details", "URL"]

def _ensure_education_rows(ed):
    rows = []
    if isinstance(ed, list):
        for it in ed:
            if isinstance(it, (list, tuple)):
                vals = list(it) + [""] * (6 - len(it))
                rows.append(vals[:6])
            elif isinstance(it, dict):
                rows.append([
                    it.get("title", ""),
                    it.get("school", ""),
                    it.get("start", ""),
                    it.get("end", ""),
                    it.get("details", ""),
                    it.get("url", ""),
                ])
            else:
                rows.append(["", "", "", "", str(it), ""])
    return rows or [["", "", "", "", "", ""]]

def render(profile: dict) -> dict:
    st.subheader("Education / Training")
    ed_rows = _ensure_education_rows(profile.get("education", []))
    df_edu = pd.DataFrame(ed_rows, columns=EDU_COLUMNS)

    st.caption("Use the table below to edit your education entries:")
    edited = st.data_editor(
        df_edu,
        num_rows="dynamic",
        key="education_editor",
        width='stretch',
        column_config={
            "Title / Program": st.column_config.TextColumn(width="large"),
            "School": st.column_config.TextColumn(width="large"),
            "Start": st.column_config.TextColumn(help="e.g., 06/2024"),
            "End": st.column_config.TextColumn(help="e.g., 12/2024 or Present"),
            "Details": st.column_config.TextColumn(width="large"),
            "URL": st.column_config.LinkColumn(),
        },
    )
    profile["education"] = edited.fillna("").values.tolist()
    st.info("💡 Tip: Leave URL empty if not applicable.")
    return profile
