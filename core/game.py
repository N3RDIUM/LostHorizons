class Game(object):
    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.window.schedule_mainloop(self)
        self.window.schedule_shared_context(self)
        
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