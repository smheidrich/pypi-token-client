from dataclasses import dataclass
from pathlib import Path

import typer

from . import app

cli_app = typer.Typer()


@dataclass
class TyperState:
    headful: bool
    persist_to: Path | None


@cli_app.callback()
def typer_callback(
    ctx: typer.Context,
    headful: bool = typer.Option(
        False, help="display browser window (i.e. no-headless mode)"
    ),
    persist_to: str = typer.Option(
        None,
        help="persist browser state to directory (default is no persistence)",
    ),
):
    ctx.obj = TyperState(
        headful, Path(persist_to) if persist_to is not None else None
    )


@cli_app.command()
def create(
    ctx: typer.Context,
    project: str = typer.Argument(..., help="project to generate token for"),
    token_name: str = typer.Option(
        None, help="name of the token; will be auto-generated if not given"
    ),
):
    """
    Create a new project token on PyPI
    """
    app.create_token(
        project=project,
        token_name=token_name,
        headless=not ctx.obj.headful,
        persist_to=ctx.obj.persist_to,
    )


@cli_app.command("list")
def list_tokens(ctx: typer.Context):
    """
    List tokens on PyPI
    """
    app.list_tokens(
        headless=not ctx.obj.headful, persist_to=ctx.obj.persist_to
    )


def cli_main():
    cli_app()


if __name__ == "__main__":
    cli_main()
