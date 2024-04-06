# Imports
from core.renderer import Renderer
from core.window import Window

# Initialization
window = Window()
renderer = Renderer()
render_task = window.draw_queue.add(renderer, "draw")

# Driver code
if __name__ == "__main__":
    window.mainloop()
