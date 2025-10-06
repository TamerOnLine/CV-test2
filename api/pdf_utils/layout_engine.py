# api/pdf_utils/layout_engine.py
from __future__ import annotations
import json, sys
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas

from .layout import render_with_layout
from .data_utils import build_ready_from_profile

def main():
    if len(sys.argv) != 4:
        print("Usage: python -m api.pdf_utils.layout_engine <profile.json> <layout.json> <output.pdf>")
        sys.exit(2)

    profile_path = Path(sys.argv[1])
    layout_path  = Path(sys.argv[2])
    output_path  = Path(sys.argv[3])

    # 1) تحقق من الملفات
    if not profile_path.is_file():
        print(f"[ERR] profile not found: {profile_path}")
        sys.exit(1)
    if not layout_path.is_file():
        print(f"[ERR] layout not found:  {layout_path}")
        sys.exit(1)

    # 2) أنشئ مجلد الإخراج إن لزم
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Loading profile: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    print(f"[INFO] Loading layout : {layout_path}")
    layout  = json.loads(layout_path.read_text(encoding="utf-8"))

    # 3) بناء خريطة البيانات
    data_map = build_ready_from_profile(profile)

    # 4) رسم PDF
    print(f"[INFO] Writing PDF   : {output_path}")
    c = Canvas(str(output_path))
    ui_lang = profile.get("ui_lang", "en")
    render_with_layout(c, layout, data_map, ui_lang=ui_lang)
    c.showPage()
    c.save()

    # 5) تأكيد
    size = output_path.stat().st_size if output_path.exists() else 0
    print(f"✅ PDF generated: {output_path} ({size} bytes)")

if __name__ == "__main__":
    main()
