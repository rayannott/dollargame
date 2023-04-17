import os
import json
from datetime import datetime
from copy import deepcopy
from random import choice

import numpy as np
import networkx as nx

from utils import GAMES_DIR, OPTIONS, get_list_of_game_files
import animation
from sfx import play_sfx


def node_gives(node_down, g, anim, moves, silent=False):
    print(f'Node {node_down} gives')
    g.give(node_down)
    if not silent:
        play_sfx('scroll_short_click')
    if OPTIONS['bezier_animation']:
        anim.add_curves(animation.get_curves(g, node_down, give=True))
    moves.append((node_down, 'give'))

def node_takes(node_down, g, anim, moves, silent=False):
    print(f'Node {node_down} takes')
    g.take(node_down)
    if not silent:
        play_sfx('scroll_short_click')
    if OPTIONS['bezier_animation']:
        anim.add_curves(animation.get_curves(g, node_down, give=False))
    moves.append((node_down, 'take'))


class DGGraph(nx.Graph):
    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        self.genus = 1
        self.bank = 0
        self.debt = 0
        self._update_bank()

    # indicators
    def is_connected(self):
        if len(self.nodes) > 0:
            return nx.is_connected(self)
        return False
    # sandbox mode

    def add_node(self, node, val=0, pos=None):
        super().add_node(node, val=val, pos=pos)
        self._update_genus()
        self._update_bank()
        self._update_debt()

    def add_nodes_from(self, nodes):
        pass

    def add_edges_from(self, edges):
        pass

    def remove_node(self, node):
        super().remove_node(node)
        self._update_genus()
        self._update_bank()
        self._update_debt()

    def add_edge(self, s, f):
        super().add_edge(s, f)
        self._update_genus()

    def remove_edge(self, s, f):
        super().remove_edge(s, f)
        self._update_genus()

    def change_value(self, node, increase=True):
        self.nodes[node]['val'] += (1 if increase else -1)
        self._update_bank()
        self._update_debt()

    def _update_genus(self):
        self.genus = self.number_of_edges() - self.number_of_nodes() + 1

    def _update_bank(self):
        self.bank = sum([self.nodes[node]['val'] for node in self.nodes])

    def _update_debt(self):
        self.debt = sum([self.nodes[node]['val']
                        for node in self.nodes if self.nodes[node]['val'] < 0])

    # level mode

    def take(self, node):
        neig = list(self.neighbors(node))
        for n in neig:
            self.nodes[n]['val'] -= 1
        self.nodes[node]['val'] += len(neig)
        self._update_debt()

    def give(self, node):
        neig = list(self.neighbors(node))
        for n in neig:
            self.nodes[n]['val'] += 1
        self.nodes[node]['val'] -= len(neig)
        self._update_debt()

    def is_victory(self):
        return self.debt == 0


# utils

def load_game(filename):
    with open(os.path.join(GAMES_DIR, filename), 'r') as fr:
        dat = json.load(fr)
    G = DGGraph(info=dat['info'])
    for n, v in dat['graph']['values'].items():
        G.add_node(int(n), val=v, pos=dat['graph']['positions'][n])
    for e in dat['graph']['edges']:
        G.add_edge(*e)
    return G

def get_random_game():
    games0 = get_list_of_game_files()
    if len(games0) > 0:
        filename = choice(games0)
        return load_game(filename), filename
    return None, None

# graph generation

def random_connected_graph(n):
    done = False
    while not done:
        G = nx.binomial_graph(n, 0.25)
        done = nx.is_connected(G) and nx.check_planarity(G)[0]
    # TODO: check if planar (how to generate a connected planar graph?)
    return G


def random_list_of_values(n, bank=0):
    a = np.random.randint(-3, 4, n)
    diff = sum(a) - bank
    shifts = (2, 1) if diff > 0 else (-2, -1)
    for i in range(abs(diff)):
        inds = np.random.choice(np.arange(len(a)), 2)
        a[inds[0]] -= shifts[0]
        a[inds[1]] += shifts[1]
    if not sum(a < 0):
        a[0] += max(a)
        a[-1] -= max(a)
    return a.tolist()


def transform_positions(positions):
    # maps positions from networkx layout function to [210, 750] x [50, 550]
    pos = np.array(list(positions.values()))
    mins = np.min(pos, axis=0)
    delta = np.tile(mins, (len(positions), 1))
    pos -= delta
    pos /= np.tile(np.max(pos, axis=0), (len(positions), 1))

    pos *= np.tile([540, 500], (len(positions), 1))
    pos += np.tile([210, 50], (len(positions), 1))
    pos = np.around(pos)
    res = dict(zip(positions.keys(), pos.tolist()))
    return res


def generate_game(number_of_nodes: int, bank_minus_genus=0, display_layout='planar') -> DGGraph:
    '''
    This function creates a graph representing a playable game (i.e. bank>=genus)
    '''
    G = random_connected_graph(number_of_nodes)
    if display_layout == 'planar':
        posit = nx.planar_layout(G)
    elif display_layout == 'shell':
        posit = nx.shell_layout(G)
    else:
        raise KeyError('Unknown layout:', display_layout)

    genus = G.number_of_edges() - G.number_of_nodes() + 1
    values = random_list_of_values(
        n=number_of_nodes, bank=genus + bank_minus_genus)
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    posit = transform_positions(posit)
    DG = DGGraph(info={'date_created': dt_string})
    for n in range(number_of_nodes):
        DG.add_node(n, val=values[n], pos=posit[n])
    for e in G.edges():
        DG.add_edge(*e)
    return DG

# game solving algorithm


def collapse_moves(moves):
    collapsed = dict()
    for node, move in moves:
        if not node in collapsed.keys():
            collapsed[node] = 0
        collapsed[node] += 1 if move == 'take' else -1
    num_moves = sum([abs(num) for num in collapsed.values()])
    return collapsed, num_moves


def solve(G):
    moves = []
    while True:
        n = choice(list(G.nodes))
        if G.nodes[n]['val'] > 0:
            G.give(n)
            moves.append((n, 'give'))
        elif G.nodes[n]['val'] < 0:
            G.take(n)
            moves.append((n, 'take'))
        if G.is_victory():
            return collapse_moves(moves)


def find_best(G, N=10):
    best_so_far = None
    min_num_of_moves = np.inf
    for _ in range(N):
        g = deepcopy(G)
        moves, number_of_moves = solve(g)
        if number_of_moves < min_num_of_moves:
            best_so_far = moves
            min_num_of_moves = number_of_moves
    return best_so_far, min_num_of_moves


def show_instruction(moves, arrows=True):
    tmp = []
    take_give = ['←', '→'] if arrows else [
        ' take', ' give']
    for node, move in moves.items():
        if move > 0:
            tmp.append(f'{node}{take_give[0]}({abs(move)})')
        elif move < 0:
            tmp.append(f'{node}{take_give[1]}({abs(move)})')
    return tmp
