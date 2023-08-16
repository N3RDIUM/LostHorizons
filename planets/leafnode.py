from uuid import uuid4

class LeafNode(object):
    def __init__(
        self,
        quad,
        segments = {
            "x": 32,
            "y": 32
        },
        parent = None,
        planet = None,
    ):
        """
        LeafNode
        """
        self.quad = quad
        self.segments = segments
        self.parent = parent
        self.planet = planet
        
        self.uuid = uuid4()
        self.color = (
            0, 
            102/256, 
            39/256
        )