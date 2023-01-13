from dataclasses import dataclass
from pathlib import Path

import typer

from pypi_token_client.common import AllProjects, SingleProject

from .app import App

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
    pypi_base_url: str = "https://pypi.org"


def _app_from_typer_state(state: TyperState) -> App:
    return App(
        state.headless,
        state.persist_to,
        state.username,
        state.password,
        state.pypi_base_url,
    )


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
    pypi_base_url: str = typer.Option(
        "https://pypi.org", help="base URL of the pypi website to use"
    ),
):
    ctx.obj = TyperState(
        headless,
        Path(persist_to) if persist_to is not None else None,
        username,
        password,
        pypi_base_url,
    )


@cli_app.command()
def create(
    ctx: typer.Context,
    token_name: str = typer.Argument(..., help="name of the token"),
    project: str = typer.Option(
        None, help="project for which to generate token"
    ),
):
    """
    Create a new token on PyPI
    """
    scope = AllProjects() if project is None else SingleProject(project)
    app = _app_from_typer_state(ctx.obj)
    app.create_token(token_name, scope)


@cli_app.command("list")
def list_tokens(ctx: typer.Context):
    """
    List tokens on PyPI
    """
    app = _app_from_typer_state(ctx.obj)
    app.list_tokens()


@cli_app.command()
def delete(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="name of token to delete"),
):
    """
    Delete token on PyPI
    """
    app = _app_from_typer_state(ctx.obj)
    app.delete_token(name)


def cli_main():
    cli_app()


if __name__ == "__main__":
    cli_main()
