# TODO: Comments
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *


class Mesh:

    def __init__(self, vertices, indices, normals=[], uvs=[]):
        self.vertices = vertices
        self.indices = indices
        self.normals = normals
        self.uvs = uvs

        self.vbo = vbo.VBO(np.array(self.vertices, "f"))
        self.normal_vbo = vbo.VBO(np.array(self.normals, "f"))

    def draw(self):
        try:
            self.vbo.bind()
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, self.vbo)

            self.normal_vbo.bind()
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, self.normal_vbo)

            glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))

            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)

            self.vbo.unbind()
            self.normal_vbo.unbind()
        except:
            pass

    def dispose(self):
        if self.vbo:
            self.vbo.delete()
            del self.vbo
            self.vbo = None
        if self.normal_vbo:
            self.normal_vbo.delete()
            del self.normal_vbo
            self.normal_vbo = None
        glFinish()
