import json
import os

import filelock
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

    def update_storage(self, id, result):
        """
        If the storage has changed, update it.
        TODO: Only update the parts of the storage that have changed.
        """
        with filelock.FileLock(result["datafile"] + ".lock"):
            conents = ""
            with open(result["datafile"], "r") as f:
                for line in f:
                    conents += line
            res = json.loads(conents)
            vertices = res["vertices"]
            colors = res["colors"]
        try:
            self.storages[id].vertices += vertices
            self.storages[id].colors += colors
            self.buffers[id]["vertices"].modify(vertices)
            self.buffers[id]["colors"].modify(colors)
        except KeyError:
            pass
        os.remove(result["datafile"])
        os.remove(result["datafile"] + ".lock")

    def update(self):
        """
        Update the buffers.
        """
        for i in range(len(self.parent.result_queue)):
            try:
                item = self.parent.result_queue[i]
                if item["type"] == "buffer_mod":
                    self.update_storage(item["mesh"], item)
                    self.parent.result_queue.pop(i)
                    break
            except IndexError:
                break

    def draw_storage(self, id):
        """
        Draw the specified storage.
        """
        vbo_vertices = self.buffers[id]["vertices"].buf
        vbo_colors = self.buffers[id]["colors"].buf
        vbo_vertices.bind()
        glVertexPointer(3, GL_FLOAT, 0, vbo_vertices)
        vbo_colors.bind()
        glColorPointer(3, GL_FLOAT, 0, vbo_colors)

        glDrawArrays(GL_TRIANGLES, 0, len(self.storages[id].vertices) // 3)

        vbo_vertices.unbind()
        vbo_colors.unbind()

    def draw(self):
        """
        Draw all the storages.
        """
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
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
                self.buffers[id][buffer_type].delete()
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
        self.buffers[id]["show"] = True

    def hide(self, id):
        self.buffers[id]["show"] = False
