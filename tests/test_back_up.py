from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os.path import exists, expanduser
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile
from textwrap import dedent
import unittest
from unittest.mock import Mock, patch

from back_up import (
    DEFAULT_ARCHIVE_FORMAT,
    DEFAULT_BACKUPS_DIR,
    # DEFAULT_CONFIG_FILE,
    DEFAULT_LOGGING_LEVEL,
)
from back_up.config import Config
from back_up.main import main


class TestConfig(unittest.TestCase):

    def test_from_file_should_use_file_if_exists(self):
        content = dedent("""\
            # comment
            archive_format: gztar
            backups_dir: ~/.backups
            log_file: ~/.logs/back-up.log
            logging_level: WARNING
            # another comment
            to_backup:
              NAME1: /path/to/some/directory/1
              NAME2: /path/to/some/directory/2
        """)
        with NamedTemporaryFile() as fh:
            fh.write(content.encode())
            fh.flush()

            config = Config.from_file(fh.name)

        self.assertEqual(config.archive_format, "gztar")
        self.assertEqual(str(config.backups_dir), expanduser("~/.backups"))
        self.assertEqual(str(config.log_file),
                         expanduser("~/.logs/back-up.log"))
        self.assertEqual(config.logging_level, "WARNING")
        self.assertEqual(config.to_backup, {
            "NAME1": Path("/path/to/some/directory/1"),
            "NAME2": Path("/path/to/some/directory/2"),
        })

    @patch("back_up.main.logging", Mock())
    def test_from_file_should_use_defaults_if_file_does_not_exist(self):
        path = "/path/to/nonexistent/file.txt"
        assert not exists(path)
        buffer = StringIO()

        with redirect_stderr(buffer):
            config = Config.from_file(path)

        self.assertEqual(config.archive_format, DEFAULT_ARCHIVE_FORMAT)
        self.assertEqual(str(config.backups_dir),
                         expanduser(DEFAULT_BACKUPS_DIR))
        self.assertIsNone(config.log_file)
        self.assertEqual(config.logging_level, DEFAULT_LOGGING_LEVEL)
        self.assertEqual(config.to_backup, {})
        self.assertEqual(buffer.getvalue(),
                         "WARNING:root:Config file "
                         "/path/to/nonexistent/file.txt does not exist.\n")

    def test_update(self):
        args = Namespace(log_file="/path/to/log/file.log", some_other_key=True)
        config = Config()

        config.update(args)

        self.assertEqual(config.archive_format, DEFAULT_ARCHIVE_FORMAT)
        self.assertEqual(str(config.backups_dir),
                         expanduser(DEFAULT_BACKUPS_DIR))
        self.assertEqual(str(config.log_file), "/path/to/log/file.log")
        self.assertEqual(config.logging_level, DEFAULT_LOGGING_LEVEL)
        self.assertEqual(config.to_backup, {})


class TestMain(unittest.TestCase):

    def test_main_with_argument_version_should_print_version_and_exit(self):
        args = Namespace(
            archive_format="dummy",
            backups_dir="dummy",
            config_file="dummy",
            log_file="dummy",
            logging_level="dummy",
            to_backup=["dummy"],
            quiet=0,
            verbose=0,
            version=True,
        )
        buffer = StringIO()

        with patch("back_up.main.parse_args", lambda: args), \
             redirect_stdout(buffer), \
             self.assertRaises(SystemExit):
            main()

        self.assertEqual(buffer.getvalue(), "back-up __OVERWRITE_THIS__\n")


class TestEntrypoint(unittest.TestCase):

    def test_entrypoint(self):
        entrypoint = "back-up"

        p = subprocess.Popen([entrypoint, "-h"], stdout=subprocess.DEVNULL)
        p.communicate()

        self.assertEqual(p.returncode, 0)
