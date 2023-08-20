from planets.node import Node

class Planet(object):
    def __init__(
            self, 
            position = (0, 0, 0), 
            radius = 10,
            renderer = None,
            game = None
        ):
        """
        Planet
        """
        self.position = position
        self.radius = radius
        self.renderer = renderer
        self.game = game
        
        self.children = {}
        
        self.node = Node(
            planet=self,
            renderer=self.renderer,
            game=self.game
        )
        self.node.generate()
        self.node.split()
        self.children[self.node.uuid] = self.node
    
    def draw(self):
        """
        Draw the planet.
        """
        self.node.draw()
