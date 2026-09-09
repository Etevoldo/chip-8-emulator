import pyglet
import ctypes
import test

pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

SCALE = 20
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
BLACK_BYTE = 0
WHITE_BYTE = 255
# pseudo preprocessor definitions
debug_grid = True
DEBUG_REFRESH = True

display = None
buffer = None
window = None
image_data = None

def initialize():
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

    if DEBUG_REFRESH:
        pyglet.clock.schedule_interval(
            debug_fill_display, 1/240, buffer)

    return (buffer, display, window)

def attach_handlers(window):
    """joins all the handlers in their respective windows"""
    window.on_draw = on_draw
    window.on_mouse_press = on_mouse_press
    window.on_key_press = on_key_press
    window.on_key_release = on_key_release

def on_draw():
    global display, buffer, window, image_data
    window.clear()
    update_pixels(image_data)
    buffer.clear()
    image_data.get_texture()
    sprite = pyglet.sprite.Sprite(image_data)
    sprite.scale = SCALE
    sprite.draw()
    if debug_grid:
        draw_grid()

def on_mouse_press(x, y, button, mods):
    """Debug only: puts on the buffer clicked location"""
    global buffer
    print(f"mouse pressed on: ({x}, {y})")
    x = int(x // SCALE)
    y = int(y // SCALE)

    # pyglet vertical axis starts on bottom converting to start on top
    y = DISPLAY_HEIGHT - y - 1

    buffer.append((x, y))

def on_key_press(symbol, modifiers):
    print("pressed:", symbol)
    global debug_grid

    if symbol == pyglet.window.key.G and debug_grid:
        debug_grid = False
    else: 
        debug_grid = True

def on_key_release(symbol, modifiers):
    pass

def update_pixels(image_data):
    byte_list = image_data.get_bytes()

    for x, y in buffer:
        # pyglet vertical axis starts on bottom,
        # converting to start on top.
        y = DISPLAY_HEIGHT - y - 1

        index =  x + y * DISPLAY_WIDTH
        #TODO remember to set one of the registers flag later
        if byte_list[index]:
            byte_list[index] = BLACK_BYTE
        else:
            byte_list[index] = WHITE_BYTE

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

def draw_grid():
    """draw grid for easier debugging the display"""
    batch = pyglet.graphics.Batch()
    lines = []
    for i in range(DISPLAY_WIDTH):
        line = pyglet.shapes.Line(
            x = i * SCALE + SCALE,
            y = 0,
            x2 = i * SCALE + SCALE,
            y2 = DISPLAY_HEIGHT * SCALE - 1,
            color = (128, 128, 128),
            thickness=1,
            batch=batch
            )
        lines.append(line)
    for i in range(DISPLAY_HEIGHT):
        line = pyglet.shapes.Line(
            x = 0,
            y = i * SCALE + SCALE,
            x2 = DISPLAY_WIDTH * SCALE,
            y2 = i * SCALE + SCALE,
            color = (128, 128, 128),
            thickness=1,
            batch=batch
            )
        lines.append(line)
    batch.draw()


if __name__ == "__main__":
    print("wrong module")