from __future__ import annotations
import streamlit as st
from utils import guess_mime_from_name

def render_headshot() -> None:
    st.header("Headshot (optional)")
    photo_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg", "webp"])
    colp1, colp2 = st.columns(2)

    with colp1:
        if photo_file is not None:
            st.session_state.photo_bytes = photo_file.read()
            st.session_state.photo_mime = guess_mime_from_name(photo_file.name)
            st.session_state.photo_name = photo_file.name
            st.success("Photo uploaded.")
        if st.session_state.photo_bytes:
            st.image(
                st.session_state.photo_bytes,
                caption=st.session_state.photo_name,
                width="stretch",  # replaces deprecated use_container_width
            )

    with colp2:
        if st.button("Remove photo"):
            st.session_state.photo_bytes = None
            st.session_state.photo_mime = None
            st.session_state.photo_name = None
