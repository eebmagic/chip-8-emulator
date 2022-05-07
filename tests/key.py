from sys import exit
import pygame
from pygame.locals import *
pygame.init()

white = 255, 255, 255

size = screen_width, screen_height = 600, 400
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

def game_loop():
    fps_cap = 120
    running = True
    while running:
        clock.tick(fps_cap)

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

        screen.fill(white)

        pygame.display.flip()

    pygame.quit()
    exit()

game_loop()
#!/usr/bin/env python