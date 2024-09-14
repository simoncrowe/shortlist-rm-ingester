import typing


class SetStore(typing.Protocol):
    """Simple set-like data store
    supporting adding members and membership checks.
    """

    def __contains__(self, item: typing.Any):
        """Does the store contain an item."""

    def add(self, item: typing.Any):
        """Add and item to the store"""
