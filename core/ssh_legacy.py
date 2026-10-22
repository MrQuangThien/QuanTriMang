"""Fallback SSH connector for old Cisco IOS lab images.

This is used only when devices.yaml has legacy_ssh: true.
Ubuntu/Linux requires sshpass:
    sudo apt install sshpass

Windows requires an OpenSSH client and sshpass-like tooling is not
normally available. For the current lab, run the FastAPI service on
Ubuntu when the Cisco image is reachable only from Ubuntu.
"""

import os
import subprocess


class LegacySSHError(RuntimeError):
    pass


def _ssh_base(host: str, port: int, username: str) -> list[str]:
    return [
        "sshpass", "-e", "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "KexAlgorithms=+diffie-hellman-group1-sha1",
        "-o", "Ciphers=+aes128-cbc",
        "-o", "HostKeyAlgorithms=+ssh-rsa",
        "-o", "PubkeyAcceptedAlgorithms=+ssh-rsa",
        "-o", "ConnectTimeout=10",
        "-p", str(port),
        f"{username}@{host}",
    ]


def _run(args: list[str], password: str, input_text: str | None = None,
         timeout: int = 45) -> str:
    env = os.environ.copy()
    env["SSHPASS"] = password

    try:
        result = subprocess.run(
            args,
            env=env,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise LegacySSHError(
            "Không tìm thấy sshpass. Trên Ubuntu chạy: "
            "sudo apt update && sudo apt install -y sshpass"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise LegacySSHError("SSH legacy timeout.") from exc

    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        raise LegacySSHError(message or "SSH legacy command failed.")
    return result.stdout


def legacy_command(host: str, port: int, username: str,
                   password: str, command: str) -> str:
    return _run(
        _ssh_base(host, port, username) + [command],
        password,
        timeout=45,
    )


def legacy_restore(host: str, port: int, username: str,
                   password: str, config_text: str) -> str:
    commands = (
        "configure terminal\n"
        + config_text.strip()
        + "\nend\n"
        "write memory\n"
    )
    return _run(
        _ssh_base(host, port, username),
        password,
        input_text=commands,
        timeout=60,
    )
