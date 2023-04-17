import os
import numpy as np

import pygame
from ui_elements import Panel

from utils import GREEN, OPTIONS, PANEL_HEIGHT, RED, THEME, UPSCALE_POS_PREVIEW, WIDTH, HEIGHT, FONT_DIR, is_game_valid


pygame_icon = pygame.image.load(os.path.join('assets','icon.png'))
pygame.display.set_icon(pygame_icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
default_font = pygame.font.SysFont('cambria', 20)
my_font = pygame.font.SysFont(FONT_DIR, 30)
my_font_bigger = pygame.font.SysFont(FONT_DIR, 36)
my_font_hover = pygame.font.SysFont(FONT_DIR, 26)

def create_panels(df):
    panels = []
    for dat in df:
        panels.append(Panel(data=dat))
    return panels


def display_panels(panels):
    for ind, panel in enumerate(panels):
        panel.draw(topleft=(17, PANEL_HEIGHT + ind*54),
                   screen=screen, font=my_font)


def display_prev_stats(game_number, best=None):
    dots = '...'
    screen.blit(my_font.render(
        f'Game #{game_number if game_number is not None else dots}', False, GREEN), (20, 110))
    if not best is None:
        screen.blit(my_font.render(f'Best = {best}', False, GREEN), (20, 130))


def display_labels(G, sandbox, num_moves=None, y_shift_genus_bank=False):
    # node values
    for n in G.nodes():
        current_value = G.nodes[n]['val']
        pos = G.nodes[n]['pos']
        screen.blit(my_font_bigger.render(str(current_value), False,
                    THEME['def'] if current_value >= 0 else RED), (pos[0]+20, pos[1]+12))
        if OPTIONS['show_node_ids']:
            text_node_indices = my_font.render(
                str(n), False, THEME['indices_text'])
            screen.blit(text_node_indices, (pos[0]-36, pos[1]-14))

    # display parameters (genus, bank) and indicator
    shift = 90 if y_shift_genus_bank else 0
    screen.blit(my_font.render(
        f'GENUS = {G.genus}', False, THEME['def']), (20, 40 + shift))
    screen.blit(my_font.render(
        f'BANK = {G.bank}', False, THEME['def']), (20, 60 + shift))

    # sandbox if .. True else game
    if sandbox:
        valid = is_game_valid(G)
        screen.blit(my_font.render(
            'valid' if valid else 'invalid', False, GREEN if valid else RED), (20, 80))
    else:
        if not y_shift_genus_bank:
            screen.blit(my_font.render(
                f'MOVES = {num_moves}', False, THEME['def']), (20, 80 + shift))


def display_nodes_edges(G, node_to_highlight):
    # nodes
    if node_to_highlight is not None:
        for node in G.nodes:
            pygame.draw.circle(screen, THEME['def'] if node != node_to_highlight else '#00ff00',
                           G.nodes[node]['pos'], 20, 2)
    else:
        for node in G.nodes:
            pygame.draw.circle(screen, THEME['def'],
                           G.nodes[node]['pos'], 20, 2)
    # edges
    for s, f in G.edges:
        pygame.draw.line(screen, THEME['def'],
                         G.nodes[s]['pos'],
                         G.nodes[f]['pos'], 2)

def shift_tuple(tup, delta):
    return (tup[0] + delta[0], tup[1] + delta[1])

def display_graph_preview(positions: dict[int, np.array], edges: np.array, current_mouse_pos: np.array):
    pygame.draw.rect(screen, THEME['button_inactive'], 
                    pygame.Rect(shift_tuple(current_mouse_pos, (-15, -15)), shift_tuple(UPSCALE_POS_PREVIEW, (30, 30))),
                    border_radius=3)
    pygame.draw.rect(screen, THEME['def'], 
                    pygame.Rect(shift_tuple(current_mouse_pos, (-10, -10)), shift_tuple(UPSCALE_POS_PREVIEW, (20, 20))),
                    border_radius=3, width=2)
    for pos in positions.values():
        pygame.draw.circle(screen, THEME['def'], pos + current_mouse_pos, 4)
    for s, f in edges:
        pygame.draw.line(screen, THEME['def'],
                        positions[s] + current_mouse_pos,
                        positions[f] + current_mouse_pos, 1)
