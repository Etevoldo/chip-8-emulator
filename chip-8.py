import app_pyglet
import pyglet
from font import get_font
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
    with open('IBM Logo.ch8', 'rb') as rom:
        read_data = rom.read()

    (buffer, window) = app_pyglet.initialize()
    regs = init_registers()

    buffer.append((1,1))
    buffer.append((2,2))
    buffer.append((2,3))
    get_font(regs.ram)

    # used to keep track which bits are on or OFF
    display = [[False] * window.height] * window.width

    # load data in ram
    i = 0x200
    for byte in read_data:
        regs.ram[i] = byte
        i += 1

    for i in range(0x200, 0x220, 0x2):
        # debug
        # joining bytes for a full 2-byte instruction
        instruc = (regs.ram[i] << 0x8) + (regs.ram[i+1])
        print(f"{instruc:04X}")

    regs.pc = PROGRAM_COUNTER_START

    def FDE(dt):
        nonlocal regs, buffer, display

        # fetch
        # combining bytes for a full 2-byte instruction
        instruc = (regs.ram[regs.pc] << 0x8) + (regs.ram[regs.pc+1])

        # debug
        print(f"\n{instruc:04X}")

        regs.pc += 2

        # decode
        decode(instruc, regs, buffer, display)

    pyglet.clock.schedule_interval(FDE, 0.5)
    pyglet.app.run()

def decode(instruc: int,
           regs: Registers,
           buffer: list[tuple],
           display: list[bool]):
    (x, y, n, kk, nnn) = extract_nibbles(instruc)
    type = instruc & 0xF000

    # ... and execute
    match type:
        case 0x0000:
            print("CLS")
            CLS(display)
        case 0x1000:
            print("1nnn JP addr")
            regs.pc = nnn
        case 0x2000:
            print("2nnn CALL addr")
            regs.stack.push(regs.pc)
            regs.pc = nnn
        case 0x6000:
            print("6xkk - LD Vx, byte")
            regs.v[x] = kk
        case 0x7000:
            print("7xkk - ADD Vx, byte")
            regs.v[x] += kk
        case 0xA000:
            print("ANNN - LD I, addr")
            regs.index = nnn
        case 0xD000:
            print("DXYN - Vx, Vy, nibble")
            DRW(x, y, n, buffer, display, regs)

def DRW(x, y, n, buffer: list, display: list, regs: Registers):
    """The behemoth DRAW instruction
    Display n-byte sprite starting at memory location I at (Vx, Vy),
    set VF = collision.
    """
    sprite_index = regs.index
    x_cord = regs.v[x]
    y_cord = regs.v[y]
    for byte_n in range(n):
        mask = 0b1000_0000
        for bit in range(8):
            x_cord = x_cord % app_pyglet.DISPLAY_WIDTH
            y_cord = y_cord % app_pyglet.DISPLAY_HEIGHT

            line_copy = regs.ram[sprite_index + byte_n]
            is_bit_on = line_copy & mask

            draw_bit(is_bit_on, buffer, display, x_cord, y_cord, regs)

            mask = mask >> 1
            x_cord += 1
        x_cord -= 8
        y_cord += 1

def draw_bit(is_bit_on, buffer, display, x_cord, y_cord, regs):
    if is_bit_on > 0:
        buffer.append((x_cord, y_cord))
        if display[x_cord][y_cord]:
            regs.v[0xF] = 1
            display[x_cord][y_cord] = False
        else:
            regs.v[0xF] = 0
            display[x_cord][y_cord] = True


def CLS(display: list[bool]):
    app_pyglet.clear_screen()
    display = [False for _ in range(len(display))]

def extract_nibbles(instruc):
    x   = (instruc & 0x0F00) >> 8
    y   = (instruc & 0x00F0) >> 4
    n   = (instruc & 0x000F)
    kk  = (instruc & 0x00FF)
    nnn = (instruc & 0x0FFF)
    return (x, y, n, kk, nnn)

RAM_LENGTH = 2048
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