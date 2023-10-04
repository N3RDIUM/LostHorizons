import json
import math
import multiprocessing
import random
import threading
import time
import uuid

import filelock

from camera.player import Player
from core.fractalnoise import fractal_noise, fractal_ridge_noise
from core.renderer import Renderer
from core.tesselate import tesselate_partial
from planets.planet import LoDPlanet as LoD


class Game(object):

    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.renderer = Renderer(self)
        self.player = Player()
        self.frame = 0

        self.processes = []
        self.result_queue = []
        self.generation_queue = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.generated_chunks = self.manager.list()
        self.namespace.killed = False
        self.process_count = multiprocessing.cpu_count()
        for i in range(self.process_count):
            self.processes.append(
                multiprocessing.Process(target=self.process,
                                        args=(self.namespace, )))
            self.processes[i].start()

        self.lod = LoD(self)
        self.lod.generate()

        self.window.schedule_mainloop(self)
        self.window.schedule_shared_context(self)

        self.thread = threading.Thread(target=self.update_thread)
        self.thread.start()
        self.thread_2 = threading.Thread(target=self.generate_thread)
        self.thread_2.start()

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
        if item["task"] == "tesselate_full":
            t = time.time()
            # Vertex calculations
            quad = tuple(item["quad"])
            segments = item["segments"]
            divisions = item["denominator"]
            CENTER = item["planet_center"]
            RADIUS = item["planet_radius"]
            new_verts = []
            for i in range(divisions):
                new_verts += [tesselate_partial(quad, segments, divisions, i)]
            pos_sum = [0, 0, 0]
            pos_len = 0
            texScale = 1 / 16
            out = []
            color = (random.random() / 4, random.random() / 4,
                     random.random() / 4)
            for _new_verts in new_verts:
                colors = []
                for i in range(len(_new_verts)):
                    # Get the vector from the planet center to the vertex
                    v = _new_verts[i]
                    x = v[0] - CENTER[0]
                    y = v[1] - CENTER[1]
                    z = v[2] - CENTER[2]

                    length = math.sqrt(x**2 + y**2 + z**2)

                    x = x / length * RADIUS
                    y = y / length * RADIUS
                    z = z / length * RADIUS

                    noiseval = fractal_noise((x / 1000, y / 1000, z / 1000),
                                             seed=64,
                                             octaves=16)
                    tex_noiseval = fractal_ridge_noise(
                        (x * texScale, y * texScale, z * texScale),
                        seed=32786,
                        octaves=4,
                    )
                    length = math.sqrt(x**2 + y**2 + z**2) + noiseval * 10

                    x = x / length * RADIUS
                    y = y / length * RADIUS
                    z = z / length * RADIUS

                    _new_verts[i] = (x, y, z)
                    colors.extend(((color[i] + tex_noiseval * 0.5 + 0.25))
                                  for i in range(3))

                verts_1d = [item for sublist in _new_verts for item in sublist]
                file = f".datatrans/{item['mesh']}-{uuid.uuid4()}.json"
                with filelock.FileLock(file + ".lock"):
                    with open(file, "w") as f:
                        json.dump(
                            {
                                "vertices": list(verts_1d).copy(),
                                "colors": list(colors).copy(),
                            },
                            f,
                        )
                out.append({
                    "type": "buffer_mod",
                    "mesh": item["mesh"],
                    "datafile": file
                })
                # Calculate the average position of the vertices
                for vert in _new_verts:
                    pos_sum[0] += vert[0]
                    pos_sum[1] += vert[1]
                    pos_sum[2] += vert[2]
                    pos_len += 1
        for item in out:
            namespace.result_queue.put(item)
        namespace.generated_chunks.append(({
            "mesh":
            item["mesh"],
            "average_position": (
                pos_sum[0] / pos_len,
                pos_sum[1] / pos_len,
                pos_sum[2] / pos_len,
            ),
            "expected_verts":
            pos_len * 2,
            "datafiles":
            out,
        }))

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
        self.renderer.update()
        self.frame += 1

    def sharedcon(self):
        """
        Shared context.
        """
        while not self.namespace.killed:
            self.lod.update()

    def update_thread(self):
        while not self.namespace.killed:
            self.result_queue.append(self.namespace.result_queue.get())

    def generate_thread(self):
        while not self.namespace.killed:
            try:
                self.generation_queue.pop(0).generate()
            except IndexError:
                pass
