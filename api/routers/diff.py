from fastapi import APIRouter, HTTPException

from config.settings import BACKUP_DIR
from core.connector import get_device
from core.diff_engine import diff_latest

router = APIRouter(prefix="/api/diff", tags=["Diff"])


@router.get("/{device}")
def diff(device: str):
    if not get_device(device):
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thiết bị",
        )
    try:
        return diff_latest(device, BACKUP_DIR)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
