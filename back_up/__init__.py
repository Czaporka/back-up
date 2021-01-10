from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
import json
import logging
import os
from pathlib import Path
import shutil
from typing import Dict, List

import yaml


logger = logging.getLogger(__name__)


class BackUpException(RuntimeError):
    pass


@dataclass
class Config:
    log_file: Path
    backups_dir: Path
    to_backup: Dict[str, str]

    def __init__(self, log_file: str, backups_dir: str, to_backup: Dict[str, str]):
        self.log_file = Path(log_file).expanduser()
        self.backups_dir = Path(backups_dir).expanduser()
        self.to_backup = to_backup

    @classmethod
    def from_file(cls, file: Path) -> "Config":
        try:
            with file.open() as fh:
                return cls(**yaml.safe_load(fh))
        except Exception as e:
            msg = f"Could not read config from {CONFIG_FILE}"
            logging.exception(msg)
            raise BackUpException(msg)


@dataclass
class Info:
    """
    """
    top_level: Path
    files: Dict[Path, str]  # path to hash

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


CONFIG_FILE = Path("./back-up.yaml").expanduser()  # TODO


def _get_hash(path: Path) -> str:
    with path.open("rb") as fh:
        hash = md5()
        while chunk := fh.read(8192):
            hash.update(chunk)
    return hash.hexdigest()


def main():
    logging.basicConfig(
        level="INFO",
        format="%(filename)s:%(lineno)d %(levelname)s %(message)s")

    config = Config.from_file(CONFIG_FILE)

    for item, path in config.to_backup.items():
        path = Path(path)
        current_hashes = {f: _get_hash(f) for f in path.glob("**/*") if f.is_file()}
        info_files = (config.backups_dir / item).glob("*.json")
        info_files = sorted(info_files, key=lambda p: p.stat().st_mtime)

        if info_files:
            latest_info = Info.from_json_file(info_files[0])
            if latest_info.files == current_hashes:
                return

        config.backups_dir.mkdir(exist_ok=True)
        backup = config.backups_dir / item / datetime.now().strftime("%Y-%m-%dT%H%M%S")
        shutil.make_archive(
            base_name=backup,
            format="zip",
            root_dir=path)
        Info(path, current_hashes).to_json_file(str(backup) + ".json")


if __name__ == "__main__":
    main()
