from fastapi import APIRouter, HTTPException

from core.connector import get_device
from core.monitor import collect_metrics

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


@router.get("/{device_name}")
def metrics(device_name: str):
    if not get_device(device_name):
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thiết bị",
        )

    try:
        return collect_metrics(device_name)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
