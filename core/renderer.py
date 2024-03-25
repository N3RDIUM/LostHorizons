# imports
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_COLOR_ARRAY,
    GL_FLOAT,
    GL_VERTEX_ARRAY,
    glColorPointer,
    glDrawArrays,
    glEnable,
    glEnableClientState,
    glVertexPointer,
)

from core.buffer import Buffer
from core.bufferdata import BufferDataStorage

# Enable required OpenGL features
glEnable(GL_ARRAY_BUFFER)
glEnableClientState(GL_VERTEX_ARRAY)
glEnableClientState(GL_COLOR_ARRAY)


class Renderer:

    def __init__(self, parent):
        """
        Renderer
        This renders the bufferdata_storage stuff and handles vbo data updates.
        """
        super().__init__()
        self.parent = parent
        self.storages = {}
        self.buffers = {}
        self.deletion_queue = []

        glEnableClientState(GL_VERTEX_ARRAY)

    def create_storage(self, id):
        """
        Create a new storage.
        """
        local_storage = BufferDataStorage()
        local_storage.vertices = []
        local_storage.colors = []
        self.storages[id] = local_storage
        self.buffers[id] = {
            "vertices": Buffer(f"{str(id)}-vertices"),
            "colors": Buffer(f"{str(id)}-colors"),
            "show": True,
        }

    def update_storage(self, id, vertices, colors):
        """
        If the storage has changed, update it.
        """
        self.storages[id].vertices = vertices.copy()
        self.storages[id].colors = colors.copy()

        self.buffers[id]["vertices"].modify(vertices)
        self.buffers[id]["colors"].modify(colors)

    def update(self):
        """
        Update the buffers.
        """

    def draw_storage(self, id):
        """
        Draw the specified storage.
        """
        vbo_vertices = self.buffers[id]["vertices"]
        vbo_colors = self.buffers[id]["colors"]
        vbo_vertices.bind()
        glVertexPointer(3, GL_FLOAT, 0, vbo_vertices.buf)
        vbo_colors.bind()
        glColorPointer(3, GL_FLOAT, 0, vbo_colors.buf)

        glDrawArrays(GL_TRIANGLES, 0, len(self.storages[id].vertices) // 3)

        vbo_vertices.unbind()
        vbo_colors.unbind()

    def draw(self):
        """
        Draw all the storages.
        """
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LEQUAL)
        glDepthRange(0.0, 1.0)
        try:
            for storage in self.storages:
                try:
                    if self.buffers[storage]["show"]:
                        self.draw_storage(storage)
                except KeyError:
                    pass
        except RuntimeError:
            self.draw()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

        # Process one deletion per frame
        if len(self.deletion_queue) > 0:
            self.delete_storage(self.deletion_queue.pop(0))

    def delete_storage(self, id):
        """
        Delete the specified storage.
        """
        try:
            del self.buffers[id]["show"]
            for buffer_type in self.buffers[id]:
                try:
                    self.buffers[id][buffer_type].delete()
                except AttributeError:
                    pass
            del self.buffers[id]
            del self.storages[id]
        except KeyError:
            pass

    def delete_later(self, id):
        """
        Delete the specified storage later.
        """
        self.deletion_queue.append(id)

    def show(self, id):
        try:
            self.buffers[id]["show"] = True
        except KeyError:
            pass

    def hide(self, id):
        try:
            self.buffers[id]["show"] = False
        except KeyError:
            pass
