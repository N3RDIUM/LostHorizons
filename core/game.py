import math
import multiprocessing

from core.renderer import Renderer
from core.util import normalize
from camera.player import Player
from planets.tesselate import tesselate_partial
from planets.planet import Planet

import noise

from camera.player import Player
from core.renderer import Renderer
from core.util import normalize
from planets.leafnode import LeafNode
from planets.planet import DummyPlanet
from planets.tesselate import tesselate_partial


class Game(object):

    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.renderer = Renderer()
        self.player = Player()

        self.processes = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.storages = self.renderer.storages
        self.namespace.killed = False
        self.process_count = multiprocessing.cpu_count()
        for i in range(self.process_count):
            self.processes.append(
                multiprocessing.Process(target=self.process,
                                        args=(self.namespace, )))
            self.processes[i].start()
            
        self.planet = Planet(
            renderer=self.renderer,
            game=self,
        )
        
        self.window.schedule_mainloop(self)
        self.window.schedule_shared_context(self)

    def addToQueue(self, item):
        """
        Add an item to the queue.
        """
        self.namespace.queue.put(item)

    @staticmethod
    def process(namespace):
        """
        This function is called to start a multiprocessing process.
        """
        import glfw

        glfw.init()

        # Get all items from the queue
        queue = namespace.queue
        while not namespace.killed:
            if not queue.empty():
                item = queue.get()
                Game.handleQueueItem(item, namespace)

        if namespace.killed:
            glfw.terminate()

    @staticmethod
    def handleQueueItem(item, namespace):
        """
        Handle a queue item.
        """
        if item["task"] == "generate_leafnode":
            # Tesselate
            quad = tuple(item["quad"])
            newquad = []
            for i in range(len(quad)):
                newquad.append(tuple(quad[i]))
            quad = tuple(newquad)
            segments = item["segments"]
            _new_verts = tesselate_partial(quad, segments, item["denominator"],
                                           item["numerator"])
            for i in range(len(_new_verts)):
                _new_verts[i] = (
                    _new_verts[i][0] * segments,
                    item["planet_radius"] + item["planet_center"][1],
                    _new_verts[i][2] * segments,
                )

            # Spherify
            CENTER = item["planet_center"]
            RADIUS = item["planet_radius"]
            for i in range(len(_new_verts)):
                v = _new_verts[i]
                x = v[0] - CENTER[0]
                y = v[1] - CENTER[1]
                z = v[2] - CENTER[2]

                length = math.sqrt(x**2 + y**2 + z**2)

                x = x / length * RADIUS
                y = y / length * RADIUS
                z = z / length * RADIUS

                # Add noise
                vector = [x, y, z]
                vector = normalize(vector)
                _noise = 1 # No noise for now
                
                x = x + vector[0] * _noise
                y = y + vector[1] * _noise
                z = z + vector[2] * _noise

                _new_verts[i] = [x, y, z]

            # Color calculations based on perlin noise in that area
            colors = []
            for i in range(len(_new_verts)):
                x = _new_verts[i][0]
                y = _new_verts[i][1]
                z = _new_verts[i][2]
                colors.extend((
                    abs(
                        noise.pnoise3(x / 10 + 8, y / 10 + 8, z / 10 + 8) / 4 *
                        3 + 0.25),
                    abs(
                        noise.pnoise3(x / 10 + 16, y / 10 + 16, z / 10 + 16) /
                        4 * 3 + 0.25),
                    abs(
                        noise.pnoise3(x / 10 + 32, y / 10 + 32, z / 10 + 32) /
                        4 * 3 + 0.25),
                ))
                
            # Get the average position (center) of the vertices
            center = [0, 0, 0]
            for i in range(len(_new_verts)):
                center[0] += _new_verts[i][0]
                center[1] += _new_verts[i][1]
                center[2] += _new_verts[i][2]
            center[0] /= len(_new_verts)
            center[1] /= len(_new_verts)
            center[2] /= len(_new_verts)
                
            verts_1d = [item for sublist in _new_verts for item in sublist]
            namespace.storages[item["mesh"]].vertices.extend(verts_1d)
            namespace.storages[item["mesh"]].colors.extend(colors)

    def terminate(self):
        """
        Terminate all processes.
        """
        self.namespace.killed = True
        for process in self.processes:
            process.join()
        for process in self.processes:
            process.terminate()

    def drawcall(self):
        """
        Draw call.
        """
        self.player.update(self.window.window)
        self.planet.draw()

    def sharedcon(self):
        """
        Shared context.
        """
        while not self.namespace.killed:
            self.renderer.update()
