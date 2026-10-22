from fastapi import APIRouter, HTTPException

from core.connector import (
    get_device,
    get_interfaces,
    load_devices,
    run_command,
)

router = APIRouter(prefix="/api/devices", tags=["Devices"])


@router.get("")
def get_devices():
    return load_devices()


@router.get("/{name}")
def get_device_info(name: str):
    device = get_device(name)
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thiết bị",
        )
    return device


@router.get("/{name}/interfaces")
def interfaces(name: str):
    try:
        return {
            "device": name,
            "output": get_interfaces(name),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/{name}/command")
def command(name: str, command: str):
    try:
        return {
            "device": name,
            "command": command,
            "output": run_command(name, command),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
