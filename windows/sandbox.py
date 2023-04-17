from itertools import count

import pygame

from utils import *
from pygame_setup import *
from graph import DGGraph, create_edge, create_node, decrease_value, far_enough_from_nodes, generate_game, increase_value, mouse_on_node, remove_edge, remove_node
from ui_elements import Button, HoverTooltip, Panel, Counter, TextInput
from sfx import play_sfx
from windows.game import GameWindow


def SandboxWindow():
    pygame.display.set_caption('Game creation')
    running = True
    holding_down = False
    holding_with_shift = False
    down_bool = False
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))

    G = DGGraph()
    cnt = count(0)
    btn_generate = Button(topleft=(15, 230), size=(135, 40),
                          text='Generate', hover_text='generate a new game')
    cnt_nodes = Counter(topleft=(15, 280), size=(110, 40), value=6, bounds=(3, 100),
                        text='Nodes', hover_text='enter the number of nodes')
    cnt_b_minus_g = Counter(topleft=(15, 330), size=(110, 40), value=2, bounds=(0, 100),
                            text='B-G', hover_text='bank - genus; 0 is the most difficult (no extra dollars)')
    btn_clear = Button(topleft=(30, 410), size=(100, 40),
                       text='Clear', hover_text='clears the field')
    btn_proceed = Button(topleft=(30, 460), size=(100, 40),
                         text='Proceed', is_active=False, hover_text='play!')
    btn_discard = Button(topleft=(30, 510), size=(100, 40), text='Discard',
                         hover_text='go back (loses progress)')
    objects = [
        btn_proceed, btn_discard, btn_generate,
        btn_clear, cnt_nodes, cnt_b_minus_g
    ]
    hover = HoverTooltip(objects=objects)
    clock = pygame.time.Clock()

    # Game creation loop
    while running:
        screen.fill(THEME['background'])
        for event in pygame.event.get():
            if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                holding_with_shift = False # fixed issue #4
                if event.type == pygame.MOUSEBUTTONDOWN:
                    down = pygame.mouse.get_pos()
                    holding_down = True
                    down_bool, node_down = mouse_on_node(G, down)
                elif event.type == pygame.MOUSEBUTTONUP:
                    holding_down = False
                    up = pygame.mouse.get_pos()
                    if not field_rect.collidepoint(up):
                        if event.button == 1:
                            if btn_proceed.hovering(up):
                                play_sfx('click')
                                GameWindow(G)
                                # pygame.display.set_caption('Game creation')
                                running = False
                            elif btn_generate.hovering(up):
                                play_sfx('click')
                                G = generate_game(number_of_nodes=cnt_nodes.value,
                                                  bank_minus_genus=cnt_b_minus_g.value,
                                                  display_layout=OPTIONS['layout'])
                                cnt = count(G.number_of_nodes())
                                btn_proceed.is_active = True
                            elif btn_discard.hovering(up):
                                play_sfx('click')
                                running = False
                            elif btn_clear.hovering(up):
                                play_sfx('click')
                                G = DGGraph()
                                cnt = count(0)
                        elif event.button in {4, 5}:
                            play_sfx('scroll_short_click')
                            cnt_nodes.hovering(
                                up, add=1 if event.button == 4 else -1)
                            cnt_b_minus_g.hovering(
                                up, add=1 if event.button == 4 else -1)
                    else:
                        down_bool, node_down = mouse_on_node(G, down)
                        up_bool, node_up = mouse_on_node(G, up)
                        if event.button == 4:  # mousewheel up
                            if down_bool:
                                increase_value(G, node_down)
                                play_sfx('scroll_short_click')
                        elif event.button == 5:  # mousewheel down
                            if down_bool:
                                decrease_value(G, node_down)
                                play_sfx('scroll_short_click')
                        elif down_bool:
                            if up_bool:
                                if node_down == node_up:
                                    remove_node(G, node_up)
                                    play_sfx('node_action')
                                else:
                                    if (node_down, node_up) in G.edges:
                                        remove_edge(G, node_down, node_up)
                                    else:
                                        create_edge(G, node_down, node_up)
                                    play_sfx('edge_action')
                        else:
                            if dist(down, up) < 20 and far_enough_from_nodes(G, down):
                                create_node(G, next(cnt), down)
                                play_sfx('node_action')
                elif event.type == pygame.QUIT:
                    running = False
            else:
                # moving the nodes
                if event.type == pygame.MOUSEBUTTONDOWN:
                    down_shift = pygame.mouse.get_pos()
                    holding_with_shift = True
                    down_bool_shift, node_down_shift = mouse_on_node(
                        G, down_shift)
                elif event.type == pygame.MOUSEBUTTONUP:
                    holding_with_shift = False

        # moving the nodes
        if holding_with_shift and down_bool_shift:
            G.nodes[node_down_shift]['pos'] = pygame.mouse.get_pos()

        display_nodes_edges(G, None)
        display_labels(G, sandbox=True)

        # aesthetics (when drawing edges)
        if holding_down:
            pos = pygame.mouse.get_pos()
            if down_bool:
                hovering_node_bool, hovering_node_number = mouse_on_node(
                    G, pos)
                if hovering_node_bool:
                    color = RED if (
                        node_down, hovering_node_number) in G.edges else (120, 205, 0)
                    pygame.draw.line(screen, color,
                                     G.nodes[node_down]['pos'], G.nodes[hovering_node_number]['pos'], 2)
                else:
                    pygame.draw.line(screen, (150, 150, 150),
                                     G.nodes[node_down]['pos'], pos, 2)

        btn_proceed.is_active = is_game_valid(G)
        for obj in objects:
            obj.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # purple outline
        pygame.draw.rect(screen, (213, 88, 251), [0, 0, WIDTH, HEIGHT], 4)
        # sandbox field
        pygame.draw.rect(screen, THEME['field_outline'], [
            WIDTH*0.2, 4, WIDTH*0.8-4, HEIGHT-8], 2)
        pygame.display.update()
        clock.tick(FRAMERATE)

