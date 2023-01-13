"""
PyPI credential data structure and utilities.
"""
from dataclasses import dataclass
from getpass import getpass

import keyring

keyring_service_prefix = "pypi-token-client-cli"


@dataclass
class PypiCredentials:
    username: str
    "PyPI username"
    password: str
    "PyPI password"


def make_keyring_service_name(pypi_base_url: str) -> str:
    return f"{keyring_service_prefix} ({pypi_base_url})"


def get_credentials_from_keyring_and_prompt(
    pypi_base_url: str,
    username: str | None = None,
    password: str | None = None,
) -> tuple[PypiCredentials, bool]:
    """
    Get PyPI credentials from both the keyring and by prompting the user.

    Returns:
      Tuple of the credentials and whether the credentials were not in the
      keyring ("credentials are new" boolean).
    """
    if username is not None and password is not None:
        return (PypiCredentials(username, password), False)
    if username is None:
        username = input("pypi username: ")
    if password is not None:
        return (PypiCredentials(username, password), True)
    credentials = get_credentials_from_keyring(pypi_base_url, username)
    if credentials is None:
        password = getpass("pypi password: ")
        return (PypiCredentials(username, password), True)
    return (credentials, False)


def prompt_for_credentials(username: str | None = None) -> PypiCredentials:
    if username is None:
        username = input("pypi username: ")
    password = getpass("pypi password: ")
    return PypiCredentials(username, password)


def get_credentials_from_keyring(
    pypi_base_url: str, username: str
) -> PypiCredentials | None:
    cred = keyring.get_credential(
        make_keyring_service_name(pypi_base_url), username
    )
    if cred:
        return PypiCredentials(cred.username, cred.password)
    return None


def save_credentials_to_keyring(
    pypi_base_url: str, credentials: PypiCredentials
):
    keyring.set_password(
        make_keyring_service_name(pypi_base_url),
        credentials.username,
        credentials.password,
    )
