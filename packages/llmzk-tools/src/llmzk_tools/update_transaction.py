"""Filesystem transaction support for llmzk system-layer updates."""
from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Iterable


class UpdateRollbackError(RuntimeError):
    """Raised when an update fails and its backup cannot be fully restored."""

    def __init__(self, message: str, backup_path: Path) -> None:
        super().__init__(f"{message}. Backup retained at: {backup_path}")
        self.backup_path = backup_path


@dataclass(frozen=True)
class Snapshot:
    relative_path: Path
    existed: bool


def _exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _remove(path: Path) -> None:
    if not _exists(path):
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _link_or_copy(source: str, destination: str) -> str:
    """Create a cheap snapshot using hard links, falling back to copying."""
    try:
        os.link(source, destination)
        return destination
    except OSError:
        return shutil.copy2(source, destination)


def _copy_path(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        destination.symlink_to(os.readlink(source), target_is_directory=source.resolve().is_dir())
    elif source.is_dir():
        shutil.copytree(
            source,
            destination,
            symlinks=True,
            copy_function=_link_or_copy,
        )
    else:
        shutil.copy2(source, destination)


class SystemLayerTransaction:
    """Back up and restore the paths that an llmzk update is allowed to change."""

    def __init__(self, vault: Path, relative_paths: Iterable[str | Path]) -> None:
        self.vault = vault.expanduser().resolve()
        self.relative_paths = tuple(Path(path) for path in relative_paths)
        self._backup_root: Path | None = None
        self._snapshots: list[Snapshot] = []

    @property
    def backup_root(self) -> Path | None:
        return self._backup_root

    def __enter__(self) -> SystemLayerTransaction:
        self._backup_root = Path(
            tempfile.mkdtemp(prefix=".llmzk-update-backup-", dir=self.vault)
        )

        try:
            for relative_path in self.relative_paths:
                source = self.vault / relative_path
                existed = _exists(source)
                self._snapshots.append(Snapshot(relative_path, existed))
                if existed:
                    _copy_path(source, self._backup_root / relative_path)
        except BaseException:
            self._cleanup()
            raise
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            self._cleanup()
            return False

        try:
            self.restore()
        except BaseException as rollback_error:
            assert self._backup_root is not None
            raise UpdateRollbackError(
                "Update failed and the previous system layer could not be fully restored",
                self._backup_root,
            ) from rollback_error

        self._cleanup()
        return False

    def restore(self) -> None:
        if self._backup_root is None:
            raise RuntimeError("Transaction has not been started")

        for snapshot in reversed(self._snapshots):
            _remove(self.vault / snapshot.relative_path)

        for snapshot in self._snapshots:
            if not snapshot.existed:
                continue
            backup = self._backup_root / snapshot.relative_path
            target = self.vault / snapshot.relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(backup), str(target))

    def _cleanup(self) -> None:
        if self._backup_root is not None:
            shutil.rmtree(self._backup_root, ignore_errors=True)
        self._backup_root = None


def system_layer_transaction(
    vault: Path,
    relative_paths: Iterable[str | Path],
) -> SystemLayerTransaction:
    return SystemLayerTransaction(vault, relative_paths)
