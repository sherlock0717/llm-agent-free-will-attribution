from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text missing in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    ROOT / "site" / "index.html",
    '<strong>1005</strong><span>自动化测试</span>',
    '<strong>1011</strong><span>自动化测试</span>',
)
replace_once(
    ROOT / "site" / "assets" / "figures" / "social-preview.svg",
    '>1005</text><text x="24" y="82"',
    '>1011</text><text x="24" y="82"',
)
replace_once(
    ROOT / "tests" / "site" / "test_portfolio_packaging.py",
    '"360", "96", "1005"',
    '"360", "96", "1011"',
)

Path(__file__).unlink()
workflow = ROOT / ".github" / "workflows" / "sync_portfolio_test_count_once.yml"
if workflow.exists():
    workflow.unlink()
