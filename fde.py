import ch8window
import random
from chip8 import Registers
from ch8window import Chip8Window
import font
import random

def FDE(regs: Registers, ch8_display: Chip8Window):
    """Fetch, Decode, and Execute"""
    #if ch8_display.display_wait: return

    # fetch
    # combining bytes for a full 2-byte instruction
    instruc = (regs.ram[regs.pc] << 0x8) + (regs.ram[regs.pc+1])

    # debug
    #print(f"\n{instruc:04X}")

    regs.pc += 2

    # decode
    decode(instruc, regs, ch8_display)

def decode(instruc: int,
           regs: Registers,
           ch8_display: Chip8Window):
    (x, y, n, kk, nnn) = extract_nibbles(instruc)

    type = instruc & 0xF000
    # for 8VX_ instructions
    logical_type = instruc & 0x000F
    # for E000 and F000
    other_types = instruc & 0x00FF

    # ... and execute
    match type:
        case 0x0000:
            if other_types == 0x00E0:
                ch8_display.clear_screen()
            elif other_types == 0x00EE:
                address = regs.stack.pop()
                regs.pc = address
            else:
                print("not an instruction")
        case 0x1000:
            regs.pc = nnn
        case 0x2000:
            regs.stack.append(regs.pc)
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
            regs.v[x] = kk
        case 0x7000:
            regs.v[x] += kk
            regs.v[x] = regs.v[x] & 0x00FF
        case 0x8000:
            op_8XY(regs, logical_type, x, y)
        case 0x9000:
            if regs.v[x] != regs.v[y]:
                regs.pc += 2
        case 0xA000:
            regs.index = nnn
        case 0xB000:
            regs.pc = regs.v[0x0] + nnn
        case 0xC000:
            regs.v[x] = kk & int(random.random() * 0xFFFF)
        case 0xD000:
            ch8_display.display_wait = True
            DXYN(x, y, n, ch8_display, regs)
        case 0xE000:
            if other_types == 0x009E:
                key = regs.v[x] & 0x000F
                regs.pc += 2 if ch8_display.keys_pressed[key] else 0
            elif other_types == 0x00A1:
                key = regs.v[x] & 0x000F
                regs.pc += 2 if not ch8_display.keys_pressed[key] else 0
        case 0xF000:
            op_FX(x, regs, other_types, ch8_display)
        case _:
            pass


def op_FX(x, regs: Registers, types: int, ch8_display: Chip8Window):
    match types:
        case 0x0007:
            regs.v[x] = regs.delay_timer
        case 0x000A:
            if ch8_display.last_key_released:
                regs.v[x] = ch8_display.last_key_released
            else:
                regs.pc -= 2
        case 0x0015:
            regs.delay_timer = regs.v[x]
        case 0x0018:
            regs.sound_timer = regs.v[x]
        case 0x001E:
            regs.index += regs.v[x]
        case 0x0029:
            last_nibble = regs.v[x] & 0x0F
            regs.index = font.FONT_START + (last_nibble * 5)
        case 0x0033:
            number = regs.v[x]
            digits = []
            for _ in range(3):
                digits.append(number % 10)
                number = number // 10

            for j in range(3):
                regs.ram[regs.index + j] = digits[2 - j]
        case 0x0055:
            for j in range(x+1):
                regs.ram[regs.index + j] = regs.v[j]
            regs.index += x + 1
        case 0x0065:
            for j in range(x+1):
                regs.v[j] = regs.ram[regs.index + j]
            regs.index += x + 1


def op_8XY(regs: Registers, type, x, y):
    v = regs.v
    match type:
        case 0x0000:
            v[x] = v[y]
        case 0x0001:
            v[x] = v[x] | v[y]
            v[0xF] = 0
        case 0x0002:
            v[x] = v[x] & v[y]
            v[0xF] = 0
        case 0x0003:
            v[x] = v[x] ^ v[y]
            v[0xF] = 0
        case 0x0004:
            x_plus_y = regs.v[x] + regs.v[y]
            if x_plus_y > 2**8 - 1:
                v[x] = x_plus_y - 2**8
            else:
                v[x] = x_plus_y

            v[0xF] = 1 if x_plus_y > 0x00FF else 0
        case 0x0005:
            vx = v[x]
            vy = v[y]
            v[x] = vx - vy
            if vx >= vy:
                v[0xF] = 1
            else:
                # underflowing the result
                v[x] += 2**8
                v[0xF] = 0
        case 0x0006:
            # Ambiguous one
            # v[x] = v[y] # comment for SUPER-CHIP/CHIP-48
            vx = v[x]
            v[x] = (v[x] >> 1) & 0b1111_1111
            v[0xF] = 1 if (vx & 0b0000_0001) > 0 else 0
        case 0x0007:
            vx = v[x]
            vy = v[y]
            v[x] = vy - vx
            if vy >= vx:
                v[0xF] = 1
            else:
                # underflowing the result
                v[x] += 2**8

                v[0xF] = 0
        case 0x000E:
            v[x] = v[y]
            vx = v[x]
            # masking and setting the value to avoid values bigger than a byte
            v[x] = (v[x] << 1) & 0b1111_1111

            v[0xF] = 1 if (vx & 0b1000_0000) > 0 else 0


def DXYN(x, y, n, ch8_display: Chip8Window, regs: Registers):
    """The behemoth DRAW instruction
    Display n-byte sprite starting at memory location I at (Vx, Vy),
    set VF = collision.  """
    sprite_index = regs.index
    x_anchor = regs.v[x] % ch8window.DISPLAY_WIDTH
    y_anchor = regs.v[y] % ch8window.DISPLAY_HEIGHT
    regs.v[0xF] = 0

    # wrap around starting positions
    x = x_anchor
    y = y_anchor

    for byte_n in range(n):
        x = x_anchor
        mask = 0b1000_0000
        line_copy = regs.ram[sprite_index + byte_n]
        for _ in range(8):
            is_bit_on = line_copy & mask
            is_collision = ch8_display.draw_pixel(is_bit_on, x, y)
            if is_collision:
                regs.v[0xF] = 1

            mask = mask >> 1
            x += 1
            # clip if cordinate is out of screen
            if x >= ch8window.DISPLAY_WIDTH:
                break
        y += 1
        # clip if cordinate is out of screen
        if y >= ch8window.DISPLAY_HEIGHT:
            break

    ch8_display.update_pixels()
    ch8_display.buffer.clear()

def extract_nibbles(instruc):
    x   = (instruc & 0x0F00) >> 8
    y   = (instruc & 0x00F0) >> 4
    n   = (instruc & 0x000F)
    kk  = (instruc & 0x00FF)
    nnn = (instruc & 0x0FFF)
    return (x, y, n, kk, nnn)