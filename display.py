import pyglet
import ctypes
import test

pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

SCALE = 10
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
BLACK = 0
WHITE = 255

display = None
buffer = None
window = None
image_data = None

def init_pyglet():
    """initializes globals and returns (buffer, window)
    for further manipulation
    """
    global display, buffer, window, image_data
    # used to keep track which bits are on or OFF
    display = [False] * (DISPLAY_WIDTH * DISPLAY_HEIGHT)

    # a touple list of x, y values
    # which represent fliped-on bits on the memory buffer
    buffer = []

    window = pyglet.window.Window(
        width=DISPLAY_WIDTH * SCALE, height=DISPLAY_HEIGHT * SCALE)

    image_data = pyglet.image.ImageData(
        DISPLAY_WIDTH,
        DISPLAY_HEIGHT, 
        "L",
        (ctypes.c_ubyte * (DISPLAY_WIDTH * DISPLAY_HEIGHT))(),
        DISPLAY_WIDTH)

    attach_handlers(window)

    pyglet.clock.schedule_interval(
        debug_fill_display, 1/240, buffer)

    return (buffer, window)

def attach_handlers(window):
    window.on_draw = on_draw
    window.on_mouse_press = on_mouse_press
    window.on_key_press = on_key_press
    window.on_key_release = on_key_release

def on_draw():
    global display, buffer, window, image_data
    update_pixels(image_data)
    buffer.clear()
    image_data.get_texture()
    sprite = pyglet.sprite.Sprite(image_data)
    sprite.scale = SCALE
    sprite.draw()

def on_mouse_press(x, y, button, mods):
    """Debug only: puts on the buffer clicked location"""
    global buffer
    print(f"mouse pressed on: ({x}, {y})")
    x = int(x // SCALE)
    y = int(y // SCALE)
    buffer.append((x, y))

def on_key_press(symbol, modifiers):
    pass

def on_key_release(symbol, modifiers):
    pass

def update_pixels(image_data):
    byte_list = image_data.get_bytes()

    for x, y in buffer:
        index =  x + y * DISPLAY_WIDTH
        #TODO remember to set one of the registers flag later
        if byte_list[index]:
            byte_list[index] = BLACK
        else:
            byte_list[index] = WHITE

    image_data.set_bytes("L", DISPLAY_WIDTH, byte_list)

i = 0
j = 0
def debug_fill_display(dt, buffer):
    global i, j
    """Fills the screen gradually from bottom to top"""
    if (i >= DISPLAY_WIDTH):
        i = 0
        j += 1
    if (j >= DISPLAY_HEIGHT):
        j = 0
    buffer.append((i, j))
    i += 1


if __name__ == "__main__":
    print("wrong module")