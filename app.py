# app.py (raíz del repo)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from liqscope.api.app import create_app  # noqa: E402

app = create_app()
