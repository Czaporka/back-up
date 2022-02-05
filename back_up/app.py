from datetime import datetime
from hashlib import md5
import logging
import os.path
from pathlib import Path
import shutil

from .config import Config
from .info import Info
from . import HASH_CHUNK_SIZE, Hash


class BackUpApp:

    def __init__(self, logger: logging.Logger, library_logger: logging.Logger):
        self.logger = logger
        self.library_logger = library_logger

    def run(self, config: Config):
        self.logger.info("Starting a new backing up...")

        if not config.to_backup:
            self.logger.warning("Nothing to do!")

        for item, path in config.to_backup.items():
            self.logger.info(f"Processing {item}...")

            if not os.path.exists(path):
                self.logger.info("> Source directory does not exist - skipping.")
                continue

            self.logger.debug("> Computing hashes...")
            current_hashes = {
                f: self._get_hash(f) for f in path.glob("**/*") if f.is_file()}

            self.logger.debug("> Comparing with latest backup...")
            info_files = (config.backups_dir / item).glob("*.json")
            info_files = sorted(info_files, key=lambda p: p.stat().st_mtime)
            if not info_files:
                self.logger.debug("> There are no previous backups.")
                diff = dict(
                    added=frozenset(),
                    modified=frozenset(),
                    removed=frozenset(),
                )
                previous_version = None
            else:
                previous_version = info_files[-1]
                latest_info = Info.from_json_file(previous_version)
                latest_files = set(latest_info.files.keys())
                current_files = set(current_hashes.keys())

                diff = dict(
                    added=frozenset(current_files - latest_files),
                    modified=frozenset(
                        f for f in current_files & latest_files
                        if current_hashes[f] != latest_info.files[f]),
                    removed=frozenset(latest_files - current_files),
                )
                if not any(diff.values()):
                    self.logger.info(
                        "> The most recent backup is still up to date!")
                    continue

            self.logger.info("> Making a backup...")

            backup_dir = config.backups_dir / item

            self.logger.debug(f"-> Creating directory {backup_dir}...")
            backup_dir.mkdir(exist_ok=True, parents=True)

            now = datetime.now().strftime("%Y-%m-%dT%H%M%S")
            backup = backup_dir / now
            result = shutil.make_archive(
                base_name=backup,
                format=config.archive_format,
                root_dir=path,
                logger=self.library_logger)
            self.logger.debug(f'-> Created a new backup: "{result}".')

            self.logger.debug(
                f"-> Storing new backup metadata under {backup}.json...")
            Info(path, current_hashes,
                 diff, previous_version).to_json_file(str(backup) + ".json")

            self.logger.info("> Done!")
        self.logger.info("Finished!")

    @staticmethod
    def _get_hash(path: Path) -> Hash:
        hash = md5()
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(HASH_CHUNK_SIZE)
                if not chunk:
                    break
                hash.update(chunk)
        return hash.hexdigest()
