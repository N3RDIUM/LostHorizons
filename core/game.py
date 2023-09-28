import json
import multiprocessing

import filelock
import noise

from camera.player import Player
from core.renderer import Renderer
from planets.tesselate import tesselate_partial


class Game(object):

    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.renderer = Renderer(self)
        self.player = Player()

        self.processes = []
        self.result_queue = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.killed = False
        self.process_count = multiprocessing.cpu_count()
        for i in range(self.process_count):
            self.processes.append(
                multiprocessing.Process(target=self.process,
                                        args=(self.namespace, )))
            self.processes[i].start()

        for i in range(len(self.processes)):
            self.addToQueue({
                "task":
                "tesselate",
                "mesh":
                "default",
                "quad": [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)],
                "segments":
                128,
                "denominator":
                len(self.processes),
                "numerator":
                i,
            })

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
        if item["task"] == "tesselate":
            # Vertex calculations
            quad = tuple(item["quad"])
            segments = item["segments"]
            _new_verts = tesselate_partial(quad, segments, item["denominator"],
                                           item["numerator"])
            for i in range(len(_new_verts)):
                _new_verts[i] = (
                    _new_verts[i][0] * segments,
                    _new_verts[i][1] +
                    noise.pnoise3(_new_verts[i][0], _new_verts[i][1],
                                  _new_verts[i][2]) * 10,
                    _new_verts[i][2] * segments,
                )
            verts_1d = [item for sublist in _new_verts for item in sublist]
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
            # save to JSON
            file = f".datatrans/default-{item['numerator']}.json"
            with filelock.FileLock(file + ".lock"):
                with open(file, "w") as f:
                    json.dump(
                        {
                            "vertices": list(verts_1d).copy(),
                            "colors": list(colors).copy(),
                        },
                        f,
                    )
            namespace.result_queue.put({
                "type": "buffer_mod",
                "mesh": "default",
                "numerator": item["numerator"],
                "denominator": item["denominator"],
                "datafile": file,
            })

    def terminate(self):
        """
        Terminate all processes.
        """
        self.namespace.killed = True
        for process in self.processes:
            process.terminate()

    def drawcall(self):
        """
        Draw call.
        """
        self.player.update(self.window.window)
        self.renderer.draw()

    def sharedcon(self):
        """
        Shared context.
        """
        while not self.namespace.killed:
            self.result_queue.append(self.namespace.result_queue.get())
            self.renderer.update()
