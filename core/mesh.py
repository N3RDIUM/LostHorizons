import numpy as np
from OpenGL.GL import *

# A mesh class which has its own VBO
from OpenGL.GL import *
from OpenGL.arrays import vbo
import numpy as np

glLineWidth(8)

class Mesh:
    def __init__(self, vertices, indices, normals=[], uvs=[]):
        self.vertices = vertices
        self.indices = indices
        self.normals = normals
        self.uvs = uvs
        
        # Only implement the vertices
        self.vbo = vbo.VBO(np.array(self.vertices, 'f'))
        self.normal_vbo = vbo.VBO(np.array(self.normals, 'f'))
        
    def draw(self):
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
            
    def __del__(self):
        self.vbo.delete()
        self.normal_vbo.delete()