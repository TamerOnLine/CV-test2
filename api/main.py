"""FastAPI application for generating resume PDFs.

This module exposes endpoints for health checking and PDF generation
based on provided profile data and optional layout/theme parameters.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Response

# 1) سجّل الخطوط أولاً قبل أي استيراد للـ builder
from api.pdf_utils import fonts  # noqa: F401  (side-effect: register fonts)
fonts.register_all_fonts()  # يضمن تحميل كل الخطوط الموجودة في assets/

# 2) الآن استورد الـ builder بعد التسجيل
from api.pdf_utils.builder import build_resume_pdf

APP_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = APP_ROOT / "themes"
LAYOUTS_DIR = APP_ROOT / "layouts"

app = FastAPI(title="Resume API")


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
    data: Dict[str, Any] = {
        "theme_name": normalize_theme_name(
            payload.get("theme_name") or payload.get("theme")
        ),
        "ui_lang": payload.get("ui_lang") or "en",
        "rtl_mode": bool(payload.get("rtl_mode")),
        "profile": payload.get("profile") or {},
    }

    # inline layout or from file
    layout_inline = payload.get("layout_inline")
    if not layout_inline:
        layout_name = payload.get("layout_name")
        if isinstance(layout_name, str) and layout_name.strip():
            path = LAYOUTS_DIR / layout_name
            try:
                layout_inline = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] Could not read layout '{path}': {exc}")

    if layout_inline:
        data["layout_inline"] = layout_inline

    if isinstance(data["profile"], dict):
        coerce_summary(data["profile"])

    flow = (layout_inline or {}).get("flow", [])
    blocks_count = (
        sum(len(x.get("blocks", [])) for x in flow) if isinstance(flow, list) else 0
    )
    print(f"[REQ] theme='{data['theme_name']}', blocks={blocks_count}")

    pdf_bytes = build_resume_pdf(data=data)
    return Response(content=pdf_bytes, media_type="application/pdf")
