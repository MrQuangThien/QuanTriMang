import os
from typing import Any

import yaml
from netmiko import ConnectHandler

from config.settings import DEVICES_FILE
from core.ssh_legacy import legacy_command, legacy_restore
from core.ubuntu_agent import command as ubuntu_command, restore as ubuntu_restore


def load_devices() -> list[dict[str, Any]]:
    if not DEVICES_FILE.exists():
        return []
    with DEVICES_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("devices", [])


def get_device(name: str) -> dict[str, Any] | None:
    return next((d for d in load_devices() if d.get("name") == name), None)


def get_credentials(device: dict[str, Any]) -> tuple[str, str]:
    username_env = device.get("username_env")
    password_env = device.get("password_env")

    username = os.getenv(username_env or "", "")
    password = os.getenv(password_env or "", "")

    if not username or not password:
        raise RuntimeError(
            f"Thiết bị {device.get('name')} chưa có credential. "
            f"Kiểm tra {username_env}/{password_env} trong .env."
        )
    return username, password


def build_connection_config(device: dict[str, Any]) -> dict[str, Any]:
    username, password = get_credentials(device)
    return {
        "device_type": device.get("device_type", "cisco_ios"),
        "host": device["host"],
        "port": int(device.get("port", 22)),
        "username": username,
        "password": password,
        "conn_timeout": 10,
        "banner_timeout": 15,
        "auth_timeout": 15,
        "fast_cli": False,
    }


def connect_device(name: str):
    device = get_device(name)
    if not device:
        raise ValueError(f"Không tìm thấy thiết bị: {name}")
    if not device.get("enabled", True):
        raise ValueError(f"Thiết bị đang disabled: {name}")
    if device.get("legacy_ssh", False):
        raise RuntimeError(
            "Thiết bị SSH legacy phải dùng run_command(), không dùng "
            "ConnectHandler trực tiếp."
        )
    return ConnectHandler(**build_connection_config(device))


def run_command(name: str, command: str) -> str:
    device = get_device(name)
    if not device:
        raise ValueError(f"Không tìm thấy thiết bị: {name}")
    if not device.get("enabled", True):
        raise ValueError(f"Thiết bị đang disabled: {name}")

    username, password = get_credentials(device)

    if device.get("legacy_ssh", False):
        # R1 is reachable from Ubuntu, not reliably from Windows.
        # Windows FastAPI delegates legacy SSH to the Ubuntu Agent.
        return ubuntu_command(name, command)

    connection = None
    try:
        connection = ConnectHandler(**build_connection_config(device))
        return connection.send_command(command)
    finally:
        if connection:
            connection.disconnect()


def get_running_config(name: str) -> str:
    return run_command(name, "show running-config")


def get_interfaces(name: str) -> str:
    return run_command(name, "show ip interface brief")


def restore_config(name: str, config_text: str) -> str:
    device = get_device(name)
    if not device:
        raise ValueError(f"Không tìm thấy thiết bị: {name}")
    if device.get("legacy_ssh", False):
        return ubuntu_restore(name, config_text)

    connection = None
    try:
        connection = ConnectHandler(**build_connection_config(device))
        commands = [x.strip() for x in config_text.splitlines() if x.strip()]
        return connection.send_config_set(commands)
    finally:
        if connection:
            connection.disconnect()
