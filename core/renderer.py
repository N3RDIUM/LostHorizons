from multiprocessing import shared_memory

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
            "vtx_shared_memory": shared_memory.SharedMemory(
                create=True, size=32768 * 512, name=f"buffer-{str(id)}-vertices"
            ),
            "clr_shared_memory": shared_memory.SharedMemory(
                create=True, size=32768 * 512, name=f"buffer-{str(id)}-colors"
            ),
            "show": True,
        }

    def update_storage(self, id, item):
        """
        If the storage has changed, update it.
        """
        try:
            vertices = self.buffers[id]["vtx_shared_memory"]
            colors = self.buffers[id]["clr_shared_memory"]
            shape = item["shape"]
            vtx_shape = shape["vtx"]
            clr_shape = shape["clr"]

            vtx = np.ndarray(shape=vtx_shape, dtype=np.float32, buffer=vertices.buf)
            clr = np.ndarray(shape=clr_shape, dtype=np.float32, buffer=colors.buf)

            self.buffers[id]["vertices"].modify(vtx)
            self.buffers[id]["colors"].modify(clr)

            self.storages[id].vertices = vtx.copy()
            self.storages[id].colors = clr.copy()
        except KeyError:
            pass

    def update(self):
        """
        Update the buffers.
        """
        for i, item in enumerate(self.parent.result_queue):
            try:
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
            try:
                self.buffers[id]["vtx_shared_memory"].unlink()
                self.buffers[id]["vtx_shared_memory"].close()
                self.buffers[id]["clr_shared_memory"].unlink()
                self.buffers[id]["clr_shared_memory"].close()
                del self.buffers[id]["vtx_shared_memory"]
                del self.buffers[id]["clr_shared_memory"]
            except:
                pass
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
        self.buffers[id]["show"] = True

    def hide(self, id):
        self.buffers[id]["show"] = False
