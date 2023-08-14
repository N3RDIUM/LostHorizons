# imports
import ctypes
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *

VBO_SIZE = 120000

class Buffer:
    """
    Buffer

    This is a wrapper for OpenGL buffer objects.
    It supports persistent mapping.
    """

    def __init__(self, id):
        """
        Initializes the buffer.
        """
        self.id = id
        data = np.empty(VBO_SIZE, dtype=np.float32)
        self.vbo = vbo.VBO(data, usage='GL_DYNAMIC_DRAW_ARB', target='GL_ARRAY_BUFFER')
        self.vbo.bind()
        self.vbo.unbind()
        
    def modify(self, data):
        """
        Modify the buffer data.
        """
        data = np.asarray(data, dtype=np.float32)
        self.vbo.bind()
        self.vbo.set_array(data, data.nbytes)
        self.vbo.unbind()
        
    def bind(self):
        """
        Bind the buffer.
        """
        self.vbo.bind()
    
    def unbind(self):
        """
        Unbind the buffer.
        """
        self.vbo.unbind()
        
    def delete(self):
        """
        Delete the buffer.
        """
        self.vbo.delete()
        
    def __del__(self):
        """
        Delete the buffer.
        """
        self.delete()