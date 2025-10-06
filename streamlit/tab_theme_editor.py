import streamlit as st

def theme_selector():
    """
    Renders the theme and layout selection inputs in the UI.

    Returns:
        tuple[str, str | None]: Selected theme name and layout name.
    """
    st.subheader("🎨 Theme")

    theme_name = st.selectbox(
        "Choose a theme",
        [
            "default", "modern", "clean-white", "bold-header",
            "bold-panel", "aqua-card-3col", "grid-pro", "modern-pro"
        ],
        index=0,
    )

    layout_name = st.selectbox(
        "Layout (optional)",
        ["", "left-panel", "two-col-red", "three-column-rtl", "single-column"],
        index=0,
    )

    layout_name = layout_name or None
    return theme_name, layout_name
