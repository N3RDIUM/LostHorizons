class BufferDataStorage:
    def __init__(self) -> None:
        """
        This class stores the data for a buffer.
        """
        self.vertices = []
        self.colors = []

    def has_changed(self, other_storage) -> bool:
        """
        Returns True if the this storage is different from other_storage.
        """
        return hash(frozenset(self.vertices)) != hash(
            frozenset(other_storage.vertices)
        ) or hash(frozenset(self.colors)) != hash(frozenset(other_storage.colors))
