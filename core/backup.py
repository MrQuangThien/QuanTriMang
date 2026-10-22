from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from config.settings import BACKUP_DIR
from core.connector import get_running_config
from core.diff_engine import latest_two, compare_configs
from storage.db import save_backup
from storage.git_repo import commit_backup


def backup_one(device: dict) -> dict:
    name = device["name"]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = BACKUP_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    output_file = folder / f"{timestamp}.cfg"

    try:
        config = get_running_config(name)
        output_file.write_text(config, encoding="utf-8")

        _, previous = latest_two(name, BACKUP_DIR)
        changed = False
        diff = ""

        if previous:
            diff = compare_configs(
                str(previous),
                str(output_file),
            )
            changed = bool(diff)

        save_backup(
            name,
            str(output_file),
            "SUCCESS",
            "YES" if changed else "NO",
        )

        try:
            commit_backup(name, output_file)
        except Exception as exc:
            print(f"[WARNING] Git: {exc}")

        return {
            "device": name,
            "status": "success",
            "file": str(output_file),
            "changed": changed,
            "diff": diff,
        }

    except Exception as exc:
        try:
            save_backup(name, "", "FAILED", "UNKNOWN")
        except Exception:
            pass

        return {
            "device": name,
            "status": "error",
            "error": str(exc),
        }


def backup_all(devices: list[dict], workers: int = 4) -> list[dict]:
    enabled = [
        d for d in devices if d.get("enabled", True)
    ]
    if not enabled:
        return []

    results = []
    with ThreadPoolExecutor(
        max_workers=min(workers, len(enabled))
    ) as pool:
        futures = [
            pool.submit(backup_one, device)
            for device in enabled
        ]
        for future in as_completed(futures):
            results.append(future.result())

    return results
