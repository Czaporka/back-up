"""Back up directories of files.

How it works:
  1. Visits each directory specified in the config file or on the command line,
     then hashes every file under it.

  2. Compresses the directory and files, and stores the result in the backups
     folder, along with the hashes.

  3. The next time it is invoked, it hashes the files again, then compares
     the results with the hashes from the most recent backup. If the hashes
     are the same, it doesn't dump the same file again not to waste disk space.
     If the hashes differ, a new backup is stored under a new timestamp.

Potential TODO:
  - Clean up old backups.
"""
import argparse

from ._version import __version__


DEFAULT_ARCHIVE_FORMAT = "zip"
DEFAULT_BACKUPS_DIR = "~/.backups"
DEFAULT_CONFIG_FILE = "~/.config/back-up/back-up.yaml"
DEFAULT_LOGGING_LEVEL = "INFO"

HASH_CHUNK_SIZE = 65536

_LOG_FORMAT_BASE = "%(module)6s:%(lineno)4d %(levelname)-5s"
LOG_FORMAT_FILE = f"%(asctime)s {_LOG_FORMAT_BASE} %(message)s"
LOG_FORMAT_FILE_LIB = f"%(asctime)s {_LOG_FORMAT_BASE} --> %(message)s"
LOG_FORMAT_STDERR = f"{_LOG_FORMAT_BASE} %(message)s"
LOG_FORMAT_STDERR_LIB = f"{_LOG_FORMAT_BASE} --> %(message)s"


class BackUpException(RuntimeError):
    pass


Hash = str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Utility for backing up directories of files.")
    parser.add_argument(
        "--archive-format", metavar="FORMAT",
        help="what format to store the backups in;"
        f" default: '{DEFAULT_ARCHIVE_FORMAT}'")
    parser.add_argument(
        "--backups-dir", metavar="PATH",
        help="set the directory to dump the backups to; this is the 'general'"
        " backups directory, i.e. specific directories that you back up will"
        " have their own subdirectories in there")
    parser.add_argument(
        "--config-file", metavar="PATH", default=DEFAULT_CONFIG_FILE,
        help=f"where to take config from; command line"
        f" arguments have priority though; default: '{DEFAULT_CONFIG_FILE}'")
    parser.add_argument(
        "--log-file", metavar="PATH",
        help="set the file to dump logs to")
    parser.add_argument(
        "--logging-level", help="set logging verbosity",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"))
    parser.add_argument(
        "--to-backup", metavar="NAME=PATH", nargs="+",
        help="set the directories to back up; PATH is the directory to back"
        " up, NAME is an arbitrary identifier used to organize the backup"
        " files in the backup directory, so it's easier to find the thing you"
        " want to restore; sample value: 'DOCUMENTS=~/Documents' (the tilde"
        " will be expanded appropriately, backups will be dumped under"
        " '<backups_dir>/DOCUMENTS/...')")
    parser.add_argument(
        "--quiet", "-q", action="count", default=0,
        help="decrease verbosity of console output",)
    parser.add_argument(
        "--verbose", "-v", action="count", default=0,
        help="increase verbosity of console output")
    parser.add_argument(
        "--version", "-V", action="store_true",
        help="show version and exit")
    return parser.parse_args()
