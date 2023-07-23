from core.leafnode import LeafNode
from core.utils import midpoint
import math

class QuadTree:
    def __init__(self, rect=[(0,0,0), (100,0,0), (100,0,100), (0,0,100)], level=1, parent=None, planet=None):
        self.rect = rect
        self.level = level
        self.parent = parent
        self.planet = planet
        self.children = []
        self.size = (self.rect[1][0] - self.rect[0][0]) / 2
        self.position = []
        self.planet.generation_queue.append(self)
    
    def generate(self):
        lnode = LeafNode(self.rect, 4, self, self.planet)
        self.children.append(lnode)
        self.position = [
            (self.rect[0][0]+self.rect[1][0]+self.rect[2][0]+self.rect[3][0])/4,
            (self.rect[0][1]+self.rect[1][1]+self.rect[2][1]+self.rect[3][1])/4,
            (self.rect[0][2]+self.rect[1][2]+self.rect[2][2]+self.rect[3][2])/4
        ]
        
    def split(self):
        if self.level >= 2:
            return
        # Split the quad into 4 quads
        corner1 = self.rect[0]
        corner2 = self.rect[1]
        corner3 = self.rect[2]
        corner4 = self.rect[3]
        
        # Make a midpoint between each corner
        midpoint1 = midpoint(corner1, corner2)
        midpoint2 = midpoint(corner2, corner3)
        midpoint3 = midpoint(corner3, corner4)
        midpoint4 = midpoint(corner4, corner1)
        midpoint5 = midpoint(corner1, corner3)
        
        # Now, make a simple quad
        rect1 = [corner1, midpoint1, midpoint5, midpoint4]
        rect2 = [midpoint1, corner2, midpoint2, midpoint5]
        rect3 = [midpoint5, midpoint2, corner3, midpoint3]
        rect4 = [midpoint4, midpoint5, midpoint3, corner4]
        
        # Create a node for each quad
        node1 = QuadTree(rect1, self.level + 1, self.parent, planet=self.planet)
        node2 = QuadTree(rect2, self.level + 1, self.parent, planet=self.planet)
        node3 = QuadTree(rect3, self.level + 1, self.parent, planet=self.planet)
        node4 = QuadTree(rect4, self.level + 1, self.parent, planet=self.planet)
        
        # Add the nodes to the children list
        self.children.append(node1)
        self.children.append(node2)
        self.children.append(node3)
        self.children.append(node4)
        
        # self.children[0].dispose()
        # del self.children[0]
        
    def unite(self):
        del self.children[:]
        self.generate()
        
    def draw(self):
        for child in self.children:
            child.draw()
        
    def update(self, camera_position):
        if len(self.position) == 0:
            return
        
        # Calculate the distance between the camera and the center of the quad
        distance = math.dist([
            -camera_position[0],
            -camera_position[2],
        ], [
            self.position[0],
            self.position[2]
        ])
        
        # If the camera is close enough to the quad, split it
        if distance < self.size:
            if len(self.children) == 1:
                self.split()
            for child in self.children:
                try:
                    child.update(camera_position)
                except:
                    pass
        else:
            if len(self.children) == 4:
                self.unite()