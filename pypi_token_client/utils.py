import asyncio
from typing import Any, AsyncContextManager, ContextManager, Sequence


def one_or_none(seq: Sequence[Any]):
    if len(seq) > 1:
        raise ValueError("more than one element found")
    elif len(seq) == 1:
        return seq[0]
    return None


class SyncifiedContextManager(ContextManager):
    def __init__(self, cm: AsyncContextManager):
        self.cm = cm

    def __enter__(self):
        return asyncio.run(self.cm.__aenter__())

    def __exit__(self, *exc_info):
        return asyncio.run(self.cm.__aexit__(*exc_info))
