from dataclasses import dataclass
from getpass import getpass

import keyring

keyring_service_name = "pypi-token-automation"


@dataclass
class PypiCredentials:
    username: str
    password: str


def prompt_for_credentials() -> PypiCredentials:
    username = input("pypi username: ")
    password = getpass("pypi password: ")
    return PypiCredentials(username, password)


def get_credentials_from_keyring() -> PypiCredentials | None:
    cred = keyring.get_credential(keyring_service_name, None)
    if cred:
        return PypiCredentials(cred.username, cred.password)
    return None


def save_credentials_to_keyring(credentials: PypiCredentials):
    keyring.set_password(
        keyring_service_name, credentials.username, credentials.password
    )
