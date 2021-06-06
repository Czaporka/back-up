import argparse
import logging
from sys import exit

from . import (
    __version__, DEFAULT_ARCHIVE_FORMAT, DEFAULT_CONFIG_FILE, LOG_FORMAT_FILE,
    LOG_FORMAT_FILE_LIB, LOG_FORMAT_STDERR, LOG_FORMAT_STDERR_LIB)
from .app import BackUpApp
from .config import Config


logger = logging.getLogger(__name__)
library_logger = logging.getLogger("_lib_logger")
library_logger.info = library_logger.debug


def _parse_args() -> argparse.Namespace:
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


def _set_up_logger(logger: logging.Logger, config: Config, format_file: str,
                   format_stderr: str):
    logger.propagate = False

    if config.log_file is not None:
        config.log_file.parent.mkdir(exist_ok=True)
        handler_file = logging.FileHandler(config.log_file)
        handler_file.setFormatter(logging.Formatter(format_file))
        handler_file.setLevel(logging.DEBUG)
        logger.addHandler(handler_file)

    handler_stderr = logging.StreamHandler()
    handler_stderr.setFormatter(logging.Formatter(format_stderr))
    handler_stderr.setLevel(logging.INFO + 10*config.quiet - 10*config.verbose)
    logger.addHandler(handler_stderr)

    if config.logging_level is not None:
        logger.setLevel(config.logging_level)


def main():
    args = _parse_args()

    if args.version:
        print(f"back-up {__version__}")
        exit(0)

    config = Config.from_file(args.config_file)
    config.update(args)

    _set_up_logger(logger, config, LOG_FORMAT_FILE, LOG_FORMAT_STDERR)
    _set_up_logger(
        library_logger, config, LOG_FORMAT_FILE_LIB, LOG_FORMAT_STDERR_LIB)

    logger.debug("args: %s", args)
    logger.debug("config: %s", config)

    BackUpApp(logger, library_logger).run(config)


if __name__ == "__main__":
    main()
