import app_pyglet
import pyglet
from dataclasses import dataclass 

def run():
    (buffer, display, window) = app_pyglet.initialize()
    regs = init_registers()
    pyglet.app.run()

@dataclass
class Registers:
    memory: list[int]
    pc: int
    reg_i: int
    stack: list[int]
    delay_timer: int
    sound_timer: int
    v: list[int]

def init_registers():
    return Registers(
        memory = [],
        pc = 0,
        reg_i = 0,
        stack = [],
        delay_timer = 0,
        sound_timer = 0,
        v = [])

if __name__ == "__main__":
    run()