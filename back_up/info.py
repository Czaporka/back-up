from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional

from . import Hash


# TODO: lstrip "files" of "top_level"


@dataclass
class Info:
    """Information about the backup, gets dumped together with the zip file."""
    top_level: Path
    files: Dict[Path, Hash]
    differences: Dict[str, FrozenSet[Path]] = field(
        default_factory=lambda: dict(
            added=frozenset(),
            modified=frozenset(),
            removed=frozenset(),
        )
    )
    previous_version: Optional[Path] = None

    def to_json_file(self, path: str):
        d = dict(
            top_level=str(self.top_level),
            files={str(path): hash for path, hash in self.files.items()},
        )
        if any(self.differences.values()):
            d["differences"] = {k: list(map(str, v)) for k, v
                                in self.differences.items()}
        with open(path, "w") as fh:
            json.dump(d, fh, indent=4)
            fh.write("\n")

    @classmethod
    def from_json_file(cls, path: str) -> "Info":
        with open(path) as fh:
            d = json.load(fh)
        return cls(
            top_level=Path(d["top_level"]),
            files={
                Path(path): hash for path, hash in d["files"].items()},
            differences={
                k: frozenset(map(Path, v))
                for k, v
                in d.get("differences", {})},
            previous_version=(
                Path(d.get("previous_version"))
                if d.get("previous_version") is not None
                else None),
        )
