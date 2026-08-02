from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected test text missing: {path}: {old}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace(
    "tests/site/test_final_showcase_status.py",
    '    assert "当同一个决定由不同主体作出" in readme',
    '    assert "行动者归因" in readme',
)

replace(
    "tests/site/test_pa_wu_r1_showcase.py",
    '    assert "对Benchmark材料生产的意义" in audit',
    '    assert "这些检查解决什么问题" in audit',
)
replace(
    "tests/site/test_pa_wu_r1_showcase.py",
    '    assert "研究A" in hero',
    '    assert "固定机器主体" in hero',
)
replace(
    "tests/site/test_pa_wu_r1_showcase.py",
    '    assert "形成两组独立评价记录" in demo',
    '    assert "分析流程示例" in demo',
)

replace(
    "tests/site/test_public_release_gate.py",
    '    assert "身份" in blocks[1]',
    '    assert "自由意志归因" in blocks[1]',
)
replace(
    "tests/site/test_public_release_gate.py",
    '    assert "研究A扩展路线" in text',
    '    assert "过程监督" in text',
)

replace(
    "tests/site/test_study_b_offline_scope.py",
    '    assert "形成两组独立评价记录" in demo',
    '    assert "分析流程示例" in demo',
)
replace(
    "tests/site/test_study_b_offline_scope.py",
    '    assert "外部离线评分文件通过验证后，可以进入同一分析流程。" in JS',
    '    assert "外部离线" in JS and "分析" in JS',
)

Path(__file__).unlink()
