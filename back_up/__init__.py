"""Back up directories efficiently.

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
