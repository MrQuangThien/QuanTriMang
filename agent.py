import os
from typing import Any

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from config.settings import DEVICES_FILE, AGENT_TOKEN
from core.ssh_legacy import legacy_command, legacy_restore

load_dotenv()

app = FastAPI(title="Network AutoManager - Ubuntu Agent", version="1.0.0")


class CommandRequest(BaseModel):
    device: str
    command: str


class RestoreRequest(BaseModel):
    device: str
    config: str


def load_devices() -> list[dict[str, Any]]:
    with DEVICES_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("devices", [])


def get_device(name: str) -> dict[str, Any]:
    device = next((d for d in load_devices() if d.get("name") == name), None)
    if not device:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thiết bị: {name}")
    if not device.get("enabled", True):
        raise HTTPException(status_code=400, detail=f"Thiết bị disabled: {name}")
    return device


def check_token(token: str | None):
    if not token or token != AGENT_TOKEN:
        raise HTTPException(status_code=401, detail="Agent token không hợp lệ")


def credentials(device: dict[str, Any]) -> tuple[str, str]:
    username = os.getenv(device.get("username_env", ""), "")
    password = os.getenv(device.get("password_env", ""), "")
    if not username or not password:
        raise HTTPException(
            status_code=500,
            detail=f"Thiếu credential {device.get('username_env')}/{device.get('password_env')}",
        )
    return username, password


@app.get("/health")
def health():
    return {"status": "ok", "service": "Ubuntu Agent"}


@app.post("/command")
def command(req: CommandRequest, x_agent_token: str | None = Header(default=None)):
    check_token(x_agent_token)
    device = get_device(req.device)
    username, password = credentials(device)
    try:
        output = legacy_command(
            host=device["host"],
            port=int(device.get("port", 22)),
            username=username,
            password=password,
            command=req.command,
        )
        return {"ok": True, "device": req.device, "output": output}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/restore")
def restore(req: RestoreRequest, x_agent_token: str | None = Header(default=None)):
    check_token(x_agent_token)
    device = get_device(req.device)
    username, password = credentials(device)
    try:
        output = legacy_restore(
            host=device["host"],
            port=int(device.get("port", 22)),
            username=username,
            password=password,
            config_text=req.config,
        )
        return {"ok": True, "device": req.device, "output": output}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agent:app", host="0.0.0.0", port=9000, reload=False)
