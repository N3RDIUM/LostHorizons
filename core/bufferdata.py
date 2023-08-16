from uuid import uuid4

class BufferDataStorage(object):
    def __init__(self):
        """
        BufferDataStorage
        This class stores the data for a buffer.
        """
        self.vertices = []
        self.colors = []
        self.uuid = uuid4()
        
    def has_changed(self, other_storage):
        return (
            hash(frozenset(self.vertices)) != hash(frozenset(other_storage.vertices)) or
            hash(frozenset(self.colors)) != hash(frozenset(other_storage.colors))
        )

class SharableBufferDataStorage(BufferDataStorage):
    def __init__(self, manager):
        """
        BufferDataStorage
        This class stores the data for a buffer.
        TODO: Implement textures instead of colors.
        """
        super().__init__()
        self.vertices = manager.list()
        self.colors = manager.list()
    