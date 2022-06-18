import pygame
import os
import json
from datetime import datetime
from random import choice
from math import sqrt

from Graph import load_game

PANEL_HEIGHT = 50
WHITE, GREEN, RED, YELLOW = (
    255, 255, 255), (0, 255, 0), (255, 0, 0), (233, 218, 52)
RECTS = [pygame.Rect([15, PANEL_HEIGHT + ind*(PANEL_HEIGHT + 4), 770, PANEL_HEIGHT])
         for ind in range(9)]
WIDTH, HEIGHT = 800, 600
ALLOWED_SYMBOLS = set(' 0123456789_-abcdefghijklmnopqrstuvwxyz')
SORTBY_LIST = ['date_created', 'num_of_plays', 'best_score', 'game_number']
LAYOUT_LIST = ['planar', 'shell']

with open('options.json', 'r') as f:
    OPTIONS = json.load(f)

with open('theme.json', 'r') as f:
    THEME = json.load(f)


def get_list_of_game_files():
    if not os.path.isdir('games'):
        os.mkdir('games')
    return [el for el in os.listdir('games') if el.endswith('.json')]


def get_random_game():
    games0 = get_list_of_game_files()
    if len(games0) > 0:
        filename = choice(games0)
        return load_game(filename), filename
    return None, None


def get_next_game_number():
    # cutting off the '.json' part
    games_num = [int(el[:-5]) for el in get_list_of_game_files()]
    if len(games_num) > 0:
        return max(games_num) + 1
    else:
        return 0


def assemble_games_dataframe():
    df = []
    filenames = get_list_of_game_files()
    for file in filenames:
        with open('games/' + file, 'r') as f:
            dat = json.load(f)
        data = {}
        graph = dat['graph']
        values = graph['values'].values()
        genus = len(graph['edges']) - len(values) + 1
        plays = dat['plays']
        if len(plays):
            best_score = min([len(play['moves']) for play in plays])
        else:
            best_score = 'not solved'
        data['game_number'] = int(file[:-5])
        data['graph'] = (len(graph['values']), len(graph['edges']))
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
    print(f'New file {filename} created')
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


def is_game_valid(G):
    mask = [G.nodes[n]['val'] < 0 for n in G.nodes]
    at_least_one_negative = sum(mask)
    winnable = G.bank >= G.genus
    enough_nodes = len(G.nodes) > 2
    enough_edges = len(G.edges) > 1
    connected = G.is_connected()
    return winnable and enough_nodes and enough_edges and at_least_one_negative and connected


def mouse_on_node(G, pos):
    for node, attr in G.nodes.items():
        if dist(pos, attr['pos']) < 20:
            return (True, node)
    return (False, None)


def create_node(G, node_num, pos):
    G.add_node(node=node_num, val=0, pos=pos)
    print(f'Node {node_num} created: {G.nodes[node_num]}')


def remove_node(G, node_num):
    G.remove_node(node_num)
    print(f'Node {node_num} removed')


def create_edge(G, s, f):
    G.add_edge(s, f)
    print(f'Created edge {s}->{f}')


def remove_edge(G, s, f):
    G.remove_edge(s, f)
    print(f'Removed edge {s}->{f}')


def increase_value(G, node):
    G.change_value(node, increase=True)


def decrease_value(G, node):
    G.change_value(node, increase=False)


def far_enough_from_nodes(G, release_pos):
    # to avoid overcrowding :)
    for node in G.nodes:
        if dist(release_pos, G.nodes[node]['pos']) < 80:
            return False
    return True
