from uuid import uuid4

class BufferDataStorage(object):
    def __init__(self):
        """
        BufferDataStorage
        This class stores the data for a buffer.
        TODO: Implement textures instead of colors.
        """
        self.vertices = []
        self.indices = []
        self.normals = []
        self.colors = []
        
        self.previous_vertices = []
        self.previous_indices = []
        self.previous_normals = []
        self.previous_colors = []
        
        self.uuid = uuid4()