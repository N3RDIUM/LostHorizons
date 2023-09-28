class BufferDataStorage(object):

    def __init__(self):
        """
        BufferDataStorage
        This class stores the data for a buffer.
        """
        self.vertices = []
        self.colors = []

    def has_changed(self, other_storage):
        return hash(frozenset(self.vertices)) != hash(
            frozenset(other_storage.vertices)) or hash(frozenset(
                self.colors)) != hash(frozenset(other_storage.colors))
