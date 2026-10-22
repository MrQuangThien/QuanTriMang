from fastapi import APIRouter, HTTPException

from config.settings import BACKUP_DIR
from core.backup import backup_all, backup_one
from core.connector import get_device, load_devices
from core.diff_engine import diff_latest
from storage.db import list_backups

router = APIRouter(prefix="/api/backup", tags=["Backup"])


@router.post("")
def create_backup(device: str | None = None):
    try:
        if device:
            selected = get_device(device)
            if not selected:
                raise HTTPException(
                    status_code=404,
                    detail=f"Không tìm thấy thiết bị: {device}",
                )
            return backup_one(selected)

        return backup_all(load_devices())

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("")
def get_backups(limit: int = 100):
    return list_backups(limit)


@router.get("/{device}/latest-diff")
def latest_diff(device: str):
    if not get_device(device):
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy thiết bị: {device}",
        )
    try:
        return diff_latest(device, BACKUP_DIR)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
