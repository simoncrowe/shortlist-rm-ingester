import typing


class SetStore(typing.Protocol):
    """Simple set-like data store
    supporting adding members and membership checks.
    """

    def __contains__(self, item: typing.Any):
        pass

    def add(self, item: typing.Any):
        pass
