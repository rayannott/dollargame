from time import perf_counter
from copy import deepcopy
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import choice
from itertools import repeat


from graph import load_game, find_best, collapse_moves

def solve_threading(G, results: list):
    g = deepcopy(G)
    moves = []
    while True:
        n = choice(list(g.nodes))
        if g.nodes[n]['val'] > 0:
            g.give(n)
            moves.append((n, 'give'))
        elif g.nodes[n]['val'] < 0:
            g.take(n)
            moves.append((n, 'take'))
        if g.is_victory():
            return results.append(collapse_moves(moves))

def find_best_threading(g, N):
    threads = []
    results = []
    for i in range(N):
        x = threading.Thread(target=solve_threading, args=(g, results))
        threads.append(x)
        x.start()
    return min(results, key=lambda x: x[1])

def solve_poolexec(g):
    moves = []
    while True:
        n = choice(list(g.nodes))
        if g.nodes[n]['val'] > 0:
            g.give(n)
            moves.append((n, 'give'))
        elif g.nodes[n]['val'] < 0:
            g.take(n)
            moves.append((n, 'take'))
        if g.is_victory():
            return collapse_moves(moves)


def find_best_poolexec(G, N):
    with ThreadPoolExecutor() as executor:
        results = []
        for _ in range(N):
            g = deepcopy(G)
            results.append(executor.submit(solve_poolexec, g))
    true_res = [] 
    for f in as_completed(results):
        true_res.append(f.result())
    return min(true_res, key=lambda x: x[1])


g = load_game('8.json')
print(g)

t0 = perf_counter()
best = find_best(g, N=100)
print('linear time:', perf_counter() - t0)
print(best)

t0 = perf_counter()
res = find_best_threading(g, N=100)
print('simple threading time:', perf_counter() - t0)
print(res)

t0 = perf_counter()
res = find_best_poolexec(g, N=100)
print('ThreadPoolExecutor time:', perf_counter() - t0)
print(res)
# for el in f:
    # print
    # (el)