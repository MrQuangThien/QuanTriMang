from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_URL
from storage.models import Base, BackupRecord


if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def init_db():
    Base.metadata.create_all(engine)
    print("[DATABASE] Database initialized")


def save_backup(device: str, path: str, status: str,
                changed: str = "UNKNOWN"):
    with SessionLocal() as session:
        record = BackupRecord(
            device=device,
            path=path,
            status=status,
            changed=changed,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def add_backup(device: str, path: str, status: str):
    return save_backup(device, path, status)


def list_backups(limit: int = 100) -> list[dict]:
    with SessionLocal() as session:
        rows = session.scalars(
            select(BackupRecord)
            .order_by(BackupRecord.created_at.desc())
            .limit(limit)
        ).all()

        return [
            {
                "id": row.id,
                "device": row.device,
                "path": row.path,
                "status": row.status,
                "changed": row.changed,
                "created_at": row.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            for row in rows
        ]
