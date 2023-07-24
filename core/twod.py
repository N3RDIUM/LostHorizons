from core.planet import DummyPlanet
from core.node import Node
from settings import settings
PROCESSES_PER_FRAME = settings['LoD']['processes_per_frame']

class TwoDTerrain:
    def __init__(self, planet=DummyPlanet(), render_distance=4, chunksize=10000):
        self.planet = planet
        self.render_distance = render_distance
        self.chunksize = chunksize
        self.chunks = {}
        self.split_queue = []
        self.unify_queue = []
        self.type = "planet"
        
    def generate_chunk(self, position):
        self.chunks[tuple(position)] = Node(
            rect=[
                (position[0]*self.chunksize,0,position[2]*self.chunksize),
                (position[0]*self.chunksize+self.chunksize,0,position[2]*self.chunksize),
                (position[0]*self.chunksize+self.chunksize,0,position[2]*self.chunksize+self.chunksize),
                (position[0]*self.chunksize,0,position[2]*self.chunksize+self.chunksize)
            ],parent=self, planet=self.planet)
        self.planet.generation_queue.append(self.chunks[tuple(position)])
        
    def generate(self):
        # Generate the world
        for x in range(-self.render_distance, self.render_distance):
            for z in range(-self.render_distance, self.render_distance):
                self.generate_chunk((x, 0, z))
                
    def update(self, camera):
        for chunk in self.chunks.values():
            chunk.update(camera.position)
            
        currchunk = [-camera.position[0]//self.chunksize, -camera.position[2]//self.chunksize]
        chunks = []
        for x in range(-self.render_distance, self.render_distance):
            for z in range(-self.render_distance, self.render_distance):
                chunks.append((currchunk[0]+x, 0, currchunk[1]+z))
        for chunk in chunks:
            if chunk not in self.chunks:
                self.generate_chunk(chunk)
        try:
            for chunk in self.chunks.keys():
                if chunk not in chunks:
                    self.chunks[chunk].dispose()
                    del self.chunks[chunk]
        except RuntimeError:
            pass
        
        for i in range(PROCESSES_PER_FRAME):        
            # Process the split queue
            tosplit = self.split_queue.pop(0) if len(self.split_queue) > 0 else None
            if tosplit:
                tosplit.swap_children()
                tosplit.generate_split()
                
            # Process the unify queue
            tounify = self.unify_queue.pop(0) if len(self.unify_queue) > 0 else None
            if tounify:
                rect = tounify.rect.copy()
                parent = tounify.parent
                planet = tounify.planet
                id = tounify.id
                tounify_index = self.findchunk(id)
                if tounify_index:
                    tounify.dispose()
                    del self.chunks[tounify_index]
                    del tounify
                    tounify = Node(rect, 1, parent, planet=planet)
                    tounify.generate_unified()
                    self.chunks[tounify_index] = tounify
                else:
                    pass
        for i in range(PROCESSES_PER_FRAME):
            if len(self.planet.generation_queue) == 0:
                return
            _ = self.planet.generation_queue.pop(-1)
            _.generate_unified()
        
    def findchunk(self, id):
        for chunk in self.chunks.keys():
            if self.chunks[chunk].id == id:
                return chunk
            
    def draw(self):
        for chunk in self.chunks.values():
            chunk.draw()