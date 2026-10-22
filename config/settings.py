import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "Network AutoManager")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

GNS3_HOST = os.getenv("GNS3_HOST", "192.168.56.1")
GNS3_PORT = int(os.getenv("GNS3_PORT", "3080"))
GNS3_URL = os.getenv("GNS3_URL", f"http://{GNS3_HOST}:{GNS3_PORT}")

DEVICES_FILE = ROOT_DIR / "config" / "devices.yaml"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{ROOT_DIR / 'network.db'}",
)
DB_URL = DATABASE_URL

BACKUP_DIR = ROOT_DIR / os.getenv("BACKUP_DIR", "backups")
GIT_DIR = BACKUP_DIR
LOG_DIR = ROOT_DIR / os.getenv("LOG_DIR", "logs")

UBUNTU_HOST = os.getenv("UBUNTU_HOST", "192.168.56.102")
UBUNTU_USERNAME = os.getenv("UBUNTU_USERNAME", "vboxuser")
UBUNTU_AGENT_PORT = int(os.getenv("UBUNTU_AGENT_PORT", "9000"))
UBUNTU_AGENT_URL = os.getenv(
    "UBUNTU_AGENT_URL",
    f"http://{UBUNTU_HOST}:{UBUNTU_AGENT_PORT}",
)
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "network-lab-token")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
GIT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
