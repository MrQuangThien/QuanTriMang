import requests

from config.settings import AGENT_TOKEN, UBUNTU_AGENT_URL


def _headers() -> dict[str, str]:
    return {"X-Agent-Token": AGENT_TOKEN}


def command(device: str, command_text: str) -> str:
    url = f"{UBUNTU_AGENT_URL.rstrip('/')}/command"
    try:
        response = requests.post(
            url,
            json={"device": device, "command": command_text},
            headers=_headers(),
            timeout=60,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Không kết nối được Ubuntu Agent {UBUNTU_AGENT_URL}: {exc}"
        ) from exc

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"Ubuntu Agent lỗi HTTP {response.status_code}: {detail}")

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("detail", "Ubuntu Agent command failed"))
    return data.get("output", "")


def restore(device: str, config_text: str) -> str:
    url = f"{UBUNTU_AGENT_URL.rstrip('/')}/restore"
    try:
        response = requests.post(
            url,
            json={"device": device, "config": config_text},
            headers=_headers(),
            timeout=90,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Không kết nối được Ubuntu Agent {UBUNTU_AGENT_URL}: {exc}"
        ) from exc

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"Ubuntu Agent lỗi HTTP {response.status_code}: {detail}")

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("detail", "Ubuntu Agent restore failed"))
    return data.get("output", "")
