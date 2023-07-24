import math
from core.node import Node
from settings import settings
PROCESSES_PER_FRAME = settings['LoD']['processes_per_frame']

class DummyPlanet:
    def __init__(self, size=100, position=[0, 0, 0]):
        self.size = size
        self.position = position
        self.generation_queue = []
        self.call_queue = []
        self.chunks = {}
        self.split_queue = []
        self.unify_queue = []
        self.type = "planet"
        self.campos = [0, 0, 0]
        
class Planet:
    def __init__(self, size=400, position=[0, 0, 0]):
        self.size = size
        self.position = position
        self.generation_queue = []
        self.call_queue = []
        self.chunks = {}
        self.split_queue = []
        self.unify_queue = []
        self.campos = [0, 0, 0] # Camera position
        self.type = "planet"
        
    def generate_chunk(self, side, rect):
        self.chunks[side] = Node(rect=rect,parent=self, planet=self)
        self.generation_queue.append(self.chunks[side])
        
    def generate(self):
        size = self.size
        # Generate the 6 sides of the world
        self.generate_chunk("top", [(0,size,0), (0,size,size), (size,size,size), (size,size,0)])
        self.generate_chunk("left", rect=[(0,0,0), (0,0,size), (0,size,size), (0,size,0)])
        self.generate_chunk("front", rect=[(0,0,0), (0,size,0), (size,size,0), (size,0,0)])

        self.generate_chunk("bottom", rect=[(0,0,0), (size,0,0), (size,0,size), (0,0,size)])
        self.generate_chunk("right", rect=[(size,0,0), (size,size,0), (size,size,size), (size,0,size)])
        self.generate_chunk("back", rect=[(0,0,size), (size,0,size), (size,size,size), (0,size,size)]) 
        
    @staticmethod
    def normalize(vector):
        length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        return vector[0] / length, vector[1] / length, vector[2] / length
    def update(self, camera):
        # Update the camera position
        self.campos = [
            -camera.position[0]+self.position[0],
            -camera.position[1]+self.position[1],
            -camera.position[2]+self.position[2]
        ]
        
        # Update the chunks
        for chunk in self.chunks.values():
            chunk.update(camera.position)
        
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
            if len(self.generation_queue) == 0:
                return
            _ = self.generation_queue.pop(-1)
            _.generate_unified()
        
    def findchunk(self, id):
        for chunk in self.chunks.keys():
            if self.chunks[chunk].id == id:
                return chunk
            
    def draw(self):
        for chunk in self.chunks.values():
            chunk.draw()