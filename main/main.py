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
TIMER = (2**8) - 1
SOUND_TIMER = (2**8) - 1
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
    assert address >= 512 and address < 4096, f'Memory address is {address} and should be 512..4096'
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

    ## Build data array
    data = []
    for y in range(displayHeight):
        row = memory[displayStart+(displayWidth*y//8):displayStart+(displayWidth*(y+1)//8)]
        bits = ''.join(["{:08b}".format(x) for x in row])
        dataRow = [c == '1' for c in bits]
        data.append(dataRow)

    ## Display through PyGame
    blockWidth = screen_width // 64
    blockHeight = screen_height // 32
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    ## Draw gridlines
    screen.fill(BLACK)
    for x in range(0, screen_width, blockWidth):
        for y in range(0, screen_height, blockHeight):
            rect = pygame.Rect(x, y, blockWidth, blockHeight)
            pygame.draw.rect(screen, BLACK, rect, 1)

    xInd, yInd = 0, 0
    for x in range(0, screen_width, blockWidth):
        for y in range(0, screen_height, blockHeight):
            rect = pygame.Rect(x, y, blockWidth, blockHeight)
            yInd = y//blockHeight
            xInd = x//blockWidth
            if (xInd < 64) and (yInd < 32):
                color = WHITE if data[yInd][xInd] else BLACK
                # print(yInd, xInd, color)
                pygame.draw.rect(screen, color, rect, screen_width)

def decrementTimer():
    # TODO Do something aobut this one
    global TIMER, SOUND_TIMER
    if TIMER > 0:
        TIMER -= 1
    else:
        TIMER = (2**8) - 1

    if SOUND_TIMER > 0:
        SOUND_TIMER -= 1
    else:
        SOUND_TIMER = (2**8) - 1

def fetch():
    # TODO Do something about this one
    global PC
    A = memory[PC]
    B = memory[PC + 1]
    value = (hex(A) + ' ' + hex(B)).replace(' 0x', '')
    nibles = [int(nib, 16) for nib in ("{:02x}".format(A) + "{:02x}".format(B))]
    niblesHex = [hex(nib)[-1] for nib in nibles]
    print('\nfetch: ', PC, '0x'+''.join(niblesHex), nibles)
    print(f'\tWorking with niblesHex: {niblesHex}')

    if value == '0x00e0':
        clearDisplay()
    elif value == '0x00ee':
        ### TODO: Finish this after writing call sub routine
        pass
    elif niblesHex[0] == '1':
        # target = (nibleB << 8) + (nibleC << 4) + nibleD
        target = (nibles[1] << 8) + (nibles[2] << 4) + nibles[3]
        jpAddr(target)
    elif niblesHex[0] == '2':
        ### TODO: Call addr
        pass
    elif niblesHex[0] == '3':
        vx = nibles[1]
        value = (nibles[2] << 4) + nibles[3]
        skipEqual(vx, value)
    elif niblesHex[0] == '4':
        vx = nibles[1]
        value = (nibles[2] << 4) + nibles[3]
        skipEqual(vx, value)
    elif niblesHex[0] == '5':
        vx = nibles[1]
        vy = nibles[2]
        skipRegEqual(vx, vy)
    elif niblesHex[0] == '6':
        vx = nibles[1]
        value = (nibles[2] << 4) + nibles[3]
        loadReg(vx, value)
    elif niblesHex[0] == '7':
        vx = nibles[1]
        value = (nibles[2] << 4) + nibles[3]
        addReg(vx, value)
    elif niblesHex[0] == '8' and niblesHex[3] == '0':
        vx = nibles[1]
        vy = nibles[2]
        loadFromReg(vx, vy)
    elif niblesHex[0] == '8' and niblesHex[3] == '1':
        vx = nibles[1]
        vy = nibles[2]
        regOR(vx, vy)
    elif niblesHex[0] == '8' and niblesHex[3] == '2':
        vx = nibles[1]
        vy = nibles[2]
        regAND(vx, vy)
    elif niblesHex[0] == '8' and niblesHex[3] == '3':
        vx = nibles[1]
        vy = nibles[2]
        regXOR(vx, vy)
    elif niblesHex[0] == '8' and niblesHex[3] == '4':
        vx = nibles[1]
        vy = nibles[2]
        regADD(vx, vy)
    elif niblesHex[0] == '8' and niblesHex[3] == '5':
        vx = nibles[1]
        vy = nibles[2]
        regSUB(vx, vy)
    elif niblesHex[0] == '8' and niblesHex[3] == '6':
        vx = nibles[1]
        regSHR(vx)
    elif niblesHex[0] == '8' and niblesHex[3] == '7':
        vx = nibles[1]
        vy = nibles[2]
        regSUBN(vx, vy)
    elif niblesHex[0] == '8' and niblesHex[3] == 'e':
        vx = nibles[1]
        regSHL(vx)
    elif niblesHex[0] == '9' and niblesHex[3] == '0':
        vx = nibles[1]
        vy = nibles[2]
        skipRegNotEqual(vx, vy)
    elif niblesHex[0] == 'a':
        target = (nibles[1] << 8) + (nibles[2] << 4) + nibles[3]
        setI(target)
    elif niblesHex[0] == 'b':
        target = (nibles[1] << 8) + (nibles[2] << 4) + nibles[3]
        jumpRegZero(target)
    elif niblesHex[0] == 'c':
        vx = nibles[1]
        target = (niblesHex[2] << 4) + nibles[3]
        regRandomAND(vx, target)
    elif niblesHex[0] == 'd':
        vx = nibles[1]
        vy = nibles[2]
        offset = nibles[3]
        display(vx, vy, offset)
    elif niblesHex[0] == 'e' and niblesHex[2] == '9' and niblesHex[3] == 'e':
        vx = nibles[1]
        skipKeyRegEq(vx)
    elif niblesHex[0] == 'e' and niblesHex[2] == 'a' and niblesHex[3] == '1':
        vx = nibles[1]
        skipRegNotEqual(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '0' and niblesHex[3] == '7':
        vx = nibles[1]
        loadRegTimer(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '0' and niblesHex[3] == 'a':
        vx = nibles[1]
        waitForKey(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '1' and niblesHex[3] == '5':
        vx = nibles[1]
        setTimer(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '1' and niblesHex[3] == '8':
        vx = nibles[1]
        setSoundTimer(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '1' and niblesHex[3] == 'e':
        vx = nibles[1]
        addRegToI(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '2' and niblesHex[3] == '9':
        vx = nibles[1]
        setIToSprite(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '3' and niblesHex[3] == '3':
        vx = nibles[1]
        storeBCD(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '5' and niblesHex[3] == '5':
        vx = nibles[1]
        dumpRegs(vx)
    elif niblesHex[0] == 'f' and niblesHex[2] == '6' and niblesHex[3] == '5':
        vx = nibles[1]
        loadRegs(vx)

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

def clearDisplay():
    '''
    00E0 - CLS
    Clear the display.
    '''
    global memory, VERBOSE
    if VERBOSE:
        print(f'Running clearDisplay.')

    memory[displayStart:displayEnd+2] = [0x00] * displayLength

def skipEqual(vx, nn):
    '''
    3xnn - SE Vx, byte
    Skip next instruction if Vx = nn.
    If equal, PC += 2.
    '''
    assert nn >= 0 and nn < 2**8, f'Recieved nn: {nn} but should be 0..{2**8-1}'
    global registers, PC, VERBOSE

    regVal = registers[vx]
    if VERBOSE:
        print(f'skipNotEqual: comparing reg {vx} value: {regVal} to {nn}. skipping: {regVal == nn}')

    if regVal == nn:
        PC += 2

def skipNotEqual(vx, nn):
    '''
    4xnn - SNE Vx, byte
    Skip next instruction if Vx != nn.
    If not equal, PC += 2.
    '''
    assert nn >= 0 and nn < 2**8, f'Recieved nn: {nn} but should be 0..{2**8-1}'
    global registers, PC, VERBOSE

    regVal = registers[vx]
    if VERBOSE:
        print(f'skipNotEqual: comparing reg {vx} value: {regVal} to {nn}. skipping: {regVal != nn}')

    if regVal != nn:
        PC += 2

def skipRegEqual(vx, vy):
    '''
    5xy0 - SE Vx, Vy
    Skip if Vx = Vy.
    If equal, PC += 2
    '''
    global registers, PC, VERBOSE

    xVal = registers[vx]
    yVal = registers[vy]
    if VERBOSE:
        print(f'skipNotEqual: comparing reg {vx} value: {xVal} to reg {vy} value: {yVal}. skipping: {xVal == yVal}')

    if xVal == yVal:
        PC += 2

def loadReg(vx, nn):
    '''
    6xnn - LD Vx, byte
    Put value nn in register vx.
    '''
    assert nn >= 0 and nn < 2**8, f'Recieved nn: {nn} but should be 0..{2**8-1}'
    global registers, VERBOSE

    if VERBOSE:
        print(f'loadReg: Changing register {vx} value {registers[vx]} => {nn}')

    registers[vx] = nn

def addReg(vx, nn):
    '''
    7xnn - LD Vx, byte
    Add value nn to current value of register vx.
    '''
    assert nn >= 0 and nn < 2**8, f'Recieved nn: {nn} but should be 0..{2**8-1}'
    global registers, VERBOSE

    newVal = (registers[vx] + nn) % (2**8)
    if VERBOSE:
        print(f'addReg: Changing register {vx} value {registers[vx]} => {newVal}')

    registers[vx] = newVal

def loadFromReg(vx, vy):
    '''
    8xy0 - LD Vx, Vy
    Set register Vx to the current value of Vy.
    '''
    global registers, VERBOSE

    yVal = registers[vy]
    if VERBOSE:
        print(f'loadFromReg: changing reg {vx} from value {registers[vx]} to value in reg {vy} of {yVal}')

    registers[vx] = yVal

def regOR(vx, vy):
    '''
    8xy1 - OR Vx, Vy
    Set Vx to be value of: (Vx OR Vy)
    '''
    global registers, VERBOSE

    xVal = registers[vx]
    yVal = registers[vy]
    newVal = xVal | yVal

    if VERBOSE:
        print(f'regOR: changing reg {vx} from value {registers[vx]} to OR with reg {vy} value: {yVal}, results in: {newVal}')

    registers[vx] = newVal

def regAND(vx, vy):
    '''
    8xy2 - AND Vx, Vy
    Set Vx to be value of: (Vx AND Vy)
    '''
    global registers, VERBOSE

    xVal = registers[vx]
    yVal = registers[vy]
    newVal = xVal & yVal

    if VERBOSE:
        print(f'regAND: changing reg {vx} from value {registers[vx]} to AND with reg {vy} value: {yVal}, results in: {newVal}')

    registers[vx] = newVal

def regXOR(vx, vy):
    '''
    8xy3 - XOR Vx, Vy
    Set Vx to be value of: (Vx XOR Vy)
    '''
    global registers, VERBOSE
    ### TODO: Check that this XOR operator ACTUALLY working...

    xVal = registers[vx]
    yVal = registers[vy]
    newVal = xVal ^ yVal

    if VERBOSE:
        print(f'regXOR: changing reg {vx} from value {registers[vx]} to XOR with reg {vy} value: {yVal}, results in: {newVal}')

    registers[vx] = newVal

def regADD(vx, vy):
    '''
    8xy4 - ADD Vx, Vy
    Set Vx to value of Vx + Vy, set VF to carry bit.
    '''
    global registers, VERBOSE

    xVal = registers[vx]
    yVal = registers[vy]
    newVal = (xVal + yVal) % (2**8)
    carry = (xVal + yVal) // (2**8)

    if VERBOSE:
        print(f'regADD: changing reg {vx} from value {registers[vx]} to ADD with reg {vy} value: {yVal}, results in: {newVal}')
        print(f'regADD: setting carry register to {carry}')

    registers[vx] = newVal
    registers[0xf] = carry

def regSUB(vx, vy):
    '''
    8xy5 - ADD Vx, Vy
    Set Vx to value of Vx - Vy, set VF to borrow.
    '''
    global registers, VERBOSE

    xVal = registers[vx]
    yVal = registers[vy]
    newVal = xVal - yVal
    borrow = yVal // xVal

    if VERBOSE:
        print(f'regSUB: changing reg {vx} from value {registers[vx]} to SUB with reg {vy} value: {yVal}, results in: {newVal}')
        print(f'regSUB: setting borrow register to {borrow}')

    registers[vx] = newVal
    registers[0xf] = borrow

def regSHR(vx):
    '''
    8xy6 - SHR Vx
    Set VF to least significant bit of Vx, then right-shift by 1.
    '''
    global registers, VERBOSE

    xVal = registers[vx]
    leastBit = xVal & 0x01
    newVal = xVal >> 1

    if VERBOSE:
        print(f'regSHR: shifting reg {vx} from value {xVal} to {newVal}')
        print(f'regSHR: setting CF to {leastBit}')

    registers[vx] = newVal
    registers[0xf] = leastBit

def regSUBN(vx, vy):
    '''
    8xy7 - SUBN Vx, Vy
    Set Vx to Vy - Vx, set VF = NOT borrow
    '''
    global registers, VERBOSE

    xVal = registers[vx]
    yVal = registers[vy]
    newVal = xVal - yVal
    borrow = int(not (yVal // xVal))

    if VERBOSE:
        print(f'regSUBN: changing reg {vx} from value {registers[vx]} to SUBN with reg {vy} value: {yVal}, results in: {newVal}')
        print(f'regSUBN: setting (not) borrow register to {borrow}')

    registers[vx] = newVal
    registers[0xf] = borrow

def regSHL(vx):
    '''
    8xyE - SHL Vx {, Vy}
    Set VF to most significant bit of Vx, then left-shift by 1.
    '''
    global registers, VERBOSE

    xVal = registers[vx]
    mostBit = (xVal & 0x80) >> 7
    newVal = (xVal << 1) % (2**8)

    if VERBOSE:
        print(f'regSHL: shifting reg {vx} from value {xVal} to {newVal}')
        print(f'regSHL: setting CF to {mostBit}')

    registers[vx] = newVal
    registers[0xf] = mostBit

def skipRegNotEqual(vx, vy):
    '''
    9xy0 - SNE Vx, Vy
    Skip next instruction if Vx != Vy.
    If Vx != Vy, then PC += 2
    '''
    global registers, PC, VERBOSE

    xVal = registers[vx]
    yVal = registers[vy]
    sameVal = (xVal == yVal)

    if VERBOSE:
        print(f'skipRegNotEqual: comparing reg {vx} with val {xVal} to reg {vy} with val {yVal}')
        print(f'skipRegNotEqual: skipping next?: {sameVal}')

    if not sameVal:
        PC += 2

def setI(nnn):
    '''
    Annn - LD I, addr
    Set I to value at nnn in memory?
    '''
    assert nnn >= 0 and nnn < (2**12), f'Memory address is {nnn} and should be 0..4096'
    global I, memory, VERBOSE

    if VERBOSE:
        print(f'setI: changing I reg from {I} to value {nnn}')

    I = nnn

def jumpRegZero(nnn):
    '''
    Bnnn - JP V0, addr
    Jump to the address nnn plus value in V0
    '''
    assert address >= 0 and address < (2**12), f'Memory address is {address} and should be 512..4096'
    global registers, PC, VERBOSE

    target = (nnn + registers[0]) % (2**12)

    if VERBOSE:
        print(f'jumpRegZero: jumping to address at passed address: {nnn} plus reg 0: {registers[0]}.')
        print(f'jumpRegZero: jumping to address: {target}')

    PC = target

def regRandomAND(vx, nn):
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
        print(f'regRandomAND: Changing register {vx} from {registers[vx]} to {newVal} ({bin(randomVal)} & {bin(nn)} = {bin(newVal)})')

    registers[vx] = newVal

def display(vx, vy, n):
    '''
    Dxyn - DRW Vx, Vy, nibble
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
        print(f'display:')
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

def skipKeyRegEq(vx):
    '''
    Ex9E - SKP Vx
    Skip next instruction if key with value of Vx is pressed.
    If key with value in Vx pressed, then PC += 2
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global registers, keyValues, PC, VERBOSE
    ### TODO: Make keyValues accessible as a global variable

    xVal = registers[vx]
    xValHex = hex(xVal)[-1]
    keyDown = keyValues[xValHex]

    if VERBOSE:
        print(f'skipKeyRegEq: reg {vx} has value {xVal} ({hex(xVal)}), key down?: {keyDown}')

    if keyDown:
        PC += 2

def skipKeyRegNeq(vx):
    '''
    ExA1 - SKNP Vx
    Skip next instruction if key with value of Vx is pressed.
    If key with value in Vx pressed, then PC += 2
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global registers, keyValues, PC, VERBOSE
    ### TODO: Make keyValues accessible as a global variable

    xVal = registers[vx]
    xValHex = hex(xVal)[-1]
    keyDown = keyValues[xValHex]

    if VERBOSE:
        print(f'skipKeyRegNeq: reg {vx} has value {xVal} ({hex(xVal)}), key down?: {keyDown}')

    if not keyDown:
        PC += 2

def loadRegTimer(vx):
    '''
    Fx07 - LD Vx, DT
    Set Vx current timer value.
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global registers, TIMER, VERBOSE

    if VERBOSE:
        print(f'loadRegTimer: chaging reg {vx} from {registers[vx]} to timer value: {TIMER}')

    registers[vx] = TIMER

def waitForKey(vx):
    '''
    Fx0A - LD Vx, K
    Wait for a key to be pressed.
    Stop all other execution until key is pressed.
    '''
    ### TODO: Implement this
    ### TODO: What is included in "all execution"??

def setTimer(vx):
    '''
    Fx15 - LD DT, Vx
    Set the timer to value in Vx.
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global registers, TIMER, VERBOSE

    if VERBOSE:
        print(f'setTimer: changing timer from {TIMER}, to value in reg {vx}: {registers[vx]}')

    TIMER = registers[vx]

def setSoundTimer(vx):
    '''
    Fx18 - LD ST, Vx
    Set the sound timer to value in Vx.
    '''
    assert vx > 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global registers, SOUND_TIMER, VERBOSE

    if VERBOSE:
        print(f'setSoundTimer: changing sound timer from {SOUND_TIMER}, to value in reg {vx}: {registers[vx]}')

    SOUND_TIMER = registers[vx]

def addRegToI(vx):
    '''
    Fx1E - ADD I, Vx
    Set I to I plus value in Vx.
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global I, registers, VERBOSE

    xVal = registers[vx]
    newVal = (I + xVal) % (2**16)

    if VERBOSE:
        print(f'addRegToI: Adding reg {vx} with value {xVal} to I: {I} => {newVal}')

    I = newVal

def setIToSprite(vx):
    '''
    Fx29 - LD F, Vx
    ### TODO: Figure out what this one is supposed to be
    '''
    pass

def storeBCD(vx):
    '''
    Fx33 - LD B, Vx
    Store BCD representation of Vx in memory locations I..(I+2).
    Take decimal values of Vx, place as:
        hundreds : I
        tens     : I + 1
        ones     : I + 2
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global I, registers, memory, VERBOSE
    assert I < (2**12)-2, f'for storeBCD I should be 2 less than end of memory but is: {I}'

    xVal = registers[vx]
    a = xVal // 100
    b = (xVal - 100*a) // 10
    c = (xVal - 100*a - 10*b)

    if VERBOSE:
        print(f'storeBCD: Storing value in reg {vx}: {xVal} as decimal values: {(a, b, c)}')
        print(f'storeBCD: Storing in memory at I: {I}')

    memory[I] = a
    memory[I+1] = b
    memory[I+2] = c

def dumpRegs(vx):
    '''
    Fx55 - LD [I], Vx
    Store registers V0..Vx in (I+1)..(I+1+x).
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global registers, I, memory, VERBOSE

    if VERBOSE:
        print(f'Loading regs 0..{vx} into memory starting at {I}')
        ### TODO: Consider adding before/after memory print for given addresses here

    for i in range(vx+1):
        regVal = registers[i]
        memory[I+1+i] = regVal

def loadRegs(vx):
    '''
    Fx65 - LD Vx, [I]
    Fill registers V0..Vx with values in memory from (I+1)..(I+1+x).
    '''
    assert vx >= 0 and vx < 16, f'vx is {vx} and should be 0..15'
    global registers, I, memory, VERBOSE

    if VERBOSE:
        print(f'Setting regs 0..{vx} from memory starting at {I}')
        ### TODO: Consider adding before/after memory print for given addresses here

    for i in range(vx+1):
        memVal = memory[I+1+i]
        registers[i] = memVal

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
            # joined = list(sum(zip(odds, evens+[0]), ())[:-1])
            joined = sourceContent

            if VERBOSE:
                print(f'Loaded program from {sourceFile}')

        for i, byte in enumerate(joined):
            memory[512+i] = byte

        if VERBOSE:
            print('Finished writing to memory')
            printMemory(start=512, limit=16)

    # Setup pygame parts
    pygame.init()

    scale = 10
    size = screen_width, screen_height = displayWidth*scale, displayHeight*scale
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
        keyValues = {
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
        # print(keyValues)

        # Pygame display stuff
        pygame.display.flip()

        # Manage timer
        time.sleep(TICK_RATE)
        decrementTimer()
        os.system('clear')


        ## General code
        fetch()
        # if TIMER < 230:
        #     print('QUITTING from arbitrary timer limit')
        #     quit()


        ## Example with drawing A sliding across screen
        # clearDisplay()
        # # loadReg(0, 0) # x reg is 0
        # # loadReg(1, 0) # y reg is 1
        # loadReg(0, (displayWidth-TIMER-8)%displayWidth) # x reg is 0
        # loadReg(1, (TIMER-5)%displayHeight) # y reg is 1
        # # loadReg(0, randint(0, displayWidth-1)) # x reg is 0
        # # loadReg(1, randint(0, displayHeight-1)) # y reg is 1
        # # loadReg(0, 62) # x reg is 0
        # # loadReg(1, 0) # y reg is 1

        # setI(fontStart+50)
        # display(0, 1, 5)
        # # printMemory(display=True)

        displayShow()


    pygame.quit()
    exit()

    # game_loop()
    #!/usr/bin/env python
