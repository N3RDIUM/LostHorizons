from planet.quadtree import Node

class Sphere:
    def __init__(self, simulation, radius=1024, position=[0, 0, 0]):
        self.nodes = {}
        self.simulation = simulation
        self.renderer = simulation.renderer
        self.player = simulation.player
        self.radius = radius
        self.center = position

    def generate(self):
        # 6 faces of a cube
        quads = [
            [(1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1)],  # Top
            [(1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1)],  # Bottom
            [(-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)],  # Left
            [(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1)],  # Right
            [(1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1)],  # Front
            [(-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)],  # Back
        ]
        
        # Multiply each value by the radius
        for quad in quads:
            for i in range(4):
                quad[i] = (
                    quad[i][0] * self.radius,
                    quad[i][1] * self.radius,
                    quad[i][2] * self.radius,
                )
            quads[quads.index(quad)] = quad
            
            new = Node(
                quad=quad,
                parent=None,
                planet=self,
                renderer=self.renderer,
                simulation=self.simulation,
            )
            self.nodes[new.id] = new

    def update(self):
        for node in self.nodes:
            self.nodes[node].update()
