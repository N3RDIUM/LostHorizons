import multiprocessing

class Game(object):
    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        
        self.processes = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.killed = False
        for i in range(multiprocessing.cpu_count()):
            self.processes.append(multiprocessing.Process(
                target=self.process, 
                args=(self.namespace), 
                name=f"LostHorizons Worker Process {i}"
            ))
            self.processes[i].start()
        # self.addToQueue({ # Test/Example
        #     "object": "qwertyuiop asdfghjkl zxcvbnm",
        #     "function": "upper",
        # })
        
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
                function = item["object"].__getattribute__(item["function"])
                result = function()
                namespace.result_queue.put(result)
        
        if namespace.killed:
            glfw.terminate()
                
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
        pass

    def sharedcon(self):
        """
        Shared context.
        """
        try:
            while not self.namespace.killed:
                if not self.namespace.result_queue.empty():
                    # print(self.namespace.result_queue.get())
                    pass
        except:
            pass