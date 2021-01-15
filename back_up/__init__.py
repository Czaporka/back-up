"""Back up directories efficiently.

How it works:
  1.
    The script visits each directory specified in the config file or on the
      command line, then hashes every file under it.
  2.1.
    The script compresses the directory and stores the result in the backups
      folder.
  2.2.
    The script also stores the hashes alongside the compressed backup file.
  3.
    The next time the script is supposed to back up a directory, it hashes the
      files again, then compares the results with the hashes from the most
      recent backup. If the hashes are the same, the script doesn't dump the
      same file again not to waste disk space. If the hashes differ, a new
      backup is stored under a new timestamp.

Potential TODO:
  - Clean up old backups.
"""
import argparse
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
import json
import logging
from pathlib import Path
import shutil
from typing import Dict, Optional, Union

import yaml


DEFAULT_ARCHIVE_FORMAT = "zip"
DEFAULT_BACKUPS_DIR = "~/.backups"
DEFAULT_CONFIG_FILE = "~/.config/back-up/back-up.yaml"
DEFAULT_LOGGING_LEVEL = "INFO"
HASH_CHUNK_SIZE = 65536
LOG_FORMAT_FILE = \
    "%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s"
LOG_FORMAT_STDERR = "%(filename)s:%(lineno)d %(levelname)s %(message)s"


logger = logging.getLogger(__name__)


class BackUpException(RuntimeError):
    pass


Hash = str


class Config:
    """Parameters controlling the program's execution details."""

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

    def __repr__(self) -> str:
        kvps = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{type(self).__name__}({kvps})"

    @property
    def to_backup(self) -> Path:
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
                vars(self)[k] = v


@dataclass
class Info:
    """Information about the backup, gets dumped together with the zip file."""
    top_level: Path
    files: Dict[Path, Hash]

    def to_json_file(self, path: str):
        d = dict(
            top_level=str(self.top_level),
            files={str(path): hash for path, hash in self.files.items()},
        )
        with open(path, "w") as fh:
            json.dump(d, fh, indent=4)

    @classmethod
    def from_json_file(cls, path: str) -> "Info":
        with open(path) as fh:
            d = json.load(fh)
        return cls(
            top_level=Path(d["top_level"]),
            files={Path(path): hash for path, hash in d["files"].items()},
        )


def _get_hash(path: Path) -> Hash:
    hash = md5()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(HASH_CHUNK_SIZE)
            if not chunk:
                break
            hash.update(chunk)
    return hash.hexdigest()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Utility for backing up directories.")
    parser.add_argument("--backups-dir", help="set the directory to dump the "
                        "backups to; this is the 'general' backups directory, "
                        "i.e. specific directories that you back up will have "
                        "their own subdirectories in there", metavar="PATH")
    parser.add_argument("--log-file", help="set the file to dump logs to",
                        metavar="PATH")
    parser.add_argument("--logging-level", help="set logging verbosity",
                        choices=(
                            "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"))
    parser.add_argument("--to-backup", help="set the directories to back up; "
                        "PATH is the directory to back up, NAME is an "
                        "arbitrary identifier used to organize the backup "
                        "files in the backup directory, so it's easier to "
                        "find the thing you want to restore; sample value: "
                        "'DOCUMENTS=~/Documents' (the tilde will be expanded "
                        "appropriately, backups will be dumped under "
                        "'<backups_dir>/DOCUMENTS/...')",
                        metavar="NAME=PATH", nargs="+")
    parser.add_argument("--config-file", help=f"where to take config from; "
                        "command line arguments have priority though; "
                        f"default: '{DEFAULT_CONFIG_FILE}'",
                        default=DEFAULT_CONFIG_FILE, metavar="PATH")
    parser.add_argument("--archive-format", help="what format to store the "
                        f"backups in; default: '{DEFAULT_ARCHIVE_FORMAT}'",
                        metavar="FORMAT")
    return parser.parse_args()


def _set_up_logging(log_file: Optional[Path] = None,
                    logging_level: Optional[str] = None):
    logger.propagate = False

    if log_file is not None:
        log_file.parent.mkdir(exist_ok=True)
        handler_file = logging.FileHandler(log_file)
        handler_file.setFormatter(logging.Formatter(LOG_FORMAT_FILE))
        handler_file.setLevel(logging.DEBUG)
        logger.addHandler(handler_file)

    handler_stderr = logging.StreamHandler()
    handler_stderr.setFormatter(logging.Formatter(LOG_FORMAT_STDERR))
    handler_stderr.setLevel(logging.DEBUG)
    logger.addHandler(handler_stderr)

    if logging_level is not None:
        logger.setLevel(logging_level)


def main():
    args = _parse_args()

    config = Config.from_file(args.config_file)
    config.update(args)

    _set_up_logging(config.log_file, config.logging_level)

    logger.info("Starting a new backing up...")
    logger.debug("args: %s", args)
    logger.debug("config: %s", config)

    if not config.to_backup:
        logger.warning("Nothing to do!")

    for item, path in config.to_backup.items():

        logger.info(f"Processing {item}...")

        current_hashes = {f: _get_hash(f)
                          for f
                          in path.glob("**/*")
                          if f.is_file()}
        info_files = (config.backups_dir / item).glob("*.json")
        info_files = sorted(info_files, key=lambda p: p.stat().st_mtime)

        if info_files:
            latest_info = Info.from_json_file(info_files[-1])
            if latest_info.files == current_hashes:
                logger.info("> The most recent backup is still up to date!")
                continue

        logger.info("> Making a backup...")

        config.backups_dir.mkdir(exist_ok=True)

        now = datetime.now().strftime("%Y-%m-%dT%H%M%S")
        backup = config.backups_dir / item / now
        shutil.make_archive(
            base_name=backup,
            format="zip",
            root_dir=path)
        Info(path, current_hashes).to_json_file(str(backup) + ".json")

        logger.info("> Done!")
    logger.info("Finished!")


if __name__ == "__main__":
    main()
