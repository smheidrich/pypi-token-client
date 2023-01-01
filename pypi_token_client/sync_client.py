"""
Sync client, which is just a wrapper around the async one.
"""
import asyncio

from . import async_client
from .credentials import PypiCredentials


def create_project_token(
    project: str,
    token_name: str,
    credentials: PypiCredentials,
    headless: bool = False,
):
    return asyncio.run(
        async_client.create_project_token(
            project, token_name, credentials, headless=headless
        )
    )


def get_token_list(credentials: PypiCredentials, headless: bool = False):
    return asyncio.run(
        async_client.get_token_list(credentials, headless=headless)
    )
