from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError

from config.settings import GIT_DIR


def get_repo() -> Repo:
    try:
        return Repo(GIT_DIR)
    except InvalidGitRepositoryError:
        return Repo.init(GIT_DIR)


def commit_backup(device: str, path: Path):
    repo = get_repo()
    relative_path = path.relative_to(GIT_DIR)
    repo.index.add([str(relative_path)])

    if repo.is_dirty(
        index=True,
        working_tree=False,
        untracked_files=True,
    ):
        repo.index.commit(
            f"Backup {device}: {path.stem}"
        )
