from core.planet import DummyPlanet
from core.quadtree import QuadTree

class TwoDTerrain:
    def __init__(self, planet=DummyPlanet(), render_distance=4, chunksize=100):
        self.planet = planet
        self.render_distance = render_distance
        self.chunksize = chunksize
        self.chunks = {}
        
    def generate_chunk(self, position):
        self.chunks[tuple(position)] = QuadTree(
            rect=[
                (position[0]*self.chunksize,0,position[2]*self.chunksize),
                (position[0]*self.chunksize+self.chunksize,0,position[2]*self.chunksize),
                (position[0]*self.chunksize+self.chunksize,0,position[2]*self.chunksize+self.chunksize),
                (position[0]*self.chunksize,0,position[2]*self.chunksize+self.chunksize)
            ],parent=self, planet=self.planet)
        
    def generate(self):
        # Generate the world
        for x in range(-self.render_distance, self.render_distance):
            for z in range(-self.render_distance, self.render_distance):
                self.generate_chunk((x, 0, z))
                
    def update(self, camera):
        for chunk in self.chunks.values():
            chunk.update(camera.position)
        
        if len(self.planet.generation_queue) == 0:
            return
        _ = self.planet.generation_queue.pop(-1)
        _.generate()
            
    def draw(self):
        for chunk in self.chunks.values():
            chunk.draw()