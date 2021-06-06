import argparse
import logging
from pathlib import Path
from typing import Dict, Optional, Union

import yaml

from . import (
    BackUpException, DEFAULT_ARCHIVE_FORMAT, DEFAULT_BACKUPS_DIR,
    DEFAULT_LOGGING_LEVEL,
)


logger = logging.getLogger(__name__)


class Config:
    """Parameters controlling the program's execution details."""

    __slots__ = (
        "_backups_dir",
        "_log_file",
        "_to_backup",
        "archive_format",
        "logging_level",
        "quiet",
        "verbose",
    )

    def __init__(self,
                 archive_format: str = DEFAULT_ARCHIVE_FORMAT,
                 backups_dir: str = DEFAULT_BACKUPS_DIR,
                 to_backup: Dict[str, str] = {},
                 logging_level: str = DEFAULT_LOGGING_LEVEL,
                 log_file: Optional[str] = None):
        self.archive_format = archive_format
        self.backups_dir = backups_dir
        self.log_file = log_file
        self.logging_level = logging_level
        self.to_backup = to_backup

        self.quiet = 0
        self.verbose = 0

    def __repr__(self) -> str:
        kvps = ", ".join(
            f"{k.lstrip('_')}={getattr(self, k)}" for k in self.__slots__)
        return f"{type(self).__name__}({kvps})"

    @property
    def to_backup(self) -> Dict[str, Path]:
        return self._to_backup

    @to_backup.setter
    def to_backup(self, to_backup: Dict[str, str]):
        self._to_backup = {
            name: Path(path).expanduser() for name, path in to_backup.items()}

    @property
    def backups_dir(self) -> Path:
        return self._backups_dir

    @backups_dir.setter
    def backups_dir(self, backups_dir: Union[str, Path]):
        self._backups_dir = Path(backups_dir).expanduser()

    @property
    def log_file(self) -> Path:
        return self._log_file

    @log_file.setter
    def log_file(self, log_file: Optional[Union[str, Path]]):
        if log_file is None:
            self._log_file = None
        else:
            self._log_file = Path(log_file).expanduser()

    @classmethod
    def from_file(cls, file: str) -> "Config":
        try:
            with Path(file).expanduser().open() as fh:
                return cls(**yaml.safe_load(fh))
        except FileNotFoundError:
            logging.warning(f"Config file {file} does not exist.")
            return cls()
        except Exception:
            msg = f"Could not read config from '{file}'!"
            logger.exception(msg)
            raise BackUpException(msg)

    def update(self, args: argparse.Namespace):
        """Override values from config file with values from command line."""
        for k, v in vars(args).items():
            if v is not None:
                try:
                    setattr(self, k, v)
                except AttributeError:
                    pass
