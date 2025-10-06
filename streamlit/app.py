from __future__ import annotations
import json
import base64
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st
import requests
import pandas as pd

# -----------------------------
# Paths (relative to this file)
# -----------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
THEMES_DIR = ROOT / "themes"
LAYOUTS_DIR = ROOT / "layouts"
PROFILES_DIR = ROOT / "profiles"
OUTPUTS_DIR = ROOT / "outputs"

for d in [THEMES_DIR, LAYOUTS_DIR, PROFILES_DIR, OUTPUTS_DIR]:
    d.mkdir(exist_ok=True)

# -----------------------------
# Schema & Helpers
# -----------------------------
DEFAULT_PROFILE: Dict[str, Any] = {
    "header": {"name": "", "title": ""},
    "contact": {"email": "", "phone": "", "website": "", "github": "", "linkedin": ""},
    "skills": [],
    "languages": [],
    "projects": [],
    "education": [],
    "summary": "",
}

def ensure_profile_schema(p: dict | None) -> dict:
    """يضمن وجود كل المفاتيح والبُنى المطلوبة داخل profile حتى لا تقع KeyError."""
    base = json.loads(json.dumps(DEFAULT_PROFILE))  # deep copy بسيط
    if not isinstance(p, dict):
        return base

    # دعم JSON القادم بصيغة {"profile": {...}}
    if "profile" in p and isinstance(p["profile"], dict):
        p = p["profile"]

    # dict fields
    for k in ("header", "contact"):
        src = p.get(k) or {}
        if isinstance(src, dict):
            base[k].update(src)

    # list/scalar fields
    if isinstance(p.get("skills"), list): base["skills"] = p["skills"]
    if isinstance(p.get("languages"), list): base["languages"] = p["languages"]
    if isinstance(p.get("education"), list): base["education"] = p["education"]
    if "summary" in p and isinstance(p.get("summary"), (str, list, dict)):
        base["summary"] = p["summary"]

    # projects: قائمة من [title, desc, url] أو dicts
    prj = p.get("projects")
    if isinstance(prj, list):
        norm = []
        for row in prj:
            if isinstance(row, (list, tuple)):
                title = (str(row[0]) if len(row) > 0 and row[0] is not None else "").strip()
                desc  = (str(row[1]) if len(row) > 1 and row[1] is not None else "").strip()
                url   = (str(row[2]) if len(row) > 2 and row[2] is not None else "").strip()
            elif isinstance(row, dict):
                title = str(row.get("title", "")).strip()
                desc  = str(row.get("description", "")).strip()
                url   = str(row.get("url", "")).strip()
            else:
                title = str(row).strip()
                desc = url = ""
            if title or desc or url:
                norm.append([title, desc, url])
        base["projects"] = norm

    return base

