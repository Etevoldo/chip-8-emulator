import ch8window
import pyglet
from ch8window import Chip8Window
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
    with open('./roms/1-chip8-logo.ch8', 'rb') as rom:
        read_data = rom.read()

    ch8_display = Chip8Window()
    regs = init_registers()

    get_font(regs.ram)

    # load data in ram
    i = PROGRAM_COUNTER_START
    for byte in read_data:
        regs.ram[i] = byte
        i += 1

    regs.pc = PROGRAM_COUNTER_START

    def FDE(dt):
        """Fetch, Decode, and Execute"""
        nonlocal regs, ch8_display

        # fetch
        # combining bytes for a full 2-byte instruction
        instruc = (regs.ram[regs.pc] << 0x8) + (regs.ram[regs.pc+1])

        # debug
        print(f"\n{instruc:04X}")

        regs.pc += 2

        # decode
        decode(instruc, regs, ch8_display)

    pyglet.clock.schedule_interval(FDE, 0.1)
    pyglet.app.run()

def decode(instruc: int,
           regs: Registers,
           ch8_display: Chip8Window):
    (x, y, n, kk, nnn) = extract_nibbles(instruc)
    type = instruc & 0xF000
    # for 8VX_ instructions
    logical_type = instruc & 0x000F

    # ... and execute
    match type:
        case 0x0000:
            print("CLS")
            CLS(ch8_display)
        case 0x1000:
            print("1nnn - JP addr")
            regs.pc = nnn
        case 0x2000:
            print("2nnn - CALL addr")
            regs.stack.push(regs.pc)
            regs.pc = nnn
        case 0x3000:
            if regs.v[x] == kk:
                regs.pc += 2
        case 0x4000:
            if regs.v[x] != kk:
                regs.pc += 2
        case 0x5000:
            if regs.v[x] == regs.v[y]:
                regs.pc += 2
        case 0x6000:
            print("6XKK - LD Vx, byte")
            regs.v[x] = kk
        case 0x7000:
            print("7XKK - ADD Vx, byte")
            regs.v[x] += kk
        case 0x8000:
            logical_instructions(regs, logical_type, x, y)
        case 0xA000:
            print("ANNN - LD I, addr")
            regs.index = nnn
        case 0xD000:
            print("DXYN - Vx, Vy, nibble")
            DRW(x, y, n, ch8_display, regs)

def logical_instructions(regs, type, x, y):
    v = regs.v
    match type:
        case 0x0000:
            print("8xy0 - LD Vx, Vy")
            v[x] = v[y]
        case 0x0001:
            print("8xy1 - OR Vx, Vy")
            v[x] = v[x] | v[y]
        case 0x0002:
            print("8xy2 - AND Vx, Vy")
            v[x] = v[x] & v[y]
        case 0x0003:
            print("8xy3 - XOR Vx, Vy")
            v[x] = v[x] ^ v[y]
        case 0x0004:
            print("8xy4 - ADD Vx, Vy")
            x_plus_y = v[x] + v[y]
            v[x] = x_plus_y & 0x00FF

            v[0xF] = 1 if x_plus_y > 0x00FF else 0
        case 0x0005:
            print("8xy5 - SUB Vx, Vy")
            v[x] = v[x] - v[y]

            v[0xF] = 1 if v[x] >= v[y] else 0
        case 0x0006:
            print("SHR Vx {, Vy}")
            v[x] = v[y]
            v[0xF] = 1 if (v[x] & 0b0000_0001) > 0 else 0
            v[x] = v[x] >> 1
        case 0x0007:
            print("SUBN Vx, Vy")
            v[x] = v[x] - v[y]

            v[0xF] = 0 if v[x] >= v[y] else 1
        case 0x000E:
            print("SHL Vx {, Vy}")
            v[x] = v[y]
            v[0xF] = 1 if (v[x] & 0b1000_0000) > 0 else 0
            v[x] = v[x] << 1




def DRW(x, y, n, ch8_display, regs: Registers):
    """The behemoth DRAW instruction
    Display n-byte sprite starting at memory location I at (Vx, Vy),
    set VF = collision.
    """
    sprite_index = regs.index
    x_anchor = regs.v[x]
    y_anchor = regs.v[y]

    # wrap around starting positions
    x_cord = x_anchor % ch8window.DISPLAY_WIDTH
    y_cord = y_anchor % ch8window.DISPLAY_HEIGHT

    for byte_n in range(n):
        mask = 0b1000_0000
        for bit in range(8):
            # clip if cordinate is out of screen
            if x_cord > ch8window.DISPLAY_WIDTH:
                continue
            if y_cord > ch8window.DISPLAY_HEIGHT:
                continue

            line_copy = regs.ram[sprite_index + byte_n]
            is_bit_on = line_copy & mask

            regs.v[0xF] = draw_bit(is_bit_on, ch8_display, x_cord, y_cord)

            mask = mask >> 1
            x_cord += 1
        x_cord = x_anchor % ch8window.DISPLAY_WIDTH
        y_cord += 1

def draw_bit(is_bit_on, ch8_display: Chip8Window, x_cord, y_cord):
    """helper function of DRW, handles drawing exactly 1 bit
    also returns 1 or 0 if it erased a pixel or not, respectivelly."""
    buffer = ch8_display.buffer
    is_pixel_on = ch8_display.is_pixel_on

    if is_bit_on > 0:
        buffer.append((x_cord, y_cord))
        if is_pixel_on[x_cord][y_cord]:
            is_pixel_on[x_cord][y_cord] = False
            return 1
        else:
            is_pixel_on[x_cord][y_cord] = True
            return 0


def CLS(ch8_display: Chip8Window):
    ch8_display.clear_screen()

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