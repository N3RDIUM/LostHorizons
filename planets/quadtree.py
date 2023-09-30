import math
from uuid import uuid4


def midpoint(v1, v2):
    x = (v1[0] + v2[0]) / 2
    y = (v1[1] + v2[1]) / 2
    z = (v1[2] + v2[2]) / 2

    return [x, y, z]


class LeafNode(object):

    def __init__(self,
                 quad,
                 segments=32,
                 parent=None,
                 planet=None,
                 renderer=None,
                 game=None):
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

    def generate(self):
        """
        Schedule the generation of this chunk using multiprocessing.
        """
        self.mesh = self.renderer.create_storage(self.uuid)
        self.game.addToQueue({
            "task": "tesselate_full",  # NOT partial
            "mesh": self.uuid,
            "quad": self.quad,
            "segments": self.segments,
            "denominator": 8,
            "planet_center": self.planet.center,
            "planet_radius": self.planet.radius,
        })

    def delete(self):
        """
        Delete this chunk.
        """
        self.renderer.delete_later(self.uuid)

    def show(self):
        self.renderer.show(self.uuid)

    def hide(self):
        self.renderer.hide(self.uuid)


class Node(object):

    def __init__(self,
                 quad,
                 parent=None,
                 planet=None,
                 renderer=None,
                 game=None):
        """
        My go at a QuadTree node implementation.
        """
        self.quad = quad
        self.parent = parent
        self.planet = planet
        self.renderer = renderer
        self.game = game
        self.id = str(uuid4())

        self.position = [
            (self.quad[0][0] + self.quad[1][0] + self.quad[2][0] +
             self.quad[3][0]) / 4,
            (self.quad[0][1] + self.quad[1][1] + self.quad[2][1] +
             self.quad[3][1]) / 4,
            (self.quad[0][2] + self.quad[1][2] + self.quad[2][2] +
             self.quad[3][2]) / 4,
        ]
        self.size = (math.dist(self.quad[0], self.position) +
                     math.dist(self.quad[1], self.position) +
                     math.dist(self.quad[2], self.position) +
                     math.dist(self.quad[3], self.position))

        self.children = {}
        self.cached_leaf = None
        self.generate_unified()

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
            self.children[
                "unified"] = new  # Indexes: "unified": unified node and "split": [array of 4 nodes]
            self.cached_leaf = new
        else:
            self.children["unified"] = self.cached_leaf

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
        )
        node2 = Node(
            quad=quad2,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game,
        )
        node3 = Node(
            quad=quad3,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game,
        )
        node4 = Node(
            quad=quad4,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game,
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

        if self.children_generated:
            # Get the player's distance from the center of the node
            player = self.game.player
            position = self.position
            player_pos = [
                -player.position[0], -player.position[1], -player.position[2]
            ]
            distance = math.dist(player_pos, position)
            # If the player is within the node's size * 2, split the node
            if distance < self.size and "split" not in self.children:
                self.generate_split()
            elif distance > self.size and "split" in self.children:
                self.generate_unified()
                for child in self.children["split"]:
                    child.delete()
                del self.children["split"]

        res = None
        for result in self.game.namespace.generated_chunks:
            if result["mesh"] == self.children["unified"].uuid:
                self.game.namespace.generated_chunks.remove(result)
                res = result
        if res:
            self.children["unified"].generated = True
            self.position = res["average_position"]

        try:
            if "split" in self.children and self.children_generated:
                self.children["unified"].hide()
            else:
                self.children["unified"].show()
        except KeyError:
            pass

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
    def children_generated(self):
        """Get if all children were generated"""
        ret = self.children["unified"].generated
        if not ret:
            return False
        else:
            if "split" not in self.children:
                return True
            for child in self.children["split"]:
                if not child.children["unified"].generated:
                    return False
            return True
