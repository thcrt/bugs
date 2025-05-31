import tomllib
from dataclasses import InitVar, dataclass, field
from logging import getLogger
from pathlib import Path

import tattl
import tattl.exceptions
from platformdirs import user_data_dir

logger = getLogger(__name__)


@dataclass
class Config:
    game_title: str
    """The name of the game. This will determine the name of the subdirectory
    of `target` in which backups will be stored."""

    sources: list[Path] = field(init=False)
    sources_init: InitVar[list[str]] = field(metadata={"name": "sources"})
    """The files or directories to be included in a backup. POSIX-style
    globbing with `*` and `**` is supported."""

    limit: int = 50
    """The maximum number of backups to keep. If this limit is reached and a
    new backup is triggered, the oldest backup will be deleted."""

    target: Path = field(init=False)
    target_init: InitVar[str] = field(
        default=user_data_dir("bugs", appauthor=False), metadata={"name": "target"}
    )
    """The directory in which backups will be stored. Defaults to
    platform-specific data directory:

    - `/home/<user>/.local/share/bugs` (Unix)
    - `/Users/<user>/Library/Application Support/bugs` (macOS)
    - `C:\\Users\\<user>\\AppData\\Local\\bugs` (Windows)
    """

    def __post_init__(
        self,
        sources_init: list[str],
        target_init: str,
    ):
        self.sources = [Path(source) for source in sources_init]
        self.target = Path(target_init)


def load_config(path: Path):
    with path.open("rb") as f:
        data = tomllib.load(f)
    try:
        return tattl.unpack_dict(data, Config)
    except tattl.exceptions.MissingFieldException as e:
        logger.error("Your configuration file is missing the field `%s`!", e.args[0])
        raise SystemExit(1) from e
    except tattl.exceptions.ValidationException as e:
        logger.error("There was an error in your configuration file: %s", e.args[0])
        raise SystemExit(1) from e
