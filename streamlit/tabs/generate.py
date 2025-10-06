# streamlit/tabs/generate.py
from __future__ import annotations
import re
import streamlit as st

from api_client import generate_pdf
from .tab_theme_editor import theme_selector

_SEPS = re.compile(r"[;\n\r•\-–—]+")
def _as_list(v):
    if not v: return []
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in _SEPS.split(str(v)) if x.strip()]

def _fallback_profile_from_session() -> dict:
    """لو profile_data غير موجودة، ابنها من الحقول النصية في الجلسة حتى لا يخرج PDF فارغ."""
    simple = {
        "name": st.session_state.get("name"),
        "title": st.session_state.get("title"),
        "email": st.session_state.get("email"),
        "phone": st.session_state.get("phone"),
        "location": st.session_state.get("location"),
        "github": st.session_state.get("github"),
        "linkedin": st.session_state.get("linkedin"),
        "summary_text": st.session_state.get("sections_right_text") or st.session_state.get("summary_text"),
        "skills_text": st.session_state.get("skills_text"),
        "languages_text": st.session_state.get("languages_text"),
        "projects_text": st.session_state.get("projects_text"),
        "education_text": st.session_state.get("education_text"),
    }
    # تحویل مبسط للبنية القياسية
    projects = [[ln, "", ""] for ln in _as_list(simple["projects_text"])]
    social = []
    if simple.get("github"):   social.append(["GitHub",   str(simple["github"])])
    if simple.get("linkedin"): social.append(["LinkedIn", str(simple["linkedin"])])
    profile = {
        "header":   {"name": simple.get("name") or "", "title": simple.get("title") or "Backend Developer"},
        "contact":  {"email": simple.get("email") or "", "phone": simple.get("phone") or "", "location": simple.get("location") or ""},
        "summary":  _as_list(simple.get("summary_text")),
        "skills":   _as_list(simple.get("skills_text")),
        "languages":_as_list(simple.get("languages_text")),
        "projects": projects or [["Project", "Description", ""]],
        "education":_as_list(simple.get("education_text")),
        "social_links": social,
    }
    return profile

def render_generate_actions(outputs_dir):
    """
    تبويب التوليد والتحمـيل (Generate / Download)
    يوفّر اختيار الثيم والتخطيط واللغة، ثم يرسل البيانات إلى FastAPI لتوليد PDF.
    """
    st.subheader("📄 Generate Resume PDF")

    # احصل على بيانات البروفايل من session_state
    profile = st.session_state.get("profile_data") or {}
    if not profile:
        # Fallback ذكي بدل PDF فارغ
        profile = _fallback_profile_from_session()

    # اختيار الثيم والتخطيط
    theme_name, layout_name = theme_selector()
    ui_lang = st.selectbox("🌐 UI Language", ["ar", "en", "de"], index=0)
    rtl_mode = (ui_lang == "ar") or st.checkbox("↔️ Force RTL", value=True)

    if not any(profile.values()):
        st.info("No profile data found yet — you can still generate a blank PDF.", icon="ℹ️")

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🚀 Generate PDF", type="primary", width='stretch'):
            try:
                pdf_bytes = generate_pdf(
                    profile,
                    theme_name=theme_name,
                    layout_name=layout_name,
                    ui_lang=ui_lang,
                    rtl_mode=rtl_mode,
                )
                st.success("✅ PDF generated successfully!")
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"resume-{theme_name}.pdf",
                    mime="application/pdf",
                    width='stretch',
                )
            except Exception as e:
                st.error(f"❌ Failed to generate PDF: {e}")

    with col2:
        st.caption("💡 Tip: Theme and layout can be changed instantly — no need to restart the server.")

    st.divider()
    st.caption("Generated files are also stored in the 'outputs/' directory inside your project.")
