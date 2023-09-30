from planets.quadtree import Node

class LoDPlanet:
    def __init__(self, game, radius=64, position=[0, 0, 0]):
        self.nodes = {}
        self.game = game
        self.renderer = game.renderer
        self.player = game.player
        self.radius = radius
        self.center = position
        
    def generate(self):
        # 6 faces of a cube
        quads = [
            [ # Top
                (1, 1, -1),
                (1, 1, 1),
                (-1, 1, 1),
                (-1, 1, -1)
            ],
            [ # Bottom
                (1, -1, 1),
                (1, -1, -1),
                (-1, -1, -1),
                (-1, -1, 1)
            ],
            [ # Left
                (-1, 1, -1),
                (-1, 1, 1),
                (-1, -1, 1),
                (-1, -1, -1)
            ],
            [ # Right
                (1, 1, 1),
                (1, 1, -1),
                (1, -1, -1),
                (1, -1, 1)
            ],
            [ # Front
                (1, 1, 1),
                (1, -1, 1),
                (-1, -1, 1),
                (-1, 1, 1)
            ],
            [ # Back
                (-1, 1, -1),
                (-1, -1, -1),
                (1, -1, -1),
                (1, 1, -1)
            ]
        ]
        # Multiply each value by the radius
        for quad in quads:
            for i in range(4):
                quad[i] = (quad[i][0]*self.radius, quad[i][1]*self.radius, quad[i][2]*self.radius)
            quads[quads.index(quad)] = quad
        # Create a node for each quad
        for quad in quads:
            new = Node(
                quad=quad,
                parent=None,
                planet=self,
                renderer=self.renderer,
                game=self.game
            )
            self.nodes[new.id] = new
                
    def update(self):
        for node in self.nodes:
            self.nodes[node].update()