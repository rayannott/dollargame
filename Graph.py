import networkx as nx
import json
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


def generate_game(number_of_nodes) -> DGGraph:
    '''
    This would create a graph representing a playable game (i.e. bank>=genus)
    '''
    # how to generate a random connected graph?
    
    pass
