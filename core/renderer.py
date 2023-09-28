import json

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
import os
import filelock

glEnable(GL_ARRAY_BUFFER)
glEnableClientState(GL_VERTEX_ARRAY)
glEnableClientState(GL_COLOR_ARRAY)


class Renderer(object):
    def __init__(self, parent):
        """
        Renderer
        This renders the bufferdata_storage stuff and handles vbo data updates.
        """
        super().__init__()
        self.parent = parent
        self.storages = {}
        self.buffers = {}

        self.create_storage("default")

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
        }

    def update_storage(self, id, result):
        """
        If the storage has changed, update it.
        TODO: Only update the parts of the storage that have changed.
        """
        id = id
        local_storage = self.storages[id]
        with filelock.FileLock(result["datafile"] + ".lock"):
            with open(result["datafile"], "r") as f:
                res = json.load(f)
                vertices = res["vertices"]
                colors = res["colors"]
        local_storage.vertices.extend(list(vertices))
        local_storage.colors.extend(list(colors))
        self.buffers[id]["vertices"].modify(local_storage.vertices)
        self.buffers[id]["colors"].modify(local_storage.colors)
        os.remove(result["datafile"])

    def update(self):
        """
        Update the buffers.
        """
        for i in range(len(self.parent.result_queue)):
            item = self.parent.result_queue[i]
            if item["type"] == "buffer_mod":
                if item["mesh"] in self.storages:
                    self.update_storage(item["mesh"], item)
                # else:
                    # self.create_storage(item["mesh"])
                    # self.update_storage(item["mesh"], item)
                self.parent.result_queue.pop(i)

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
        glDrawArrays(GL_TRIANGLES, 0, len(self.storages[id].vertices) // 3)

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