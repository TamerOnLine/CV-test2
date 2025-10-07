from __future__ import annotations
import json
import streamlit as st
from pathlib import Path

from core.paths import THEMES_DIR, LAYOUTS_DIR, PROFILES_DIR
from core.io_utils import read_json_file, save_profile, load_profile, list_json_names
from core.schema import ensure_profile_schema

def render_sidebar() -> dict:
    """
    Render sidebar controls and return settings dict:
    {
      base_url, ui_lang, rtl_mode, theme_name, layout_file
    }
    """
    with st.sidebar:
        st.header("⚙️ Controls")

        base_url = st.text_input("API Base URL", value="http://127.0.0.1:8000", key="api_base")
        ui_lang = st.selectbox("UI Language", ["en", "de", "ar"], index=0, key="ui_lang")
        rtl_mode = st.toggle("RTL mode", value=(ui_lang == "ar"), key="rtl_mode")

        theme_files = list_json_names(THEMES_DIR)
        theme_name = st.selectbox("Theme", theme_files or ["default.theme.json"], key="theme_name")

        layout_files = list_json_names(LAYOUTS_DIR)
        layout_default_index = 1 if layout_files else 0
        layout_file = st.selectbox("Layout", ["(none)"] + layout_files, index=layout_default_index, key="layout_file")

        st.markdown("---")
        st.subheader("💾 Profiles")

        existing_profiles = list_json_names(PROFILES_DIR)
        col_p_load, col_p_save = st.columns(2)

        with col_p_load:
            selected_profile = st.selectbox("Select profile", ["(none)"] + existing_profiles, index=0, key="selected_profile")
            if st.button("📂 Load Profile", key="btn_load_profile"):
                if selected_profile and selected_profile != "(none)":
                    loaded = load_profile(Path(PROFILES_DIR) / selected_profile)
                    st.session_state.profile = ensure_profile_schema(loaded)
                    st.success(f"Loaded profile: {selected_profile}")

        with col_p_save:
            profile_name = st.text_input("Save as", value="my_profile.json", key="save_profile_as")
            if st.button("💾 Save Profile", key="btn_save_profile"):
                filename = profile_name.strip()
                if not filename.endswith(".json"):
                    filename += ".json"
                try:
                    save_profile(Path(PROFILES_DIR) / filename, ensure_profile_schema(st.session_state.profile))
                    st.success(f"Saved: {filename}")
                except Exception as e:
                    st.error(f"Save failed: {e}")

        st.markdown("---")
        up = st.file_uploader("Import profile (.json)", type=["json"], key="uploader_profile")
        if up is not None and st.button("Import now", key="btn_import_now"):
            try:
                imported = json.loads(up.getvalue().decode("utf-8"))
                st.session_state.profile = ensure_profile_schema(imported)
                st.success("Imported profile applied to the form.")
            except Exception as e:
                st.error(f"Import failed: {e}")

        if st.button("⬇️ Export current as JSON", key="btn_export_json"):
            st.download_button(
                "Download JSON",
                data=json.dumps(ensure_profile_schema(st.session_state.profile), ensure_ascii=False, indent=2).encode("utf-8"),
                file_name="profile_export.json",
                mime="application/json",
                key="download_export_json",
            )

    return {
        "base_url": base_url,
        "ui_lang": ui_lang,
        "rtl_mode": rtl_mode,
        "theme_name": theme_name,
        "layout_file": layout_file,
    }
