import argparse
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
import json
import logging
from pathlib import Path
import shutil
from typing import Dict, Optional

import yaml


DEFAULT_CONFIG_FILE = Path("~/.back-up.yaml").expanduser()


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BackUpException(RuntimeError):
    pass


Hash = str


@dataclass
class Config:
    backups_dir: Path
    to_backup: Dict[str, Path]
    logging_level: str
    log_file: Path = None

    def __init__(self,
                 backups_dir: str,
                 to_backup: Dict[str, str],
                 logging_level: Optional[str] = None,
                 log_file: Optional[str] = None):
        self.log_file = Path(log_file).expanduser()
        self.backups_dir = Path(backups_dir).expanduser()
        self.to_backup = {name: Path(path) for name, path in to_backup.items()}
        self.logging_level = logging_level

    @classmethod
    def from_file(cls, file: Path) -> "Config":
        try:
            with file.open() as fh:
                return cls(**yaml.safe_load(fh))
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
    with path.open("rb") as fh:
        hash = md5()
        while chunk := fh.read(8192):
            hash.update(chunk)
    return hash.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Utility for backing up directories.")
    parser.add_argument("--backups-dir", help="set the directory to dump the "
                        "backups to; this is the 'general' backups directory, "
                        "i.e. specific directories that you back up will have "
                        "their own subdirectories in there", metavar="PATH")
    parser.add_argument("--log-file", help="set the file to dump logs to",
                        metavar="PATH")
    parser.add_argument("--to-backup", help="set the directories to back up; "
                        "PATH is the directory to back up, NAME is an "
                        "arbitrary identifier used to organize the backup "
                        "files in the backup directory, so it's easier to "
                        "find the thing you want to restore; sample value: "
                        "'DOCUMENTS=~/Documents' (the tilde will be expanded "
                        "appropriately, backups will be dumped under "
                        "'<backups_dir>/DOCUMENTS/')",
                        metavar="NAME=PATH", nargs="+")
    parser.add_argument("--config-file", help=f"where to take config from; "
                        "command line arguments have priority though; "
                        f"default: '{DEFAULT_CONFIG_FILE}'.",
                        default=DEFAULT_CONFIG_FILE, metavar="PATH")
    return parser.parse_args()


def set_up_logging(log_file: Optional[Path] = None,
                   logging_level: Optional[str] = None):
    formatter = logging.Formatter(
        "%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s")

    if log_file is not None:
        log_file.parent.mkdir(exist_ok=True)
        handler_file = logging.FileHandler(log_file)
        handler_file.setFormatter(formatter)
        handler_file.setLevel(logging.DEBUG)
        logger.addHandler(handler_file)

    handler_stderr = logging.StreamHandler()
    handler_stderr.setFormatter(formatter)
    handler_stderr.setLevel(logging.DEBUG)
    logger.addHandler(handler_stderr)

    if logging_level is not None:
        logger.setLevel(logging_level)


def main():
    args = parse_args()

    config = Config.from_file(args.config_file)
    config.update(args)

    set_up_logging(config.log_file, config.logging_level)

    for item, path in config.to_backup.items():

        logger.info(f"Processing {item}...")

        current_hashes = {f: _get_hash(f)
                          for f
                          in path.glob("**/*")
                          if f.is_file()}
        info_files = (config.backups_dir / item).glob("*.json")
        info_files = sorted(info_files, key=lambda p: p.stat().st_mtime)

        if info_files:
            latest_info = Info.from_json_file(info_files[0])
            if latest_info.files == current_hashes:
                logger.info("> The most recent backup is still up to date!")
                return

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
