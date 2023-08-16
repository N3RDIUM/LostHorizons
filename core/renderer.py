import multiprocessing

from OpenGL.GL import (
    glEnable,
    glEnableClientState,
    glDrawArrays,
    glVertexPointer,
    glColorPointer,
)

from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_VERTEX_ARRAY,
    GL_COLOR_ARRAY,
    GL_FLOAT,
)

from OpenGL.GL import *

from core.buffer import Buffer
from core.bufferdata import BufferDataStorage, SharableBufferDataStorage

glEnable(GL_ARRAY_BUFFER)
glEnableClientState(GL_VERTEX_ARRAY)
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
        self.local_storages = {}
        self.buffers = {}
        
        self.create_storage("default")
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
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
        storage = SharableBufferDataStorage(self.manager)
        storage.uuid = id
        self.storages.update({id: storage})
        self.handle_new_storage(storage)
        return storage
    
    def handle_new_storage(self, storage):
        """
        Handle a new storage.
        This will create the desired buffers for the specified storage.
        """
        local_storage = BufferDataStorage()
        local_storage.vertices = list(storage.vertices)
        local_storage.colors = list(storage.colors)
        self.local_storages[str(storage.uuid)] = local_storage
        self.buffers[str(storage.uuid)] = {
            "vertices": Buffer(f"{str(storage.uuid)}-vertices"),
            "colors": Buffer(f"{str(storage.uuid)}-colors")
        }
    
    def update_storage(self, id):
        """
        If the storage has changed, update it.
        TODO: Only update the parts of the storage that have changed.
        """
        id = id
        storage = self.storages[id]
        local_storage = self.local_storages[id]
        if local_storage.has_changed(storage):
            self.buffers[id]["vertices"].modify(storage.vertices)
            self.buffers[id]["colors"].modify(storage.colors)
            local_storage.vertices = list(storage.vertices)
            local_storage.colors = list(storage.colors)
            
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
        glClear(GL_COLOR_BUFFER_BIT)
    
        vbo_vertices = self.buffers[id]["vertices"].buf
        vbo_colors = self.buffers[id]["colors"].buf
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Bind and enable vertex VBO
        vbo_vertices.bind()
        glVertexPointer(3, GL_FLOAT, 0, vbo_vertices)
        
        # Bind and enable color VBO
        vbo_colors.bind()
        glColorPointer(3, GL_FLOAT, 0, vbo_colors)
        
        glPointSize(8)
        glEnable(GL_POINT_SMOOTH)
        glDrawArrays(GL_POINTS, 0, len(self.storages[id].vertices) // 3)
                
        # Clean up
        vbo_vertices.unbind()
        vbo_colors.unbind()
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
            
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