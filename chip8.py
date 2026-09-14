import pyglet
import font
import sys
from ch8window import Chip8Window
import fde
from dataclasses import dataclass 

PROGRAM_COUNTER_START = 0x200

@dataclass
class Registers:
    ram: list[int]
    pc: int
    index: int
    stack: list[int]
    delay_timer: int
    sound_timer: int
    v: list[int]

def run():
    read_data = None
    rom_name = None
    if len(sys.argv) <= 1:
        print("Missing rom file argument")
        return
    rom_name = sys.argv[1]

    with open(rom_name, 'rb') as rom:
        read_data = rom.read()

    ch8_display = Chip8Window()
    regs = init_registers()

    font.get_font(regs.ram)

    # load data in ram
    i = PROGRAM_COUNTER_START
    for byte in read_data:
        regs.ram[i] = byte
        i += 1

    buzz = pyglet.media.synthesis.Triangle(1/20)

    regs.pc = PROGRAM_COUNTER_START

    #regs.ram[0x1FF] = 1

    pyglet.clock.schedule_interval(main_loop, 1/60, regs, ch8_display, buzz)
    pyglet.app.run()

IPF = 15

def main_loop(dt, regs: Registers, ch8_display: Chip8Window, buzz):
    if regs.sound_timer:
        buzz.play()
    regs.delay_timer -= 1 if regs.delay_timer > 0 else 0
    regs.sound_timer -= 1 if regs.sound_timer > 0 else 0

    for _ in range(IPF):
        fde.FDE(regs, ch8_display)

    ch8_display.refresh()
    ch8_display.buffer.clear()


RAM_LENGTH = 4096
V_REGISTERS_NUMBER = 16
STACK_LENGTH = 16

def init_registers():
    return Registers(
        ram = [0 for _ in range(RAM_LENGTH)],
        pc = 0,
        index = 0,
        stack = [0] * STACK_LENGTH,
        delay_timer = 0,
        sound_timer = 0,
        v = [0] * V_REGISTERS_NUMBER)

if __name__ == "__main__":
    run()