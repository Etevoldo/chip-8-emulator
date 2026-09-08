from display import Display, DISPLAY_HEIGHT, DISPLAY_WIDTH
from time import sleep

def run():
    display = Display()
    display.run()

def debug_fill_display(dt, display: Display):
    """Fills the screen gradually from bottom to top"""
    if display.j <= 32:
        print(display.i, display.j)
        if (display.i >= DISPLAY_WIDTH):
            display.i = 0
            display.j += 1
        if (display.j >= DISPLAY_HEIGHT):
            display.j = 0
        display.buffer.append((display.i, display.j))
        display.i += 1