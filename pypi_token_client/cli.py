from dataclasses import dataclass
from pathlib import Path

import typer

from . import app

cli_app = typer.Typer(
    context_settings={
        "auto_envvar_prefix": "PYPITOKENCLIENT",
    }
)


@dataclass
class TyperState:
    headless: bool
    persist_to: Path | None
    username: str | None
    password: str | None


@cli_app.callback()
def typer_callback(
    ctx: typer.Context,
    headless: bool = typer.Option(
        True,
        help="whether to run the broswer in headless mode "
        "(note that in non-headless mode, it will wait for you to inspect "
        "the situation and close it manually when an error happens)",
    ),
    persist_to: str = typer.Option(
        None,
        "--persist",
        metavar="PATH",
        help="persist browser state to directory (no persistence if not set)",
    ),
    username: str = typer.Option(
        None,
        "--username",
        "-u",
        help="PyPI username (will prompt for it if not given)",
    ),
    password: str = typer.Option(
        None,
        help="PyPI password "
        "(will prompt for it or load it from the keyring if not given); "
        "you should probably NOT set this via the CLI because it "
        "will then be visible in the list of processes; "
        "it's safer to provide it as an env var",
    ),
):
    ctx.obj = TyperState(
        headless,
        Path(persist_to) if persist_to is not None else None,
        username,
        password,
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
        headless=ctx.obj.headless,
        persist_to=ctx.obj.persist_to,
        username=ctx.obj.username,
        password=ctx.obj.password,
    )


@cli_app.command("list")
def list_tokens(ctx: typer.Context):
    """
    List tokens on PyPI
    """
    app.list_tokens(
        headless=ctx.obj.headless,
        persist_to=ctx.obj.persist_to,
        username=ctx.obj.username,
        password=ctx.obj.password,
    )


@cli_app.command()
def delete(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="name of token to delete"),
):
    """
    Delete token on PyPI
    """
    app.delete_token(
        name=name,
        headless=ctx.obj.headless,
        persist_to=ctx.obj.persist_to,
        username=ctx.obj.username,
        password=ctx.obj.password,
    )


def cli_main():
    cli_app()


if __name__ == "__main__":
    cli_main()
