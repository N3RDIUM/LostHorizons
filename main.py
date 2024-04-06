# Imports
from core.window import Window
from core.renderer import Renderer

# Initialization
window = Window()
renderer = Renderer()
render_task = window.draw_queue.add(renderer, "draw")

# Driver code
if __name__ == "__main__":
    window.mainloop()
