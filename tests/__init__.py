# tests/conftest.py
import sys, pathlib
# أضف جذر المشروع (حيث يوجد مجلد api/) إلى مسار الاستيراد
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
