# back-up
[![build](https://github.com/Czaporka/back-up/actions/workflows/cicd.yml/badge.svg?branch=master)](https://github.com/Czaporka/back-up/actions/workflows/cicd.yml)
[![codecov](https://codecov.io/gh/Czaporka/back-up/branch/master/graph/badge.svg)](https://codecov.io/gh/Czaporka/back-up)

## Description
`back-up` is a very simple utility for backing up directories of files.

## Features
- Awfully simple.
- Configured with a YAML configuration file, where you can specify what directories
  should be backed up, and where the backups should be stored.
- For each directory to back up, it checks whether its contents have changed since
  the last time it was backed up. If not, then `back-up` will not waste disk space
  by creating another copy. This means that it can simply be called at regular
  intervals, e.g. scheduled with `cron` or `Task Scheduler` to run every 1 hour or so.

## Installation
```bash
pip install back-up
```

## Configuration
`back-up` reads the configuration from file `~/.config/back-up/back-up.yaml`. That is where you should specify all the directories you want backed up. See [sample back-up.yaml file](https://github.com/Czaporka/back-up/blob/master/back-up.yaml) for available configuration options.

It is also possible, albeit usually impractical, to specify all the parameters on the command line.

## Usage
```
usage: back-up [-h] [--archive-format FORMAT] [--backups-dir PATH]
               [--config-file PATH] [--log-file PATH]
               [--logging-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--to-backup NAME=PATH [NAME=PATH ...]] [--quiet] [--verbose]
               [--version]

Utility for backing up directories of files.

optional arguments:
  -h, --help            show this help message and exit
  --archive-format FORMAT
                        what format to store the backups in; default: 'zip'
  --backups-dir PATH    set the directory to dump the backups to; this is the
                        'general' backups directory, i.e. specific directories
                        that you back up will have their own subdirectories in
                        there
  --config-file PATH    where to take config from; command line arguments have
                        priority though; default: '~/.config/back-up/back-
                        up.yaml'
  --log-file PATH       set the file to dump logs to
  --logging-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        set logging verbosity
  --to-backup NAME=PATH [NAME=PATH ...]
                        set the directories to back up; PATH is the directory
                        to back up, NAME is an arbitrary identifier used to
                        organize the backup files in the backup directory, so
                        it's easier to find the thing you want to restore;
                        sample value: 'DOCUMENTS=~/Documents' (the tilde will
                        be expanded appropriately, backups will be dumped
                        under '<backups_dir>/DOCUMENTS/...')
  --quiet, -q           decrease verbosity of console output
  --verbose, -v         increase verbosity of console output
  --version, -V         show version and exit
```

## Development
### Prepare environment
```
python3 -m venv .env
source .env/bin/activate
pip install --editable .
pip install coverage pycodestyle
```
### Run tests, generate coverage reports etc.
```
coverage run --source back_up/ -m unittest discover tests/
coverage report
coverage html
pycodestyle back_up/ tests/

# same thing but on one line:
coverage run --source back_up/ -m unittest discover tests/ \
  && coverage report \
  && coverage html \
  && pycodestyle back_up/ tests/
```

## TODO
- [ ] Add some sort of cleanup capability for really old backups.
