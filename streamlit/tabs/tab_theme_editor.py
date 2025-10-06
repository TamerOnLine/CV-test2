# streamlit/tabs/tab_theme_editor.py
from __future__ import annotations
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR   = PROJECT_ROOT / "themes"
LAYOUTS_DIR  = PROJECT_ROOT / "layouts"

def _list_names(dir_path: Path, suffix: str) -> list[str]:
    if not dir_path.exists():
        return []
    items = []
    for p in dir_path.glob(f"*{suffix}"):
        # أمثلة: aqua-card-3col.theme.json  → aqua-card-3col
        name = p.name
        if name.endswith(suffix):
            items.append(name[: -len(suffix)])
    items.sort()
    return items

def theme_selector() -> tuple[str, str | None]:
    st.subheader("🎨 Theme & Layout")

    # اقرأ القوائم ديناميكيًا
    theme_names  = _list_names(THEMES_DIR,  ".theme.json")
    layout_names = _list_names(LAYOUTS_DIR, ".layout.json")

    # حماية من الفراغ
    if not theme_names:
        theme_names = ["default"]  # fallback منطقي
    theme_idx = 0
    if "theme_name" in st.session_state and st.session_state["theme_name"] in theme_names:
        theme_idx = theme_names.index(st.session_state["theme_name"])

    theme_name = st.selectbox("Theme", theme_names, index=theme_idx, key="theme_name")

    # لو لقيّنا layouts اعرض Dropdown، وإلا رجّع None
    layout_name = None
    if layout_names:
        layout_idx = 0
        if "layout_name" in st.session_state and st.session_state["layout_name"] in layout_names:
            layout_idx = layout_names.index(st.session_state["layout_name"])
        layout_name = st.selectbox("Layout (optional)", layout_names, index=layout_idx, key="layout_name")
    else:
        st.info("No layout files found in ./layouts — using theme’s built-in layout if any.", icon="ℹ️")

    st.caption("Lists are read live from the folders: ./themes and ./layouts")
    return theme_name, layout_name
