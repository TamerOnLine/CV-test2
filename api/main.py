"""FastAPI application for generating resume PDFs.

Exposes:
- /healthz                          : health check
- /generate-form-simple (POST)      : build PDF from profile + (optional) layout/theme
- /api/profiles/*                   : save/load JSON profiles (via profiles router)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

# 1) سجّل الخطوط قبل استيراد الـ builder
from api.pdf_utils import fonts  # noqa: F401  (side-effect: register fonts)
fonts.register_all_fonts()  # يضمن تحميل كل الخطوط الموجودة في assets/

# 2) الآن استورد الـ builder والـ mapper بعد التسجيل
from api.pdf_utils.builder import build_resume_pdf
from api.pdf_utils.mapper import profile_to_overrides

# 3) راوتر الحفظ/التحميل للملفات الشخصية (profiles)
from api.routes import profiles as profiles_routes  # يحتوي /api/profiles/*

APP_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = APP_ROOT / "themes"
LAYOUTS_DIR = APP_ROOT / "layouts"

app = FastAPI(title="Resume API")

# ─────────────────────────────────────────────
# 🧩 إعداد CORS الآمن
# ─────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "http://localhost:8501",      # Streamlit (تطوير محلي)
    "http://127.0.0.1:8501",
    # "https://your-domain.example",  # أضف هنا دومين الإنتاج لاحقًا
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
# ─────────────────────────────────────────────

# تسجيل راوتر إدارة البروفايلات
app.include_router(profiles_routes.router, prefix="/api")


def normalize_theme_name(tn: Optional[str]) -> str:
    """Normalize an incoming theme name (drop '.theme.json' if present)."""
    if not tn:
        return "default"
    return tn[:-11] if tn.endswith(".theme.json") else tn


def coerce_summary(profile: Dict[str, Any]) -> None:
    """If summary is a stringified list, convert it to a single joined string."""
    val = profile.get("summary")
    if isinstance(val, str) and val.strip().startswith("[") and val.strip().endswith("]"):
        try:
            import ast

            lst = ast.literal_eval(val)
            if isinstance(lst, list):
                profile["summary"] = " ".join(str(x) for x in lst if x)
        except Exception:
            # best-effort; ignore parsing errors
            pass


@app.get("/healthz")
def healthz() -> Dict[str, bool]:
    return {"ok": True}


@app.post("/generate-form-simple")
def generate_form_simple(payload: Dict[str, Any]) -> Response:
    """Generate a resume PDF from the provided payload."""

    # -------- إعداد البيانات الأساسية --------
    data: Dict[str, Any] = {
        "theme_name": normalize_theme_name(payload.get("theme_name") or payload.get("theme")),
        "ui_lang": payload.get("ui_lang") or "en",
        "rtl_mode": bool(payload.get("rtl_mode")),
        "profile": payload.get("profile") or {},
    }

    # -------- قراءة layout --------
    layout_inline = payload.get("layout_inline")
    if not layout_inline:
        layout_name = payload.get("layout_name")
        if isinstance(layout_name, str) and layout_name.strip():
            path = LAYOUTS_DIR / layout_name
            try:
                layout_inline = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"[WARN] Could not read layout '{path}': {exc}")

    # -------- أدوات مساعدة داخلية --------
    import base64

    def _decode_headshots(node):
        """فكّ ترميز photo_b64 -> photo_bytes داخل avatar_circle."""
        if isinstance(node, dict):
            if node.get("block_id") == "avatar_circle":
                d = node.setdefault("data", {})
                b64 = d.get("photo_b64")
                if b64 and not d.get("photo_bytes"):
                    try:
                        d["photo_bytes"] = base64.b64decode(b64.encode("ascii"))
                    except Exception:
                        d["photo_bytes"] = None
            for v in node.values():
                _decode_headshots(v)
        elif isinstance(node, list):
            for it in node:
                _decode_headshots(it)

    def _deep_merge(dst: dict, src: dict) -> dict:
        """دمج بسيط: لا يكتب فوق قيم موجودة؛ يملأ الناقصة فقط."""
        for k, v in (src or {}).items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                _deep_merge(dst[k], v)
            else:
                if k not in dst:
                    dst[k] = v
        return dst

    # -------- ضمان وجود هيكل للّايـاوت --------
    if not layout_inline:
        layout_inline = {"flow": []}

    # -------- اشتقاق overrides تلقائيًا من الـprofile --------
    # ينتج بيانات متوافقة تمامًا مع كل block:
    # - contact_info.items
    # - key_skills.skills
    # - languages.languages
    # - projects.items
    # - text_section:summary -> {"section":"summary","text":...}
    # - avatar_circle.photo_b64 (إن وُجد avatar_b64 في الـprofile)
    # - education.items كمقاطع نصية متعددة الأسطر
    ov_from_profile = profile_to_overrides(data.get("profile") or {})
    layout_inline.setdefault("overrides", {})
    layout_inline["overrides"] = _deep_merge(layout_inline["overrides"], ov_from_profile)

    # فكّ ترميز الصور داخل البلوكات (يحوّل photo_b64 إلى photo_bytes)
    _decode_headshots(layout_inline)

    # -------- تصحيح summary إن كانت قائمة ممثلة كسلسلة --------
    if isinstance(data["profile"], dict):
        coerce_summary(data["profile"])

    # تمرير layout المحدث إلى دالة البناء
    data["layout_inline"] = layout_inline

    # -------- لوج تشخيصي --------
    flow = (layout_inline or {}).get("flow", [])
    blocks_count = sum(len(x.get("blocks", [])) for x in flow) if isinstance(flow, list) else 0
    print(f"[REQ] theme='{data['theme_name']}', blocks={blocks_count}")

    # -------- البناء والإرجاع --------
    pdf_bytes = build_resume_pdf(data=data)
    return Response(content=pdf_bytes, media_type="application/pdf")
