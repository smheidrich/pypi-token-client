Library usage
=============

Here is a basic example script showing how to use the library's ``async``
client to create a new token on PyPI:

.. code:: python

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

Further information can be found in the :ref:`API Reference`.
