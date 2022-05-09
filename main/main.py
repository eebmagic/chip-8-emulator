import time
import os
from random import randint

VERBOSE = True

## SPECIAL REGISTERS

# Set program counter register
PC = 512

# Set index register
I = 512

# Set timer
TIMER = (2 ** 8) - 1
TICK_RATE = 1/60
# TICK_RATE = 1/10
# TICK_RATE = 1/6000

## Registers

registers = [0xff] * 16


## MEMORY

# Build memory
memory = [0xff] * (2 ** 12)

# Set font in memory (from 0x00 to 0xff should be special vars?)
fontStart = 0x050
fontEnd = 0x09F
fontArr = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 6
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 7
    0xF0, 0x10, 0x20, 0x40, 0x40, # 8
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 0
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]
memory[fontStart:fontEnd] = fontArr

# Set display buffer
displayStart = 0xF00
displayEnd = 0xFFF
displayWidth, displayHeight = 64, 32
displayLength = 32 * 64 // 8
memory[displayStart:displayEnd+2] = [0x00] * displayLength


#############
# FUNCTIONS 
#############


def printMemory(display=False, start=0, limit=4096+1, condensed=False):
    '''
    HELPER METHOD
    '''
    start = start // 8
    if not display:
        for i in range(min(limit, len(memory)) // 8):
            first = (start+i)*8
            second = (start+i+1)*8-1
            a = f'{hex(first)}..{hex(second)}' 
            b = f' ' * (12-len(a))
            if condensed:
                print(f'{b}{a} : {"".join([hex(x) for x in memory[first:second+1]]).replace("0x", "")}')
            else:
                print(f'{b}{a} : {[hex(x) for x in memory[first:second+1]]}')
    else:
        for i in range(displayHeight):
            a = f'{hex(displayStart+(i*8))}..{hex(displayStart+((i+1)*8)*(8-1))}'
            b = f' ' * (12-len(a))
            print(f'{b}{a} : {[hex(x) for x in memory[displayStart+(i*8):displayStart+((i+1)*8)]]}')

def getDisplayArray():
    out = []
    for i in range(displayHeight):
        # a = f'{hex(displayStart+(i*8))}..{hex(displayStart+((i+1)*8)*(8-1))}'
        # b = f' ' * (12-len(a))
        # print(f'{b}{a} : {[hex(x) for x in memory[displayStart+(i*8):displayStart+((i+1)*8)]]}')
        out += memory[displayStart+(i*8):displayStart+((i+1)*8)]
    return out

def memoryWrite(address, value):
    '''
    HELPER METHOD
    Perform memory writes.
    '''
    assert address >= 512 and address <= 4096, f'Memory address is {address} and should be 512..4096'
    assert value >= 0 and value <= (2 ** 8), f'Value should be 0..{2**8}'
    global memory, VERBOSE
    if VERBOSE:
        print(f'Running memoryWrite, with address: {address} and value: {value}')

    memory[address] = value

def displayShow():
    '''
    HELPER METHOD
    Print screen out.
    '''
    global memory
    empty, full = ' ', '█'
    print('-'*(64+2))
    for y in range(displayHeight):
        row = memory[displayStart+(displayWidth*y//8):displayStart+(displayWidth*(y+1)//8)]
        bits = ''.join(["{:08b}".format(x) for x in row])
        displayRow = bits.replace('0', ' ').replace('1', '█')
        print(f'|{displayRow}|')
    print('-'*(64+2))

def decrementTimer():
    # TODO Do something aobut this one
    global TIMER
    if TIMER > 0:
        TIMER -= 1
    else:
        TIMER = (2 ** 8) - 1

def fetch():
    # TODO Do something about this one
    global PC
    A = memory[PC]
    B = memory[PC + 1]
    print(PC, A, B)
    PC += 2

def jpAddr(nnn):
    '''
    1nnn - JP addr
    Make the program counter jump to the given address
    Arguments:
        nnn
    '''
    global PC, VERBOSE
    if VERBOSE:
        print(f'Running jpAddr. Changing PC from {PC} to {nnn}')
    PC = nnn

def setIndxReg(nnn):
    '''
    Annn - LD I, addr
    Sets I register: I = nnn

    Arguments:
        nnn
    '''
    global I, VERBOSE

    if VERBOSE:
        print(f'Running setIndexReg. Changing I from {I} to {nnn}')
    I = nnn

def setReg(x, kk):
    '''
    6xnn - Set Vx, byte
    Set a given register to a given byte.

    Arguments:
        x: The number for the register (0..15).
        kk: An 8-bit number to add to current register value (should wrap?).
    '''
    assert x >= 0 and x < 16, f'Passed reg {x} when there are only 0..15'
    global registers, VERBOSE
    
    if VERBOSE:
        print(f'Running setReg. Changing register {x} from {registers[x]} to {kk}')
    registers[x] = kk

def addValToReg(x, kk):
    '''
    7xkk - ADD Vx, byte
    Add a given amount to the current register's value.

    Arguments:
        x: The number for the register (0..15).
        kk: An 8-bit number to add to current register value (should wrap?).
    '''
    assert x >= 0 and x < 16, f'Passed reg {x} when there are only 0..15'
    global registers, VERBOSE

    curr = registers[x]
    if VERBOSE:
        print(f'Running addValToReg (+{kk}). Changing register {x} from {registers[x]} to {(curr+kk)%(2**8)}')
    newVal = (curr + kk) % (2**8)
    setReg(x, newVal)

def clearDisplay():
    '''
    00E0 - CLS
    Clear the display.
    '''
    global memory, VERBOSE
    if VERBOSE:
        print(f'Running clearDisplay.')

    memory[displayStart:displayEnd+2] = [0x00] * displayLength

def display(vx, vy, n):
    '''
    DXYN - DRW Vx, Vy, nibble
    Display a sprite.

    Arguments:
        Vx : The number for the register contianing the x-coordinate for the sprite target.
        Vy : The number for the register contianing the y-coordinate for the sprite target.
        n  : The number of bytes after the location at I register location to draw.
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    assert vy >= 0 and vy < 16, f'vy is {vy} and should be 0..15'
    global memory, registers, displayStart, VERBOSE
    global displayEnd, displayLength
    sprite = memory[I:I+n]
    x = registers[vx]
    y = registers[vy]
    if VERBOSE:
        print(f'Running display command:')
        print(f'\tVx is register {vx} with value: {x}')
        print(f'\tVy is register {vy} with value: {y}')
        print(f'\tDisplaying {n} bytes after I: {I}')
        print(f'\tSprite: {[hex(x) for x in sprite]}')

    for i in range(n):
        rowOffset = displayWidth * ((y + i) % displayHeight) // 8
        # colOffset = (x // 8) % (displayWidth // 8)
        colOffset = (x // 8) % (displayWidth // 8)
        index = displayStart + rowOffset + colOffset

        rowByte = memory[I+i]
        A = rowByte >> (x%8)
        B = (rowByte << (8-(x%8))) & 0xFF

        currA = memory[index]
        memory[index] ^= A

        bIndex = displayStart + (index+1)%displayLength
        if (index+1)%8 == 0:
            bIndex -= 8
        currB = memory[bIndex]
        memory[bIndex] ^= B

def setXor(vx, vy):
    '''
    8xy3 - XOR Vx, Vy
    Set Vx = Vx XOR Vy. A bitwise exclusive OR on values of Vx and Vy,
      then store in Vx.
    '''
    global registers, VERBOSE
    if VERBOSE:
        print(f'Running setXor command:')
        print(f'\tRegister x is {vx} with val: {registers[vx]}')
        print(f'\tRegister y is {vy} with val: {registers[vy]}')
        print(f'\tNew value: {registers[vx] ^ registers[vy]}')

    newVal = registers[vx] ^ registers[vy]
    registers[vx] = newVal

def setIndex(nnn):
    '''
    ANNN - LD I, addr
    Set I to the value: nnn
    
    Arguments:
        nnn: The 12-bit value to set I to be
    '''
    assert nnn >= 0 and nnn < 2**12, f'Received nnn: {nnn} but should be 0..{2**12}'
    global I, VERBOSE
    if VERBOSE:
        print(f'Changing I from {I} to {nnn}')

    I = nnn

def jumpOff(nnn):
    '''
    Bnnn - JP V0, addr
    Jump the PC to location nnn + V0

    Arguments:
        nnn: The 12-bit value to add to V0 to add up to target address
    '''
    assert nnn >= 0 and nnn < 2**12, f'Received nnn: {nnn} but should be 0..{2**12-1}'
    global registers, PC, VERBOSE

    newLocation = registers[0] + nnn
    if VERBOSE:
        print(f'Jumping from PC: {PC} to {registers[0]} + {nnn} = {newLocation}')

    PC = newLocation

def random(vx, nn):
    '''
    Cxnn - RND Vx, byte
    Set register x to random byte AND nn.

    Arguments:
        nn: The byte to AND the random value with
    '''
    assert nn >= 0 and nn < 2**8, f'Recieved nn: {nn} but should be 0..{2**8-1}'
    global registers, VERBOSE

    randomVal = randint(0, 2**8-1)
    newVal = randomVal & nn

    if VERBOSE:
        print(f'Changing register {vx} from {registers[vx]} to {newVal} ({bin(randomVal)} & {bin(nn)} = {bin(newVal)})')

    registers[vx] = newVal


#############
# MAIN LOOP
#############

from sys import exit, argv
import pygame
from pygame.locals import *

if __name__ == '__main__':
    # Check for file to load
    args = list(filter(lambda item: item.endswith('.ch8'), argv))
    if len(args) > 0:
        sourceFile = args[0]

        # Place in memory
        with open(sourceFile, 'rb', buffering=4) as file:
            sourceContent = file.read().strip()
            evens = [byte for i, byte in enumerate(sourceContent) if i % 2 == 0 ]
            odds = [byte for i, byte in enumerate(sourceContent) if i % 2 == 1 ]
            joined = list(sum(zip(odds, evens+[0]), ())[:-1])

            if VERBOSE:
                print(f'Loaded program from {sourceFile}')

        for i, byte in enumerate(joined):
            memory[512+i] = byte

        if VERBOSE:
            print('Finished writing to memory')
    else:
        sourceFile = None

    # Setup pygame parts
    pygame.init()

    size = screen_width, screen_height = 600, 400
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    fps_cap = 120
    running = True

    # Main loop
    while running:
        clock.tick(fps_cap)

        # Get keyboard inputs
        for event in pygame.event.get():    # error is here
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        values = {
            'q': keys[K_q],
            'w': keys[K_w],
            'e': keys[K_e],
            'r': keys[K_r],
            'a': keys[K_a],
            's': keys[K_s],
            'd': keys[K_d],
            'f': keys[K_f],
            'z': keys[K_z],
            'x': keys[K_x],
            'c': keys[K_c],
            'v': keys[K_v],
            '1': keys[K_1],
            '2': keys[K_2],
            '3': keys[K_3],
            '4': keys[K_4],
        }
        print(values)

        # Pygame display stuff
        screen.fill((255, 255, 255))
        pygame.display.flip()

        # General code
        time.sleep(TICK_RATE)
        decrementTimer()
        os.system('clear')

        clearDisplay()
        # setReg(0, 0) # x reg is 0
        # setReg(1, 0) # y reg is 1
        setReg(0, (displayWidth-TIMER-8)%displayWidth) # x reg is 0
        setReg(1, (TIMER-5)%displayHeight) # y reg is 1
        # setReg(0, randint(0, displayWidth-1)) # x reg is 0
        # setReg(1, randint(0, displayHeight-1)) # y reg is 1
        # setReg(0, 62) # x reg is 0
        # setReg(1, 0) # y reg is 1

        setIndex(fontStart+50)
        display(0, 1, 5)
        # printMemory(display=True)
        displayShow()


    pygame.quit()
    exit()

    # game_loop()
    #!/usr/bin/env python
