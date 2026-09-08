import pyglet
import ctypes
import test

pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

SCALE = 10
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
BLACK = 0
WHITE = 255

class Display():

    def __init__(self):
        # used to keep track which bits are on or OFF
        self.display = [False] * (DISPLAY_WIDTH * DISPLAY_HEIGHT)

        # a touple list of x, y values
        # which represent fliped-on bits on the memory buffer
        self.buffer = []

        self.window = pyglet.window.Window()
        display_bytes = (ctypes.c_ubyte * (DISPLAY_WIDTH * DISPLAY_HEIGHT))()
        self.image_data = pyglet.image.ImageData(
            DISPLAY_WIDTH,
            DISPLAY_HEIGHT, 
            "L",
            display_bytes,
            DISPLAY_WIDTH)

        self.window.width = DISPLAY_WIDTH * SCALE
        self.window.height = DISPLAY_HEIGHT * SCALE

        self.i = 0
        self.j = 0
        pyglet.clock.schedule_interval(test.debug_fill_display, 0.001, self)

        # consider calling this on another routine called directly by the CPU
        def on_draw():
            #self.debug_display()
            self.update_pixels()
            self.buffer.clear()
            self.image_data.get_texture()
            sprite = pyglet.sprite.Sprite(self.image_data)
            sprite.scale = SCALE
            sprite.draw()


        def on_mouse_press(x, y, button, mods):
            """Debug only: puts on the buffer clicked location"""
            print(f"mouse pressed on: ({x}, {y})")
            x = int(x // SCALE)
            y = int(y // SCALE)
            self.buffer.append((x, y))

        self.window.on_draw = on_draw
        self.window.on_mouse_press = on_mouse_press

    def update_pixels(self):
        byte_list = self.image_data.get_bytes()

        for x, y in self.buffer:
            index =  x + y * DISPLAY_WIDTH
            if byte_list[index]:
                byte_list[index] = BLACK
            else:
                byte_list[index] = WHITE

        self.image_data.set_bytes("L", DISPLAY_WIDTH, byte_list)

    def debug_display(self, dt):
        """Fills the screen gradually from bottom to top"""
        if (self.i >= DISPLAY_WIDTH):
            self.i = 0
            self.j += 1
        if (self.j >= DISPLAY_HEIGHT):
            self.j = 0
        self.buffer.append((self.i, self.j))
        self.i += 1

    def run(self):
        pyglet.app.run()


if __name__ == "__main__":
    window = Display()
    window.run()