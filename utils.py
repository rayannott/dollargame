import os
import json
from datetime import datetime
from random import choice
from math import sqrt

import numpy as np
import pygame


FRAMERATE = 60
PANEL_HEIGHT = 50
RECTS = [pygame.Rect([15, PANEL_HEIGHT + ind*(PANEL_HEIGHT + 4), 770, PANEL_HEIGHT])
         for ind in range(9)]
WIDTH, HEIGHT = 800, 600
ALLOWED_SYMBOLS = set('abcdefghijklmnopqrstuvwxyz0123456789 _-.')
SORTBY_LIST = ['date_created', 'num_of_plays', 'best_score', 'game_number']
LAYOUT_LIST = ['planar', 'shell']
THEME_LIST = ['dark', 'light']
ANIMATION_PATHS_LINGERING_TIME = 2 # in animation duration units
FONT_DIR = os.path.join('assets', 'UASQUARE.ttf')
THEME_DIR = os.path.join('assets', 'theme.json')
OPTIONS_DIR = os.path.join('assets', 'options.json')
GAMES_DIR = 'games'
UPSCALE_POS_PREVIEW = np.array([140, 140], dtype=float)

with open(OPTIONS_DIR, 'r') as f:
    OPTIONS = json.load(f)

SFX_DIR = os.path.join('assets', 'sfx')

def load_theme():
    with open(THEME_DIR, 'r') as f:
        THEME_ALL = json.load(f)
    THEME = THEME_ALL[OPTIONS['theme']]
    return THEME

THEME = load_theme()
GREEN, RED, YELLOW = THEME['green'], THEME['red'], THEME['yellow']

PYGAME_KEYS = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9,
    pygame.K_KP0: 0,
    pygame.K_KP1: 1,
    pygame.K_KP2: 2,
    pygame.K_KP3: 3,
    pygame.K_KP4: 4,
    pygame.K_KP5: 5,
    pygame.K_KP6: 6,
    pygame.K_KP7: 7,
    pygame.K_KP8: 8,
    pygame.K_KP9: 9,
}


def get_list_of_game_files():
    if not os.path.isdir(GAMES_DIR):
        os.mkdir(GAMES_DIR)
    return [el for el in os.listdir(GAMES_DIR) if el.endswith('.json')]


def get_next_game_number():
    # cutting off the '.json' part
    games_num = [int(el[:-5]) for el in get_list_of_game_files()]
    if len(games_num) > 0:
        return max(games_num) + 1
    else:
        return 0


def pull_transform_positions_edges_from_gamefile(filename):
    with open(os.path.join(GAMES_DIR, filename)) as f:
        data = json.load(f)
    positions_raw = data['graph']['positions']
    pos = np.array(list(positions_raw.values()), dtype=float)
    pos -= np.min(pos, axis=0)
    pos /= np.max(pos, axis=0)
    pos *= UPSCALE_POS_PREVIEW
    # pos *= np.tile(UPSCALE_POS_PREVIEW, (len(positions_raw), 1))

    res = dict(zip(map(int, positions_raw.keys()), pos.tolist()))
    return res, data['graph']['edges']


def assemble_games_dataframe():
    df = []
    filenames = get_list_of_game_files()
    for file in filenames:
        with open(os.path.join(GAMES_DIR, file), 'r') as f:
            dat = json.load(f)
        data = {}
        graph = dat['graph']
        plays = dat['plays']
        if len(plays):
            best_score = min([len(play['moves']) for play in plays])
        else:
            best_score = 'not solved'
        data['game_number'] = int(file[:-5])
        data['graph'] = (len(graph['values']), len(graph['edges']))
        data['bank'] = sum(graph['values'].values())
        data['num_of_plays'] = len(plays)
        data['best_score'] = best_score
        data['date_created'] = dat['info']['date_created']
        df.append(data)

    if OPTIONS['sort_by'] == 'date_created':
        df.sort(key=lambda x: datetime.strptime(
            x['date_created'], '%d/%m/%Y %H:%M:%S'), reverse=True)
    elif OPTIONS['sort_by'] == 'num_of_plays':
        df.sort(key=lambda x: x['num_of_plays'])  # sort by the number of plays
    elif OPTIONS['sort_by'] == 'best_score':
        df.sort(key=lambda x: x['best_score'] if type(
            x['best_score']) == int else -1, reverse=True)
    elif OPTIONS['sort_by'] == 'game_number':
        df.sort(key=lambda x: x['game_number'])
    return df


def best_solution_by_player(filename):
    with open(f'games/{filename}', 'r') as f:
        game = json.load(f)
        if game['plays']:
            min_number_so_far = 1000000
            best_play_so_far = None
            for play in game['plays']:
                if len(play['moves']) < min_number_so_far:
                    min_number_so_far = len(play['moves'])
                    best_play_so_far = play['moves']
            return best_play_so_far, min_number_so_far
        else:
            return None, None


def save_finished_game(g, moves, filename):
    if filename is None:
        filename = save_new_game(g)

    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open('games/' + filename, 'r') as fr:
        dat = json.load(fr)
    dat['plays'].append({
        'date_played': dt_string,
        'moves': moves
    })
    with open(f'games/{filename}', 'w') as fr:
        json.dump(dat, fr)
    return filename


def save_new_game(g):
    n = get_next_game_number()
    filename = f'{n}.json'
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    to_save = {
        'graph': {
            'edges': list(list(g.edges)),
            'values': {node: g.nodes[node]['val'] for node in g.nodes},
            'positions': {node: g.nodes[node]['pos'] for node in g.nodes}
        },
        'plays': [],
        'info': {
            'date_created': dt_string,
            'note': ''
        }
    }
    with open(f'games/{filename}', 'w') as fr:
        json.dump(to_save, fr)
    return filename


def what_rect_hover(pos):
    for i, rect in enumerate(RECTS):
        if rect.collidepoint(pos):
            return i


def shift_panels(start, finish, shift, number_of_panels):
    # shift is either 1 (down) or -1 (up)
    if shift == 1 and start > 0:
        start -= 1
        finish -= 1
    elif shift == -1 and finish < number_of_panels:
        start += 1
        finish += 1
    return start, finish


def dist(p1, p2):
    return sqrt((p1[1]-p2[1])**2 + (p1[0]-p2[0])**2)



class Vec2:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    def __repr__(self) -> str:
        return f'Vec2({self.x:.3f}, {self.y:.3f})'
    def astuple(self):
        return (self.x, self.y)
    def __str__(self) -> str:
        return f'[{self.x:.3f} {self.y:.3f}]'
    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)
    def __mul__(self, other: float) -> "Vec2":
        return Vec2(self.x * other, self.y * other)
    def __truediv__(self, other: float) -> "Vec2":
        return Vec2(self.x / other, self.y / other)
    def __eq__(self, other) -> bool:
        diff = self - other
        return abs(diff.x) < 1e-5 and abs(diff.y) < 1e-5
    def __abs__(self) -> float:
        return sqrt(self.x**2 + self.y**2)

def linspace(a: float, b: float, N: int) -> list[float]:
    return [a + i*(b-a)/(N-1) for i in range(N)]