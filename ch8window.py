import pyglet
import ctypes
from font import map_key

pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

SCALE = 15
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
BLACK_BYTE = 0
WHITE_BYTE = 255
# pseudo preprocessor definitions
DEBUG_REFRESH = False

class Chip8Window(pyglet.window.Window):
    def __init__(self):
        super().__init__(
            width=DISPLAY_WIDTH * SCALE,
            height=DISPLAY_HEIGHT * SCALE)

        # a touple list of x, y values
        # which represent fliped-on bits on the memory buffer
        self.buffer = set()

        # used to keep track which bits are on or OFF
        self.is_pixel_on = [[False] * DISPLAY_HEIGHT] * DISPLAY_WIDTH

        self.batch = pyglet.graphics.Batch()

        self.image_data = pyglet.image.ImageData(
            DISPLAY_WIDTH,
            DISPLAY_HEIGHT,
            "L",
            (ctypes.c_ubyte * (DISPLAY_WIDTH * DISPLAY_HEIGHT))(),
            DISPLAY_WIDTH)

        self.keys_pressed = [False] * 16
        self.last_key_released = None

        self.display_wait = False

        self.debug_grid = False
        if DEBUG_REFRESH:
            self.i = 0
            self.j = 0
            pyglet.clock.schedule_interval(
                self.debug_fill_display, 1/240, self)

    def refresh(self):
        self.display_wait = False
        self.clear()
        self.update_pixels()
        self.last_key_released = None

        sprite = pyglet.sprite.Sprite(self.image_data, batch=self.batch)
        sprite.scale = SCALE

        self.batch.draw()
        if self.debug_grid:
            self.draw_grid()

    def update_pixels(self):
        byte_list = self.image_data.get_bytes()

        for x, y in self.buffer:
            # pyglet vertical axis starts on bottom,
            # converting to start on top.
            y = DISPLAY_HEIGHT - y - 1

            index =  x + y * DISPLAY_WIDTH
            #TODO remember to set one of the registers flag later
            if byte_list[index]:
                byte_list[index] = BLACK_BYTE
            else:
                byte_list[index] = WHITE_BYTE

        self.image_data.set_bytes("L", DISPLAY_WIDTH, byte_list)

    def draw_grid(self):
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
        # necessary to not be garbage-collected
        batch.draw()

    def on_mouse_press(self, x, y, button, mods):
        """Debug only: puts on the buffer clicked location"""
        print(f"mouse pressed on: ({x}, {y})")
        x = int(x // SCALE)
        y = int(y // SCALE)

        # pyglet vertical axis starts on bottom converting to start on top
        y = DISPLAY_HEIGHT - y - 1

        self.buffer.append((x, y))

    def on_key_press(self, symbol, modifiers):
        print("pressed:", symbol)

        key_index = map_key(symbol)
        if key_index or key_index == 0x0:
            self.keys_pressed[key_index] = True

        # debug grid flip switch
        if symbol == pyglet.window.key.G:
            if self.debug_grid:
                self.debug_grid = False
            else: 
                self.debug_grid = True
            return

    def on_key_release(self, symbol, modifiers):
        key_index = map_key(symbol)
        if key_index or key_index == 0x0:
            self.keys_pressed[key_index] = False

        self.last_key_released = key_index

    def clear_screen(self):
        self.is_pixel_on = [[False] * DISPLAY_HEIGHT] * DISPLAY_WIDTH
        empty_bytes = (
            ctypes.c_ubyte * (DISPLAY_WIDTH * DISPLAY_HEIGHT))()
        self.image_data.set_bytes("L", DISPLAY_WIDTH, empty_bytes)

    def debug_fill_display(self, dt):
        """Fills the screen gradually from bottom to top"""
        if (i >= DISPLAY_WIDTH):
            i = 0
            j += 1
        if (j >= DISPLAY_HEIGHT):
            j = 0
        self.buffer.append((i, j))
        i += 1

if __name__ == "__main__":
    print("wrong module")