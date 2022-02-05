import logging
from sys import exit

from . import (
    __version__, LOG_FORMAT_FILE, LOG_FORMAT_FILE_LIB, LOG_FORMAT_STDERR,
    LOG_FORMAT_STDERR_LIB, parse_args)
from .app import BackUpApp
from .config import Config


logger = logging.getLogger(__name__)
library_logger = logging.getLogger("_lib_logger")
library_logger.info = library_logger.debug


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
    args = parse_args()

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
