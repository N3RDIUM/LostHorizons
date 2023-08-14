import multiprocessing

from OpenGL.GL import (
    glEnable,
    glEnableClientState,
    glDrawArrays,
    glNormalPointer,
    glVertexPointer,
    glColorPointer,
)

from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_VERTEX_ARRAY,
    GL_NORMAL_ARRAY,
    GL_COLOR_ARRAY,
    GL_FLOAT,
    GL_TRIANGLES
)

from OpenGL.GL import *

from core.buffer import Buffer
from core.bufferdata import BufferDataStorage

glEnable(GL_ARRAY_BUFFER)
glEnableClientState(GL_VERTEX_ARRAY)
glEnableClientState(GL_NORMAL_ARRAY)
glEnableClientState(GL_COLOR_ARRAY)

class Renderer(object):
    def __init__(self):
        """
        Renderer
        This renders the bufferdata_storage stuff and handles vbo data updates.
        """
        super().__init__()
        self.manager = multiprocessing.Manager()
        self.storages = self.manager.dict()
        self.buffers = {}
        
        self.create_storage("default")
        
    def add_storage(self, storage):
        """
        Add a pre-existing storage to the renderer.
        """
        self.storages.update({storage.uuid: storage})
        self.handle_new_storage(storage)
        
    def create_storage(self, id):
        """
        Create a new storage.
        """
        storage = BufferDataStorage(self.manager)
        storage.uuid = id
        self.storages.update({id: storage})
        self.handle_new_storage(storage)
        return storage
    
    def handle_new_storage(self, storage):
        """
        Handle a new storage.
        This will create the desired buffers for the specified storage.
        """
        self.buffers[str(storage.uuid)] = {
            "vertices": Buffer(f"{str(storage.uuid)}-vertices"),
            "indices": Buffer(f"{str(storage.uuid)}-indices"),
            "normals": Buffer(f"{str(storage.uuid)}-normals"),
            "colors": Buffer(f"{str(storage.uuid)}-colors")
        }
    
    def update_storage(self, id):
        """
        If the storage has changed, update it.
        TODO: Only update the parts of the storage that have changed.
        """
        id = id
        storage = self.storages[id]
        self.buffers[id]["vertices"].modify(storage.vertices)
        storage.previous_vertices = storage.vertices
        self.buffers[id]["indices"].modify(storage.indices)
        storage.previous_indices = storage.indices
        self.buffers[id]["normals"].modify(storage.normals)
        storage.previous_normals = storage.normals
        self.buffers[id]["colors"].modify(storage.colors)
        storage.previous_colors = storage.colors
            
    def update(self):
        """
        Update the buffers.
        """
        for storage in self.storages:
            self.update_storage(storage)
        
    def draw_storage(self, id):
        """
        Draw the specified storage.
        """
        glColor3f(1, 1, 1)
        self.buffers[id]["colors"].bind()
        glColorPointer(3, GL_FLOAT, 0, None)
        self.buffers[id]["vertices"].bind()
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(GL_POINTS, 0, len(self.storages[id].vertices))
        self.buffers[id]["vertices"].unbind()
        self.buffers[id]["colors"].unbind()
        
    def draw(self):
        """
        Draw all the storages.
        """
        for storage in self.storages:
            self.draw_storage(storage)
            
    def delete_storage(self, id):
        """
        Delete the specified storage.
        """
        for buffer_type in self.buffers[id]:
            self.buffers[id][buffer_type].delete()
        del self.buffers[id]
        del self.storages[id]