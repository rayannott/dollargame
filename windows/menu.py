import pygame
from sfx import play_sfx

from utils import *
from pygame_setup import *
from ui_elements import Button, HoverTooltip

from windows.options import OptionsWindow
from windows.sandbox import SandboxWindow
from windows.open import OpenGameWindow






def MenuWindow():
    pygame.display.set_caption('Menu')
    D, d, h = 50, 44, 90
    btn_create = Button((200, D + (h+d)*0), (400, h),
                        'CREATE', hover_text='open a sandbox')
    btn_open = Button((200, D + (h+d)*1), (400, h), 'OPEN',
                      hover_text='open an existing game')
    btn_options = Button((200, D + (h+d)*2), (400, h),
                         'OPTIONS', hover_text='configure soem shit')
    btn_exit = Button((200, D + (h+d)*3), (400, h), 'EXIT', hover_text='exit the game')
    btns = [btn_options, btn_create, btn_open, btn_exit]
    hover = HoverTooltip(objects=btns)
    clock = pygame.time.Clock()

    running_menu = True
    while running_menu:
        screen.fill(THEME['background'])
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if btn_options.hovering(up):
                        play_sfx('click')
                        OptionsWindow()
                        pygame.display.set_caption('Menu')
                    elif btn_exit.hovering(up):
                        play_sfx('click')
                        running_menu = False
                        # pygame.quit()
                    elif btn_create.hovering(up):
                        play_sfx('click')
                        SandboxWindow()
                        pygame.display.set_caption('Menu')
                    elif btn_open.hovering(up):
                        play_sfx('click')
                        OpenGameWindow()
                        pygame.display.set_caption('Menu')
            elif event.type == pygame.QUIT:
                running_menu = False

        for obj in btns:
            obj.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # white outline
        pygame.draw.rect(screen, THEME['def'], [0, 0, WIDTH, HEIGHT], 4)
        pygame.display.update()
        clock.tick(FRAMERATE)