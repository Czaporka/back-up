# back-up

## Description
`back-up` is a utility for backing up directories (and their content).

I wrote it on impulse after discovering that my many hours' savegame files had been deleted for unknown reasons 😄

## Features
- Can be called at fixed intervals but will not waste disk space if the latest backup is already up to date.
- Is really simple otherwise.
- Is configured with a YAML configuration file.

## Installation
```bash
pip install back-up
```

## Configuration
`back-up` reads the configuration from file `~/.config/back-up/back-up.yaml`. That is where you should specify all the directories you want backed up. See [sample back-up.yaml file](https://github.com/Czaporka/back-up/blob/master/back-up.yaml) for available options.

It is also possible, albeit usually impractical, to specify all the parameters on the command line.

## Usage
```
usage: back-up [-h] [--backups-dir PATH] [--log-file PATH]
               [--logging-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--to-backup NAME=PATH [NAME=PATH ...]] [--config-file PATH]
               [--archive-format FORMAT]

Utility for backing up directories.

optional arguments:
  -h, --help            show this help message and exit
  --backups-dir PATH    set the directory to dump the backups to; this is the
                        'general' backups directory, i.e. specific directories
                        that you back up will have their own subdirectories in
                        there
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
  --config-file PATH    where to take config from; command line arguments have
                        priority though; default: '~/.config/back-up/back-
                        up.yaml'
  --archive-format FORMAT
                        what format to store the backups in; default: 'zip'
```

## TODO
- [ ] Add some sort of cleanup capability for really old backups.
