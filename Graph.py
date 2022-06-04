import networkx as nx
import json
import numpy as np
from datetime import datetime


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
        self.debt = sum([self.nodes[node]['val'] for node in self.nodes if self.nodes[node]['val'] < 0])
    
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
    with open('games/'+filename, 'r') as fr:
        dat = json.load(fr)
    G = DGGraph(info=dat['info'])
    for n, v in dat['graph']['values'].items():
        G.add_node(int(n), val=v, pos=dat['graph']['positions'][n])
    for e in dat['graph']['edges']:
        G.add_edge(*e)
    return G


# graph generation

def random_connected_graph(n):
    done = False
    while not done:
        G = nx.binomial_graph(n, 0.25)
        done = nx.is_connected(G)
    # TODO: check if planar (how to generate a connected planar graph?)
    return G

def random_list_of_values(n, bank=0):
    # TODO: generate a list of n integers totalling to bank
    while True:
        a = np.random.randint(-4, 5, n)
        if sum(a) == bank:
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

def generate_game(number_of_nodes: int, bank_minus_genus=0) -> DGGraph:
    '''
    This function creates a graph representing a playable game (i.e. bank>=genus)
    '''
    G = random_connected_graph(number_of_nodes)
    posit = nx.planar_layout(G)
    genus = G.number_of_edges() - G.number_of_nodes() + 1
    values = random_list_of_values(n=number_of_nodes, bank=genus + bank_minus_genus)
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    posit = transform_positions(posit)
    DG = DGGraph(info={'date_created': dt_string})
    for n in range(number_of_nodes):
        DG.add_node(n, val=values[n], pos=posit[n])
    for e in G.edges():
        DG.add_edge(*e)
    return DG
