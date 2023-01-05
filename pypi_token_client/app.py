from datetime import date
from pprint import pprint

from . import sync_client
from .credentials import KeyringAndPromptCredentialsProvider


def create_token(
    project: str,
    token_name: str | None = None,
    headless: bool = True,
):
    token_name = token_name or f"a{date.today()}"
    credentials_provider = KeyringAndPromptCredentialsProvider()
    token = sync_client.create_project_token(
        project,
        token_name,
        credentials_provider,
        headless,
    )
    print("Created token:")
    print(token)


def list_tokens(headless: bool = True):
    credentials_provider = KeyringAndPromptCredentialsProvider()
    tokens = sync_client.get_token_list(credentials_provider, headless)
    pprint(tokens)