def read_json_file(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def list_json_names(folder: Path) -> List[str]:
    if not folder.exists():
        return []
    return [p.name for p in sorted(folder.glob("*.json"))]

def to_lines(text: str) -> List[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]

def projects_df_to_list(df) -> List[List[str]]:
    rows = []
    for _, row in df.iterrows():
        title = str(row.get("Title", "") or "").strip()
        desc  = str(row.get("Description", "") or "").strip()
        url   = str(row.get("URL", "") or "").strip()
        if title or desc or url:
            rows.append([title, desc, url])
    return rows

# ✅ إصلاح اسم الثيم + اختيار layout افتراضي
def normalize_theme_name(name: str) -> str:
    """يزيل الامتداد المكرر (.theme.json) لأن الـ backend يضيفه تلقائياً."""
    return name[:-11] if name.endswith(".theme.json") else name

def choose_layout_inline(selected_name: str | None):
    """يرجع layout جاهز للـAPI أو يختار أول ملف layout موجود تلقائياً."""
    if selected_name and selected_name != "(none)":
        return read_json_file(LAYOUTS_DIR / selected_name)
    files = sorted(LAYOUTS_DIR.glob("*.json"))
    for p in files:
        if "layout" in p.name.lower():
            st.info(f"Using fallback layout: {p.name}")
            return read_json_file(p)
    return None

def build_payload(
    theme_name: str,
    ui_lang: str,
    rtl_mode: bool,
    profile: Dict[str, Any],
    layout_inline: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    data = {
        "theme_name": theme_name,
        "ui_lang": ui_lang,
        "rtl_mode": rtl_mode,
        "profile": profile,
    }
    if layout_inline:
        data["layout_inline"] = layout_inline
    return data

def api_generate_pdf(base_url: str, payload: Dict[str, Any]) -> bytes:
    # يستخدم المسار المتاح فعليًا في الـ backend لديك حالياً
    url = f"{base_url.rstrip('/')}/generate-form-simple"
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    return r.content

def save_profile(path: Path, profile: Dict[str, Any]) -> None:
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

def load_profile(path: Path) -> Dict[str, Any]:
    return read_json_file(path)

def download_button_for_pdf(pdf_bytes: bytes, filename: str = "resume.pdf"):
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    st.download_button(
        "⬇️ Download PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        width="stretch",
    )
    with st.expander("Preview (experimental)"):
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" style="width:100%;height:80vh;border:none;"></iframe>',
            unsafe_allow_html=True,
        )

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Resume Builder", page_icon="📄", layout="wide")

st.title("📄 Resume Builder — Streamlit v7.4")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Controls")

    base_url = st.text_input("API Base URL", value="http://127.0.0.1:8000")
    ui_lang = st.selectbox("UI Language", ["en", "de", "ar"], index=0)
    rtl_mode = st.toggle("RTL mode", value=(ui_lang == "ar"))

    theme_files = list_json_names(THEMES_DIR)
    theme_name = st.selectbox("Theme", theme_files or ["default.theme.json"])

    layout_files = list_json_names(LAYOUTS_DIR)
    layout_default_index = 1 if layout_files else 0
    layout_file = st.selectbox("Layout", ["(none)"] + layout_files, index=layout_default_index)

    st.markdown("---")
    st.subheader("💾 Profiles")

    existing_profiles = list_json_names(PROFILES_DIR)
    col_p_load, col_p_save = st.columns(2)

    with col_p_load:
        selected_profile = st.selectbox(
            "Select profile",
            ["(none)"] + existing_profiles,
            index=0,
        )
        load_clicked = st.button("📂 Load Profile", width="stretch")
    with col_p_save:
        profile_name = st.text_input("Save as", value="my_profile.json")
        save_clicked = st.button("💾 Save Profile", width="stretch")

    st.markdown("---")
    up = st.file_uploader("Import profile (.json)", type=["json"])
    export_clicked = st.button("⬇️ Export current as JSON", width="stretch")

# --- Session State (safe init) ---
if "profile" not in st.session_state:
    st.session_state.profile = ensure_profile_schema({})

# --- Profile Load / Save / Import / Export ---
if load_clicked and selected_profile and selected_profile != "(none)":
    loaded = load_profile(PROFILES_DIR / selected_profile)
    st.session_state.profile = ensure_profile_schema(loaded)
    st.success(f"Loaded profile: {selected_profile}")

if save_clicked:
    filename = profile_name.strip()
    if not filename.endswith(".json"):
        filename += ".json"
    try:
        save_profile(PROFILES_DIR / filename, ensure_profile_schema(st.session_state.profile))
        st.success(f"Saved: {filename}")
    except Exception as e:
        st.error(f"Save failed: {e}")

if up is not None:
    try:
        imported = json.loads(up.getvalue().decode("utf-8"))
        st.session_state.profile = ensure_profile_schema(imported)
        st.success("Imported profile applied to the form.")
    except Exception as e:
        st.error(f"Import failed: {e}")

if export_clicked:
    st.download_button(
        "Download JSON",
        data=json.dumps(ensure_profile_schema(st.session_state.profile), ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="profile_export.json",
        mime="application/json",
        width="stretch",
    )

# --- Tabs for Form Sections ---
tab_basic, tab_contact, tab_skills, tab_langs, tab_projects, tab_edu, tab_summary = st.tabs(
    ["Basic Info", "Contact", "Skills", "Languages", "Projects", "Education", "Summary"]
)

with tab_basic:
    st.subheader("Basic Info")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.profile["header"]["name"] = st.text_input(
            "Full Name", st.session_state.profile["header"].get("name", "")
        )
    with c2:
        st.session_state.profile["header"]["title"] = st.text_input(
            "Title", st.session_state.profile["header"].get("title", "")
        )

with tab_contact:
    st.subheader("Contact Info")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.profile["contact"]["email"] = st.text_input(
            "Email", st.session_state.profile["contact"].get("email", "")
        )
        st.session_state.profile["contact"]["website"] = st.text_input(
            "Website", st.session_state.profile["contact"].get("website", "")
        )
    with c2:
        st.session_state.profile["contact"]["phone"] = st.text_input(
            "Phone", st.session_state.profile["contact"].get("phone", "")
        )
        st.session_state.profile["contact"]["github"] = st.text_input(
            "GitHub", st.session_state.profile["contact"].get("github", "")
        )
        st.session_state.profile["contact"]["linkedin"] = st.text_input(
            "LinkedIn", st.session_state.profile["contact"].get("linkedin", "")
        )

with tab_skills:
    st.subheader("Skills")
    skills_text = st.text_area(
        "One per line", "\n".join(st.session_state.profile.get("skills") or []), height=180
    )
    st.session_state.profile["skills"] = to_lines(skills_text)

with tab_langs:
    st.subheader("Languages")
    langs_text = st.text_area(
        "One per line (e.g., Arabic — Native)",
        "\n".join(st.session_state.profile.get("languages") or []),
        height=150,
    )
    st.session_state.profile["languages"] = to_lines(langs_text)

with tab_projects:
    st.subheader("Projects")
    existing = st.session_state.profile.get("projects") or []
    df = pd.DataFrame(existing, columns=["Title", "Description", "URL"]) if existing else pd.DataFrame(
        [{"Title": "", "Description": "", "URL": ""}]
    )
    edited = st.data_editor(df, num_rows="dynamic", width="stretch")
    st.session_state.profile["projects"] = projects_df_to_list(edited)

with tab_edu:
    st.subheader("Education / Training")

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

    ed_rows = _ensure_education_rows(st.session_state.profile.get("education", []))
    df_edu = pd.DataFrame(ed_rows, columns=EDU_COLUMNS)

    st.caption("Use the table below to edit your education entries:")
    edited = st.data_editor(
        df_edu,
        num_rows="dynamic",
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

    # حفظ التعديلات بصيغة موحّدة
    st.session_state.profile["education"] = edited.fillna("").values.tolist()

    st.info("💡 Tip: Leave URL empty if not applicable.")


with tab_summary:
    st.subheader("Summary / About Me")
    st.session_state.profile["summary"] = st.text_area(
        "Short professional summary",
        st.session_state.profile.get("summary") or "",
        height=180,
    )

# --- PDF Generation ---
st.markdown("---")
col_gen, col_dbg = st.columns([2, 1])

with col_gen:
    st.subheader("Generate PDF")
    if st.button("🚀 Generate", type="primary", width="stretch"):
        try:
            layout_inline = choose_layout_inline(layout_file)

            payload = build_payload(
                theme_name=normalize_theme_name(theme_name),
                ui_lang=ui_lang,
                rtl_mode=bool(rtl_mode),
                profile=ensure_profile_schema(st.session_state.profile),
                layout_inline=layout_inline,
            )

            # Debug سريع قبل الإرسال
            st.write("[CLIENT] theme:", normalize_theme_name(theme_name), "layout:", layout_file)

            pdf_bytes = api_generate_pdf(base_url, payload)
            download_button_for_pdf(pdf_bytes, filename="resume.pdf")
            st.success("PDF generated successfully.")
        except requests.HTTPError as http_err:
            st.error(f"HTTP error: {http_err}")
        except Exception as e:
            st.exception(e)

with col_dbg:
    st.subheader("Debug")
    if st.checkbox("Show outgoing payload"):
        st.code(
            json.dumps(
                build_payload(
                    theme_name=normalize_theme_name(theme_name),
                    ui_lang=ui_lang,
                    rtl_mode=bool(rtl_mode),
                    profile=ensure_profile_schema(st.session_state.profile),
                    layout_inline=(
                        choose_layout_inline(layout_file)
                    ),
                ),
                ensure_ascii=False,
                indent=2,
            ),
            language="json",
        )
