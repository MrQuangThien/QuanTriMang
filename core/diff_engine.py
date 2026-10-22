from difflib import unified_diff
from pathlib import Path


def compare_configs(old_file: str, new_file: str) -> str:
    old = Path(old_file).read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines(keepends=True)

    new = Path(new_file).read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines(keepends=True)

    return "".join(
        unified_diff(
            old,
            new,
            fromfile=old_file,
            tofile=new_file,
        )
    )


def backup_files(device: str, backup_root: Path) -> list[Path]:
    folder = backup_root / device
    if not folder.exists():
        return []
    return sorted(
        folder.glob("*.cfg"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def latest_two(device: str, backup_root: Path):
    files = backup_files(device, backup_root)
    return (files[0], files[1]) if len(files) >= 2 else (None, None)


def diff_latest(device: str, backup_root: Path) -> dict:
    newest, previous = latest_two(device, backup_root)

    if not newest:
        return {
            "device": device,
            "changed": False,
            "message": "Chưa có backup.",
            "diff": "",
        }

    if not previous:
        return {
            "device": device,
            "changed": False,
            "message": "Mới có 1 backup, chưa đủ dữ liệu để so sánh.",
            "latest": str(newest),
            "diff": "",
        }

    diff = compare_configs(str(previous), str(newest))
    return {
        "device": device,
        "changed": bool(diff),
        "previous": str(previous),
        "latest": str(newest),
        "diff": diff,
    }
