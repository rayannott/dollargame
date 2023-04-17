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

def blit(text, position, color='#FFFFFF', font=my_font):
    screen.blit(font.render(text, False, color), position)

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
    blit(f'Game #{game_number if game_number is not None else dots}', (20, 110), GREEN)
    if not best is None:
        blit(f'Best = {best}', (20, 130), GREEN)


def display_labels(G, sandbox, num_moves=None, y_shift_genus_bank=False):
    # node values
    for n in G.nodes():
        current_value = G.nodes[n]['val']
        pos = G.nodes[n]['pos']
        blit(str(current_value), (pos[0]+20, pos[1]+12), THEME['def'], my_font_bigger)
        if OPTIONS['show_node_ids']:
            blit(str(n), (pos[0]-36, pos[1]-14), THEME['indices_text'])

    # display parameters (genus, bank) and indicator
    shift = 90 if y_shift_genus_bank else 0
    blit(f'GENUS = {G.genus}', (20, 40 + shift), THEME['def'])
    blit(f'BANK = {G.bank}', (20, 60 + shift), THEME['def'])

    # sandbox if .. True else game
    if sandbox:
        valid = is_game_valid(G)
        blit('valid' if valid else 'invalid', (20, 80), GREEN if valid else RED)
    elif not y_shift_genus_bank:
        blit(f'MOVES = {num_moves}', (20, 80 + shift), THEME['def'])


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
