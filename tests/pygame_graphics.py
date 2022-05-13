from sys import exit
import pygame
import time
import numpy as np
from pygame.locals import *
pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

scale = 10
size = screen_width, screen_height = 64*scale, 32*scale
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

def game_loop():
    fps_cap = 120
    running = True
    while running:
        clock.tick(fps_cap)
        time.sleep(1/20)

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
        # print(values)

        screen.fill(BLACK)
        # data = np.full((32, 64), False)
        data = np.random.rand(32, 64) > 0.9
        data[5][5] = True
        drawGrid(data)

        pygame.display.flip()

    pygame.quit()
    exit()

def drawGrid(data):
    blockWidth = screen_width // 64
    blockHeight = screen_height // 32
    print(blockWidth, blockHeight)
    # Draw gridlines
    for x in range(0, screen_width, blockWidth):
        for y in range(0, screen_height, blockHeight):
            rect = pygame.Rect(x, y, blockWidth, blockHeight)
            pygame.draw.rect(screen, BLACK, rect, 1)

    for x in range(0, screen_width, blockWidth):
        for y in range(0, screen_height, blockHeight):
            rect = pygame.Rect(x, y, blockWidth, blockHeight)
            yInd = y//blockHeight
            xInd = x//blockWidth
            # print(f'yInd: {yInd}, xInd: {xInd}')
            color = WHITE if data[yInd][xInd] else BLACK
            # if yInd == 0 and xInd == 0:
            #     color = WHITE
            # else:
            #     color = BLACK
            pygame.draw.rect(screen, color, rect, screen_width)

game_loop()
#!/usr/bin/env python