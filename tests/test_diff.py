from pathlib import Path

from core.diff_engine import compare_configs


def test_diff(tmp_path: Path):
    old = tmp_path / "old.cfg"
    new = tmp_path / "new.cfg"

    old.write_text(
        "hostname R1\ninterface FastEthernet0/0\n",
        encoding="utf-8",
    )

    new.write_text(
        "hostname R1\ninterface FastEthernet0/1\n",
        encoding="utf-8",
    )

    result = compare_configs(
        str(old),
        str(new),
    )

    assert "-interface FastEthernet0/0" in result
    assert "+interface FastEthernet0/1" in result
