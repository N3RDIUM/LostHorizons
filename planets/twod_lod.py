from planets.leafnode import LeafNode

class LoD:
    def __init__(self, game, render_distance, chunk_size=16):
        self.nodes = {}
        self.render_distance = render_distance
        self.game = game
        self.renderer = game.renderer
        self.player = game.player
        self.chunk_size = chunk_size
        
    def generate_chunk(self, x, z):
        _x = int(x)
        _z = int(z)
        x = int(x)
        X = x + 1
        z = int(z)
        Z = z + 1
        x *= self.chunk_size
        X *= self.chunk_size
        z *= self.chunk_size
        Z *= self.chunk_size
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
        self.nodes[(_x, _z)] = self.leafnode
        
    def generate(self):
        for x in range(-self.render_distance, self.render_distance+1):
            for z in range(-self.render_distance, self.render_distance+1):
                self.generate_chunk(x, z)
                
    def on_drawcall(self):
        player_position = self.player.position
        player_position = (-player_position[0] // self.chunk_size, -player_position[2] // self.chunk_size)
        _nodes = []
        for x in range(-self.render_distance, self.render_distance+1):
            for z in range(-self.render_distance, self.render_distance+1):
                _nodes.append((x + player_position[0], z + player_position[1]))
        for node in _nodes:
            if node not in self.nodes:
                self.generate_chunk(node[0], node[1])
        to_delete = []
        for node in self.nodes:
            if node not in _nodes:
                self.nodes[node].delete()
                to_delete.append(node)
        for node in to_delete:
            del self.nodes[node]