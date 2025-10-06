# api/pdf_utils/blocks/text_section.py
from __future__ import annotations
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm

from ..config import *
from ..text import draw_par
from ..icons import draw_heading_with_icon
from .base import Frame, RenderContext
from .registry import register


class TextSectionBlock:
    """
    بلوك عام لعرض أقسام نصية مثل (summary, about, objective, ...)

    - يدعم الصيغ التالية:
        "text_section:summary"
        "text_section:about"
        "text_section:objective"
    - يقرأ محتواه من:
        profile["summary"] أو profile["about"] أو data["text"]
    """

    BLOCK_ID = "text_section"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        section = (data.get("section") or data.get("key") or "summary").strip()

        # 🏷️ تحديد العنوان الافتراضي حسب نوع القسم
        title_map = {
            "summary": "Professional Summary",
            "about": "About Me",
            "objective": "Career Objective",
        }
        title = data.get("title") or title_map.get(section, section.title())

        # 📄 تحديد محتوى النص (list أو str)
        lines = data.get(section) or data.get("lines") or data.get("text") or []
        if isinstance(lines, str):
            lines = [lines]
        if not lines:
            return frame.y

        # 🎨 رسم العنوان مع خط تحت العنوان (نفس نظام Projects)
        y = draw_heading_with_icon(
            c=c,
            x=frame.x,
            y=frame.y,
            title=title,
            icon=None,
            font="Helvetica-Bold",
            size=RIGHT_SEC_HEADING_SIZE,
            color=HEADING_COLOR,
            underline_w=frame.w,
            rule_color=RIGHT_SEC_RULE_COLOR,
            rule_width=RIGHT_SEC_RULE_WIDTH,
            gap_below=GAP_AFTER_HEADING / 2,
        )
        y -= RIGHT_SEC_RULE_TO_TEXT_GAP

        # ✍️ رسم النصوص فقرة فقرة
        c.setFont("Helvetica", RIGHT_SEC_TEXT_SIZE)
        c.setFillColor(colors.black)
        y = draw_par(
            c,
            frame.x,
            y,
            lines,
            "Helvetica",
            RIGHT_SEC_TEXT_SIZE,
            frame.w,
            "left",
            False,
            BODY_LEADING,
            RIGHT_SEC_PARA_GAP,
        )

        y -= RIGHT_SEC_SECTION_GAP
        return y


# ✅ التسجيل اليدوي (نفس أسلوب ProjectsBlock و SkillsGridBlock)
register(TextSectionBlock())
