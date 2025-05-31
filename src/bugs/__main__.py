import logging
from pathlib import Path
from time import monotonic

import typer
from platformdirs import user_config_dir
from rich.logging import RichHandler
from watchfiles import watch

from .config import load_config

logger = logging.getLogger("bugs")
logging.getLogger().addHandler(
    RichHandler(
        rich_tracebacks=True,
        tracebacks_code_width=None,  # pyright: ignore[reportArgumentType]
    )
)


app = typer.Typer()


@app.command()
def main(log: str = "INFO", config_path: Path | None = None) -> None:
    logger.setLevel(log)
    logger.info("Starting bugs!")

    if config_path is None:
        config_path = Path(user_config_dir("bugs", appauthor=False), "config.toml")
    config = load_config(config_path)
    logger.debug(config)

    # Monitor when we started the last backup, to ensure we stick to the minimum interval set.
    # Initialised at 0, so the first change always gets backed up. This would be good to change if
    # we ever start saving persistent state information, but that seems like overkill for now.
    last_backup_time = 0

    for _changes in watch(
        *config.sources,
    ):
        if monotonic() < last_backup_time + config.min_interval:
            # Too early, the minimum interval hasn't elapsed yet!
            continue

        # Save the time that the backup started, not the time that it ended, in case a backup takes
        # a non-insignificant amount of time.
        last_backup_time = monotonic()
        logger.info("Changes detected!")


if __name__ == "__main__":
    app()
