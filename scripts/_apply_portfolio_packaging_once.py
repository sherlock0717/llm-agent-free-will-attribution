from __future__ import annotations

import base64
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / ".tmp_portfolio_packaging"
payload = "".join((CHUNKS / f"chunk{i:02d}").read_text(encoding="utf-8") for i in range(3))
source = zlib.decompress(base64.b64decode(payload)).decode("utf-8")
exec(compile(source, __file__, "exec"), {"__file__": __file__, "__name__": "__main__"})
