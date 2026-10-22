from fastapi import APIRouter, HTTPException

from core.connector import get_device
from core.restore import safe_restore

router = APIRouter(prefix="/api/restore", tags=["Restore"])


@router.post("")
def restore(
    device: str,
    backup_file: str,
    confirm: bool = False,
):
    if not get_device(device):
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thiết bị",
        )

    try:
        return safe_restore(
            device=device,
            backup_file=backup_file,
            confirm=confirm,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
