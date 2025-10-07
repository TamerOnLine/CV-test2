from __future__ import annotations
import io
from typing import Optional
import streamlit as st
from PIL import Image

def _square_center_crop(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))

def _to_png_bytes(img: Image.Image, quality: int = 92) -> bytes:
    buf = io.BytesIO()
    # PNG لا يستخدم quality، لكن نخليها للاتساق لو غيرت لصيغة ثانية
    img.save(buf, format="PNG")
    return buf.getvalue()

def render(profile: dict) -> dict:
    st.subheader("Headshot / Photo")
    up = st.file_uploader("Upload an image (PNG/JPG/WebP)", type=["png", "jpg", "jpeg", "webp"], key="photo_uploader")

    col1, col2, col3 = st.columns([1, 1, 1])

    if up:
        img = Image.open(up).convert("RGBA")
        st.session_state._raw_img = img
        with col1:
            st.caption("Original")
            st.image(img, use_container_width=True)
        # قص مركزي مربّع
        cropped = _square_center_crop(img)
        st.session_state._cropped_img = cropped

        with col2:
            st.caption("Square crop")
            st.image(cropped, use_container_width=True)

        # اختيار القطر التقريبي (لـ avatar_circle داخل PDF)
        with col3:
            st.caption("Export size")
            size_px = st.slider("Output size (px)", 128, 1024, 512, step=64, key="photo_export_size")
            preview = cropped.resize((size_px, size_px))
            st.image(preview, caption=f"{size_px}×{size_px}", use_container_width=True)

        # حفظ في الجلسة كـ bytes
        out_bytes = _to_png_bytes(cropped)
        st.session_state.photo_bytes = out_bytes
        st.session_state.photo_mime = "image/png"
        st.success("✅ Photo ready. It will be embedded in avatar_circle automatically.")
    else:
        st.info("Upload a square-ish image for best result. We’ll auto square-crop it 😉")

    return profile
