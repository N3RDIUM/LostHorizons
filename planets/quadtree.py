import math
import threading
import time
from uuid import uuid4


def midpoint(v1, v2):
    x = (v1[0] + v2[0]) / 2
    y = (v1[1] + v2[1]) / 2
    z = (v1[2] + v2[2]) / 2

    return [x, y, z]

class LeafNode:
    def __init__(
        self, quad, segments=64, parent=None, planet=None, renderer=None, game=None
    ):
        """
        LeafNode
        """
        self.quad = quad
        self.segments = segments
        self.parent = parent
        self.planet = planet
        self.renderer = renderer
        self.game = game
        self.uuid = str(uuid4())
        self.generated = False
        self.expected_verts = 49920 / 64 * segments

    def generate(self):
        """
        Schedule the generation of this chunk using multiprocessing.
        """
        self.mesh = self.renderer.create_storage(self.uuid)
        level = 1
        if self.parent:
            level = self.parent.level
        self.game.addToQueue(
            {
                "task": "tesselate_full",  # NOT partial
                "mesh": self.uuid,
                "quad": self.quad,
                "segments": self.segments,
                "denominator": self.segments // 16,
                "planet_center": self.planet.center,
                "planet_radius": self.planet.radius,
                "level": level
            }
        )

    def delete(self):
        """
        Delete this chunk.
        """
        self.renderer.delete_later(self.uuid)
        
    def show(self): self.renderer.show(self.uuid)
    def hide(self): self.renderer.hide(self.uuid)
        
class Node:
    def __init__(
        self, quad, parent=None, planet=None, renderer=None, game=None, level=1
    ):
        """
        My go at a QuadTree node implementation.
        """
        self.quad = quad
        self.parent = parent
        self.planet = planet
        self.renderer = renderer
        self.game = game
        self.id = str(uuid4())
        self.level = level

        self.position = [
            (self.quad[0][0] + self.quad[1][0] + self.quad[2][0] + self.quad[3][0]) / 4,
            (self.quad[0][1] + self.quad[1][1] + self.quad[2][1] + self.quad[3][1]) / 4,
            (self.quad[0][2] + self.quad[1][2] + self.quad[2][2] + self.quad[3][2]) / 4,
        ]
        self.size = (
            math.dist(self.quad[0], self.position)
            + math.dist(self.quad[1], self.position)
            + math.dist(self.quad[2], self.position)
            + math.dist(self.quad[3], self.position)
        )

        self.children = {}
        self.cached_leaf = None
        self.generate_unified()
        self.state = "unified"

    def generate_unified(self):
        """
        Generate the node as a unified node, i.e. consisting of only one leaf node.
        """
        if not self.cached_leaf:
            new = LeafNode(
                quad=self.quad,
                parent=self.parent,
                planet=self.planet,
                renderer=self.renderer,
                game=self.game,
            )
            self.game.generation_queue.append(new)
            # Indexes: "unified": unified node and "split": [array of 4 nodes]
            self.children["unified"] = new
            self.cached_leaf = new
        else:
            self.children["unified"] = self.cached_leaf
            self.children["unified"].show()

    def generate_split(self):
        """
        Generate the node as a split node, i.e. consisting of four leaf nodes.
        """
        # Split the quad into 4 quads
        corner1 = self.quad[0]
        corner2 = self.quad[1]
        corner3 = self.quad[2]
        corner4 = self.quad[3]

        # Make a midpoint between each corner
        midpoint1 = midpoint(corner1, corner2)
        midpoint2 = midpoint(corner2, corner3)
        midpoint3 = midpoint(corner3, corner4)
        midpoint4 = midpoint(corner4, corner1)
        midpoint5 = midpoint(corner1, corner3)

        # Now, make 4 quads
        quad1 = [corner1, midpoint1, midpoint5, midpoint4]
        quad2 = [midpoint1, corner2, midpoint2, midpoint5]
        quad3 = [midpoint5, midpoint2, corner3, midpoint3]
        quad4 = [midpoint4, midpoint5, midpoint3, corner4]

        # Create a node for each quad
        node1 = Node(
            quad=quad1,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game,
            level=self.level + 1,
        )
        node2 = Node(
            quad=quad2,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game,
            level=self.level + 1,
        )
        node3 = Node(
            quad=quad3,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game,
            level=self.level + 1,
        )
        node4 = Node(
            quad=quad4,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game,
            level=self.level + 1,
        )

        # Add the nodes to the children list
        self.children["split"] = [node1, node2, node3, node4]

    def update(self):
        """
        Update based on the player position
        """
        if "split" in self.children:
            children = self.children["split"]
            for child in children:
                child.update()

        # Get the player's distance from the center of the node
        player = self.game.player
        position = self.position
        player_pos = [-player.position[0], -player.position[1], -player.position[2]]
        distance = math.dist(player_pos, position) * self.level * 2
        size = self.size * self.level
        # If the player is within the node's size * 2, split the node
        if distance < size and "split" not in self.children:
            self.generate_split()
        elif distance > size and "unified" not in self.children:
            self.generate_unified()
        
        if distance < size:
            self.state = "split"
        elif distance > size:
            self.state = "unified"
        
        if self.splitchildren_generated and distance < size:
            self.children['unified'].hide()
            for child in self.children["split"]:
                child.show()
        elif self.unifiedchildren_generated and distance > size:
            if "split" in self.children:
                for child in self.children["split"]:
                    child.delete()
                del self.children["split"]
            self.children["unified"].show()
                
        res = None
        for result in self.game.namespace.generated_chunks:
            if result["mesh"] == self.children["unified"].uuid:
                self.game.namespace.generated_chunks.remove(result)
                res = result
        if res:
            self.children["unified"].generated = True
            self.children["unified"].expected_verts = res["expected_verts"]
            self.position = res["average_position"]

    def delete(self):
        """
        Delete the node along with all its children
        """
        for child in self.children.values():
            if type(child) == LeafNode:
                child.delete()
            else:
                for _child in child:
                    _child.delete()
    
    @property 
    def splitchildren_generated(self):
        try:
            values = [
                len(self.game.renderer.storages[child.children["unified"].uuid].vertices)
                >= child.children["unified"].expected_verts
                for child in self.children["split"]
            ]
            return all(values)
        except KeyError: return False
    
    @property
    def unifiedchildren_generated(self):
        if "unified" not in self.children:
            return False
        return self.children['unified'].generated
    
    def show(self):
        if self.state == "split":
            for child in self.children["split"]:
                child.show()
        elif self.state == "unified":
            self.children["unified"].show()
            
    def hide(self):
        try:
            for child in self.children["split"]:
                child.hide()
        except KeyError: pass
        try:
            self.children["unified"].hide()
        except KeyError: pass
        