from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict

from . import Hash


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
