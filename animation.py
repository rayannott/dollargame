import random
import math

import pygame

from utils import ANIMATION_PATHS_LINGERING_TIME, Vec2, linspace


def get_random_color():
    r = lambda: random.randint(10, 255)
    return (r(),r(),r())

def fade_color(color: tuple[int, int, int]):
    K = 0.95
    return int(color[0] * K), int(color[1] * K), int(color[2] * K)

class Bezier:
    '''
    Cubic Bezier curves
    '''
    def __init__(self, points: list[Vec2]) -> None:
        '''
        :param points - four points; p0 and p3 are the start and the end of the curve
        '''
        self.p = points

    def __call__(self, t: float) -> Vec2:
        return self.p[0] * (1-t)**3 + self.p[1] * 3 * (1-t)**2 * t + self.p[2] * 3 * (1-t) * t**2 + self.p[3] * t**3

def get_random_p1_p2(p0: Vec2, p3: Vec2) -> tuple[Vec2, Vec2]:
    '''
    Get random intermediate points for the Bezier curve
    '''
    diff = p3 - p0
    len_ = abs(diff)
    alpha_01 = (2 * random.random() -  1) * math.pi/3
    alpha_32 = (2 * random.random() -  1) * math.pi/3
    len_01 = random.random() * len_
    len_32 = random.random() * len_
    delta_01 = Vec2(len_01 * math.sin(alpha_01), len_01 * math.cos(alpha_01))
    delta_32 = Vec2(len_32 * math.sin(alpha_32), len_32 * math.cos(alpha_32))
    p1 = p0 - delta_01
    p2 = p3 + delta_32
    return (p1, p2)


def get_curves(g, node_index: int, give: bool) -> list[Bezier]:
    neigbors_ids = g.neighbors(node_index)
    neigbors_endpoints = [Vec2(*g.nodes[i]['pos']) for i in neigbors_ids]
    p0 = Vec2(*g.nodes[node_index]['pos'])
    curves = []
    for endpoint in neigbors_endpoints:
        if give:
            curves.append(
                Bezier([p0, *get_random_p1_p2(p0, endpoint), endpoint])
            )
        else:
            curves.append(
                Bezier([endpoint, *get_random_p1_p2(endpoint, p0), p0])
            )
    return curves


class Animation:
    def __init__(self) -> None:
        self.CURVE_RESOLUTION = 120
        self.linear_t = linspace(0, 1, self.CURVE_RESOLUTION)
        self.processes = []
        self.accumulated_time = 0
    
    def add_curves(self, curves: list[Bezier]):
        color = get_random_color()
        for curve in curves:
            self.processes.append(
                [0, curve, color]
            )
    
    def tick(self):
        for i, process in enumerate(self.processes):
            process[0] += 2
            if self.CURVE_RESOLUTION < process[0] <= self.CURVE_RESOLUTION * ANIMATION_PATHS_LINGERING_TIME:
                self.processes[i][2] = fade_color(self.processes[i][2])

        
    def draw(self, surface):
        for t, curve, color in self.processes:
            if t <= self.CURVE_RESOLUTION * ANIMATION_PATHS_LINGERING_TIME:
                for t_ in range(min(t, self.CURVE_RESOLUTION)):
                    pygame.draw.circle(surface, color, curve(self.linear_t[t_]).astuple(), 1)
