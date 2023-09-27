from uuid import uuid4


class LeafNode(object):

    def __init__(self,
                 quad,
                 segments=64,
                 parent=None,
                 planet=None,
                 renderer=None,
                 game=None):
        """
        LeafNode
        """
        self.quad = quad
        self.segments = segments
        self.parent = parent
        self.planet = planet
        self.renderer = renderer
        self.game = game
        self.uuid = uuid4()

    def generate(self):
        """
        Schedule the generation of this chunk using multiprocessing.
        """
        self.mesh = self.renderer.create_storage(self.uuid)

        for i in range(len(self.game.processes)):
            self.game.addToQueue({
                "task": "tesselate",
                "mesh": self.uuid,
                "quad": self.quad,
                "segments": self.segments,
                "denominator": len(self.game.processes),
                "numerator": i,
            })
