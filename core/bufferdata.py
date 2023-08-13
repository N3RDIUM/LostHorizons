from uuid import uuid4

class BufferDataStorage(object):
    def __init__(self, manager):
        """
        BufferDataStorage
        This class stores the data for a buffer.
        TODO: Implement textures instead of colors.
        """
        self.vertices = manager.list()
        self.indices = manager.list()
        self.normals = manager.list()
        self.colors = manager.list()
        
        self.previous_vertices = manager.list()
        self.previous_indices = manager.list()
        self.previous_normals = manager.list()
        self.previous_colors = manager.list()
        
        self.uuid = uuid4()
        self.changed = False