"""
Sync client, which is just a wrapper around the async one.
"""
import asyncio
from contextlib import contextmanager
from typing import Sequence

from . import async_client
from .common import TokenListEntry
from .credentials import PypiCredentials
from .utils import SyncifiedContextManager


@contextmanager
def sync_pypi_token_client(
    credentials: PypiCredentials, headless: bool = True
):
    with SyncifiedContextManager(
        async_client.async_pypi_token_client(credentials, headless)
    ) as async_session:
        yield SyncPypiTokenClientSession(async_session)


class SyncPypiTokenClientSession:
    def __init__(
        self, async_session: async_client.AsyncPypiTokenClientSession
    ):
        self.async_session = async_session

    def create_project_token(
        self,
        project_name: str,
        token_name: str,
    ) -> str:
        return asyncio.run(
            self.async_session.create_project_token(project_name, token_name)
        )

    def get_token_list(self) -> Sequence[TokenListEntry]:
        return asyncio.run(self.async_session.get_token_list())
