from planets.leafnode import LeafNode

class LoD:
    def __init__(self, game, render_distance):
        self.nodes = []
        self.render_distance = render_distance
        self.game = game
        self.renderer = game.renderer
        self.player = game.player
        
    def generate_chunk(self, x, z):
        x = int(x)
        X = x + 1
        z = int(z)
        Z = z + 1
        self.leafnode = LeafNode(
            quad= [
                (x, -1, z),
                (X, -1, z),
                (X, -1, Z),
                (x, -1, Z)
            ],
            segments=64,
            parent=None,
            planet=None,
            renderer=self.renderer,
            game=self.game
        )
        self.game.generation_queue.append(self.leafnode)
        
    def generate(self):
        for x in range(-self.render_distance, self.render_distance):
            for z in range(-self.render_distance, self.render_distance):
                self.generate_chunk(x, z)
                self.nodes.append(self.leafnode)