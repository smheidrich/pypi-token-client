# pypi-token-client

[![pipeline status](https://gitlab.com/smheidrich/pypi-token-client/badges/main/pipeline.svg?style=flat-square)](https://gitlab.com/smheidrich/pypi-token-client/-/commits/main)
[![docs](https://img.shields.io/badge/docs-online-brightgreen?style=flat-square)](https://smheidrich.gitlab.io/pypi-token-client/)
[![pypi](https://img.shields.io/pypi/v/pypi-token-client)](https://pypi.org/project/pypi-token-client/)
[![supported python versions](https://img.shields.io/pypi/pyversions/pypi-token-client)](https://pypi.org/project/pypi-token-client/)

Library and CLI tool for retrieving PyPI project tokens.

## Purpose

PyPI allows the creation of per-project tokens but
[doesn't](https://github.com/pypi/warehouse/issues/6396) currently have an API
to do so. While integration with CI providers is
[planned](https://github.com/pypi/warehouse/issues/6396#issuecomment-1345585291),
apparently there is
[no plan](https://github.com/pypi/warehouse/issues/6396#issuecomment-1345667940)
for an API that would allow one to create tokens from a local development
machine.

This tool seeks to provide a client exposing this functionality anyway by
whatever means necessary.

## Operating principle

Because there is no API and I'm also too lazy to try and figure out the exact
sequence of HTTP requests one would have to make to simulate what happens when
requesting tokens on the PyPI website, for now this tool just uses
[Playwright](https://playwright.dev/python/) to automate performing the
necessary steps in an *actual* browser.

This might be overkill and brittle but it works for now 🤷

## Installation

To install from PyPI:

```bash
pip3 install pypi-token-client
```

You'll also have to install the required Playwright browsers (currently just
Chromium):

```bash
playwright install chromium
```

## Command-line tool usage

To create a token `yourtokenname` for your PyPI project `yourproject`:

```bash
pypi-token-client create --project yourproject yourtokenname
```

There are more commands - please refer to the docs.

## Usage as a library

Basic example script:

```python
import asyncio
from os import getenv

from pypi_token_client import (
  async_pypi_token_client, SingleProject, PypiCredentials
)

credentials = PypiCredentials(getenv("PYPI_USER"), getenv("PYPI_PASS"))

async def main() -> str:
  async with async_pypi_token_client(credentials) as session:
      token = await session.create_token(
          "my token",
          SingleProject("my-project"),
      )
  return token

token = asyncio.run(main())

print(token)
```

## More information

For more detailed usage information and the API reference, refer to
[the documentation](https://smheidrich.gitlab.io/pypi-token-client/).
