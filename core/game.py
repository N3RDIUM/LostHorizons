import multiprocessing

class Game(object):
    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.window.schedule_mainloop(self)
        self.window.schedule_shared_context(self)
        
        self.processes = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.queue.put("Hello world!")
        for i in range(multiprocessing.cpu_count() + 1):
            self.processes.append(multiprocessing.Process(target=self.process, args=(self.namespace,)))
            self.processes[i].start()
        
    def drawcall(self):
        """
        Draw call.
        """
        pass

    def sharedcon(self):
        """
        Shared context.
        """
        pass
    
    @staticmethod
    def process(namespace):
        """
        This function is called to start a multiprocessing process.
        """
        # Get all items from the queue
        queue = namespace.queue
        while not queue.empty():
            print(queue.get())