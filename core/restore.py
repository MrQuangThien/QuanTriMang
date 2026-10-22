from pathlib import Path

from config.settings import BACKUP_DIR
from core.connector import restore_config


def validate_backup_file(path: str) -> Path:
    file = Path(path).resolve()

    backup_root = BACKUP_DIR.resolve()
    try:
        file.relative_to(backup_root)
    except ValueError as exc:
        raise ValueError(
            "Chỉ được restore file nằm trong thư mục backups."
        ) from exc

    if not file.exists():
        raise FileNotFoundError(path)
    if file.suffix.lower() != ".cfg":
        raise ValueError("Chỉ cho phép file .cfg")
    if file.stat().st_size == 0:
        raise ValueError("File cấu hình rỗng")

    return file


def safe_restore(
    device: str,
    backup_file: str,
    confirm: bool = False,
) -> dict:
    if not confirm:
        raise ValueError(
            "Restore bị chặn. Phải gửi confirm=true."
        )

    file = validate_backup_file(backup_file)
    config_text = file.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    output = restore_config(
        device,
        config_text,
    )

    return {
        "device": device,
        "status": "success",
        "file": str(file),
        "output": output,
    }
