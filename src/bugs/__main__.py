import logging
from pathlib import Path

import typer
from platformdirs import user_config_dir
from rich.logging import RichHandler

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


if __name__ == "__main__":
    app()
