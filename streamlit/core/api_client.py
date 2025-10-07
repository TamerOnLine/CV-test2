from __future__ import annotations
import json
import requests
from typing import Any, Dict, Optional
from pathlib import Path

from .paths import LAYOUTS_DIR
import base64

def normalize_theme_name(name: str) -> str:
    """Drop trailing '.theme.json' if present; API expects bare theme name."""
    return name[:-11] if name.endswith(".theme.json") else name

def choose_layout_inline(selected_name: Optional[str]):
    """Return inline layout JSON if selected; otherwise pick a fallback file with 'layout' in name."""
    if selected_name and selected_name != "(none)":
        p = Path(LAYOUTS_DIR) / selected_name
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    files = sorted(LAYOUTS_DIR.glob("*.json"))
    for p in files:
        if "layout" in p.name.lower():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
    return None

def build_payload(
    theme_name: str,
    ui_lang: str,
    rtl_mode: bool,
    profile: Dict[str, Any],
    layout_inline: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "theme_name": theme_name,
        "ui_lang": ui_lang,
        "rtl_mode": rtl_mode,
        "profile": profile,
    }
    if layout_inline:
        data["layout_inline"] = layout_inline
    return data

def api_generate_pdf(base_url: str, payload: Dict[str, Any]) -> bytes:
    url = f"{base_url.rstrip('/')}/generate-form-simple"
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    return r.content


def inject_headshot_into_layout(layout_inline: Optional[Dict[str, Any]], photo_bytes: Optional[bytes]) -> Optional[Dict[str, Any]]:
    """
    If a headshot is present, inject it into every 'avatar_circle' block's data.
    """
    if not layout_inline or not photo_bytes:
        return layout_inline

    # لتقليل حجم JSON: سنرسلها base64 ونفكّها في السيرفر؟ لا حاجة — البلوك يتوقع bytes.
    # FastAPI سيحوّلها JSON، لذا الأفضل إبقاؤها bytes داخل payload؟ لا يتم ترميز bytes مباشرة في JSON.
    # الحل: نرسلها base64 ثم نعيد فكّها داخل البلوك عند البناء (البلوك عندك يقرأ photo_bytes: bytes).
    # هنا سنستخدم مفتاح photo_b64 ويقوم محرّك الـPDF بدعمها عبر data_mapper إن متاح.
    # أو الأسلم: نترجمها لبايتات على السيرفر؟ بما أن السيرفر لا يفك base64 تلقائياً،
    # سنحقن photo_b64 الآن، وعلى جهة السيرفر إن لم يكن لديك mapper، عدّل block ليقبل photo_b64.
    # لكن لأن block الحالي يتوقع photo_bytes، سنجعل المفتاحين معاً لضمان التوافق.
    photo_b64 = base64.b64encode(photo_bytes).decode("ascii")

    def _walk_and_inject(node: Any):
        if isinstance(node, dict):
            if node.get("block_id") == "avatar_circle":
                node.setdefault("data", {})
                node["data"]["photo_b64"] = photo_b64
                # احتياطي: قد يقرأ بناءك photo_bytes مباشرة لو فُكّت في السيرفر
                node["data"]["photo_bytes"] = None
            for v in node.values():
                _walk_and_inject(v)
        elif isinstance(node, list):
            for it in node:
                _walk_and_inject(it)

    cloned = json.loads(json.dumps(layout_inline))  # clone
    _walk_and_inject(cloned)
    return cloned
