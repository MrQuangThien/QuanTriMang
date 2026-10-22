import re

from core.connector import run_command


def _number(pattern: str, text: str):
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def collect_metrics(device: str) -> dict:
    cpu_raw = run_command(
        device,
        "show processes cpu | include CPU utilization",
    )

    memory_raw = run_command(
        device,
        "show memory statistics",
    )

    return {
        "device": device,
        "cpu_percent": _number(
            r"five minutes:\s*(\d+)%",
            cpu_raw,
        ),
        "memory_used_bytes": _number(
            r"Processor\s+\S+\s+(\d+)\s+(\d+)",
            memory_raw,
        ),
        "raw": {
            "cpu": cpu_raw,
            "memory": memory_raw,
        },
    }