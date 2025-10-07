from __future__ import annotations
import base64
import streamlit as st

def show_pdf_download(pdf_bytes: bytes, filename: str = "resume.pdf"):
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    st.download_button(
        "⬇️ Download PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        key="btn_download_pdf",
    )
    with st.expander("Preview (experimental)"):
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" style="width:100%;height:80vh;border:none;"></iframe>',
            unsafe_allow_html=True,
        )
