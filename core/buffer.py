# imports
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *
VBO_SIZE = 1600000

class Buffer:
    """
    Buffer

    This is a wrapper for OpenGL buffer objects.
    """

    def __init__(self, id):
        """
        Initializes the buffer.
        """
        self.id = id
        self.buf = vbo.VBO(np.zeros(VBO_SIZE, dtype=np.float32),  usage="GL_STATIC_DRAW")

    def modify(self, data, offset=0):
        """
        Adds data to the buffer.

        :param data: The data to add to the buffer.
        :param offset: The offset to start writing at.
        """
        # Modify the buffer
        data = np.array(data, dtype=np.float32)
        self.buf.bind()
        self.buf[offset:offset + len(data)] = data
        self.buf.unbind()
        glFlush()
        
    def bind(self):
        """
        Binds the buffer.
        """
        self.buf.bind()

    def unbind(self):
        """
        Unbinds the buffer.
        """
        self.buf.unbind()

    def delete(self):
        """
        Deletes the buffer.
        """
        self.buf.delete()
