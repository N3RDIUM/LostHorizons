import math
import multiprocessing
import random
import threading
from multiprocessing import shared_memory

import numba
import numpy as np
from planets.planet import LoDPlanet as LoD

from camera.player import Player
from core.fractalnoise import fractal_noise, fractal_ridge_noise
from core.renderer import Renderer
from core.tesselate import tesselate_partial


class Game:

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
                multiprocessing.Process(target=self.process, args=(self.namespace,))
            )
            self.processes[i].start()

        self.lod = LoD(self)
        self.lod.generate()
        self.player.planet = self.lod

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
        if item["task"] == "tesselate_full":
            item = dict(item.copy())
            quad = tuple(item["quad"])
            segments = item["segments"]
            divisions = item["denominator"]
            CENTER = item["planet_center"]
            RADIUS = item["planet_radius"]
            level = item["level"]
            new_verts = [
                tesselate_partial(quad, segments, divisions, i)
                for i in range(divisions)
            ]
            pos_sum = [0, 0, 0]
            pos_len = 0
            texScale = 1 / 64
            color = [0.25 * abs(random.random()) for i in range(3)]
            color = tuple(color)

            vertices = []
            colors = []

            for x in numba.prange(len(new_verts)):
                _new_verts = new_verts[x]
                for i in numba.prange(len(_new_verts)):
                    v = _new_verts[i]
                    x, y, z = [v[j] - CENTER[j] for j in range(3)]
                    length = math.sqrt(x**2 + y**2 + z**2)
                    x, y, z = [
                        x / length * RADIUS,
                        y / length * RADIUS,
                        z / length * RADIUS,
                    ]
                    noiseval = (
                        fractal_noise(
                            (x / RADIUS, y / RADIUS, z / RADIUS), seed=64, octaves=4
                        )
                        * 16
                    )
                    length = (
                        math.sqrt(x**2 + y**2 + z**2) + noiseval * 10 - level / 1000
                    )
                    x, y, z = [
                        x / length * RADIUS,
                        y / length * RADIUS,
                        z / length * RADIUS,
                    ]
                    _new_verts[i] = (x, y, z)

                    tex_noiseval = (
                        fractal_ridge_noise(
                            (x * texScale, y * texScale, z * texScale),
                            seed=32786,
                            octaves=4,
                        )
                        / 2
                        - noiseval / 32
                    )
                    colors.extend(
                        (color[j] + tex_noiseval * 0.5 + 0.25) for j in range(3)
                    )

                verts_1d = [item for sublist in _new_verts for item in sublist]
                vertices.extend(verts_1d)

                for vert in _new_verts:
                    pos_sum = [pos_sum[j] + vert[j] for j in range(3)]
                    pos_len += 1

            try:
                vtx_shared_memory = shared_memory.SharedMemory(
                    name=f"buffer-{str(item['mesh'])}-vertices"
                )
                clr_shared_memory = shared_memory.SharedMemory(
                    name=f"buffer-{str(item['mesh'])}-colors"
                )

                vtx_data = np.asarray(vertices, dtype=np.float32)
                clr_data = np.asarray(colors, dtype=np.float32)

                vtx = np.ndarray(
                    vtx_data.shape, dtype=vtx_data.dtype, buffer=vtx_shared_memory.buf
                )
                clr = np.ndarray(
                    clr_data.shape, dtype=clr_data.dtype, buffer=clr_shared_memory.buf
                )

                vtx[:] = vtx_data[:]
                clr[:] = clr_data[:]

                namespace.result_queue.put(
                    {
                        "type": "buffer_mod",
                        "mesh": item["mesh"],
                        "shape": {"vtx": vtx.shape, "clr": clr.shape},
                    }
                )
            except:
                pass

            namespace.generated_chunks.append(
                {
                    "mesh": item["mesh"],
                    "average_position": tuple(pos_sum[j] / pos_len for j in range(3)),
                    "expected_verts": pos_len * 2,
                }
            )

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
