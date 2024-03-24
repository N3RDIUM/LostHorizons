# imports
import numpy as np
from OpenGL.arrays import vbo

VBO_SIZE = 65536 * 12  # 32 is the n_segments in the leafnode class


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
        self.buf = vbo.VBO(
            np.zeros(VBO_SIZE, dtype=np.float32),
            usage="GL_DYNAMIC_DRAW",
            target="GL_ARRAY_BUFFER",
        )
        self.max_idx = 0

    def modify(self, data, offset=-1):
        """
        Adds data to the buffer.

        :param data: The data to add to the buffer.
        :param offset: The offset to start writing at.
        """
        data = np.array(data, dtype=np.float32)
        if offset == -1:
            offset = self.max_idx
        self.max_idx = max(self.max_idx, offset + len(data))
        self.buf[offset : offset + len(data)] = data

    def delete(self):
        self.buf.delete()
