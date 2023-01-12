pypi-token-client
=================

pypi-token-client is a library and CLI tool for retrieving PyPI project tokens.

Purpose
-------

PyPI allows the creation of per-project tokens but
`doesn't <https://github.com/pypi/warehouse/issues/6396>`_ currently have an
API to do so. While integration with CI providers is
`planned <https://github.com/pypi/warehouse/issues/6396#issuecomment-1345585291>`_,
apparently there is
`no plan <https://github.com/pypi/warehouse/issues/6396#issuecomment-1345667940>`_
for an API that would allow one to create tokens from a local development
machine.

This tool seeks to provide a client exposing this functionality anyway by
whatever means necessary.

Operating principle
-------------------

Because there is no API and I'm also too lazy to try and figure out the exact
sequence of HTTP requests one would have to make to simulate what happens when
requesting tokens on the PyPI website, for now this tool just uses
`Playwright <https://playwright.dev/python/>`_ to automate performing the
necessary steps in an *actual* browser.

This might be overkill and brittle but it works for now 🤷


Table of contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   cli
   library
   reference


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
