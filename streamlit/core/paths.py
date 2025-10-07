from __future__ import annotations
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # streamlit/core -> streamlit
ROOT = HERE.parent                             # project root

THEMES_DIR = ROOT / "themes"
LAYOUTS_DIR = ROOT / "layouts"
PROFILES_DIR = ROOT / "profiles"
OUTPUTS_DIR = ROOT / "outputs"

for d in [THEMES_DIR, LAYOUTS_DIR, PROFILES_DIR, OUTPUTS_DIR]:
    d.mkdir(exist_ok=True)
