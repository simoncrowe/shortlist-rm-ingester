import typing


class SetStore(typing.Protocol):
    """Simple set-like data store
    supporting adding members and membership checks.
    """

    def __contains__(self, item: str):
        pass

    def add(self, item: str):
        pass
