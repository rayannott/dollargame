import json
import pygame
from Graph import DGGraph, load_game
from itertools import count
from math import sqrt
from Button import Button, Panel
import os
from datetime import datetime
from random import choice
import pandas as pd

WHITE, GREEN, RED = (255, 255, 255), (0, 255, 0), (255, 0, 0)


def get_list_of_game_files():
    return [el for el in os.listdir('games') if el.endswith('.json')]


def get_random_game():
    games0 = get_list_of_game_files()
    filename = choice(games0)
    return load_game(filename), filename


def assemble_games_dataframe():
    # this dataframe will have columns:
    # game_number, difficulty(genus?), number_of_plays, best_play, date_created
    import time
    data = {
        'game_number': [],
        'difficulty': [],
        'num_of_plays': [],
        'best_score': [],
        'date_created': []
    }
    filenames = get_list_of_game_files()
    for file in filenames:
        with open('games/' + file, 'r') as f:
            dat = json.load(f)

        data['game_number'].append(int(file[:-5]))
        data['difficulty'].append('none yet')
        data['num_of_plays'].append(len(dat['plays']))
        data['best_score'].append('none yet 2')
        data['date_created'].append(dat['info']['date_created'])
    df = pd.DataFrame(data)
    df = df.set_index('game_number')
    df.sort_values('num_of_plays', inplace=True)
    return df


def create_panels(df):
    panels = []
    for i, (game_num, row) in enumerate(df.iterrows()):
        row['game_number'] = game_num
        panels.append(Panel(data=row))
    return panels


def display_panels(panels):
    for ind, panel in enumerate(panels):
        panel.draw(topleft=(15, 16 + ind*87), screen=screen, font=my_font)


def shift_panels(start, finish, shift, number_of_panels):
    # shift is either 1 (down) or -1 (up)
    if shift == 1 and start > 0:
        start -= 1
        finish -= 1
    elif shift == -1 and finish < number_of_panels - 1:
        start += 1
        finish += 1
    return start, finish
    


def get_next_game_number():
    # cutting off the '.json' part
    games_num = [int(el[:-5]) for el in get_list_of_game_files()]
    return max(games_num) + 1


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
            'date_created': dt_string
        }
    }
    with open(f'games/{filename}', 'w') as fr:
        json.dump(to_save, fr)
    print(f'New file {filename} created')
    return filename


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
        if dist(pos, attr['pos']) < NODERADIUS:
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


def display_log(G, clear):
    pass


def display_labels(G, sandbox, num_moves=None):
    # node values
    for n in G.nodes():
        current_value = G.nodes[n]['val']
        text_node_vals = my_font_bigger.render(str(current_value), False,
                                               WHITE if current_value >= 0 else RED)
        pos = G.nodes[n]['pos']
        screen.blit(text_node_vals,
                    (pos[0]+int(NODERADIUS/1), pos[1]+int(NODERADIUS/2)))
    # display parameters (genus, bank) and indicator
    text_params1 = my_font.render(f'GENUS = {G.genus}', False, WHITE)
    text_params2 = my_font.render(f'BANK = {G.bank}', False, WHITE)

    screen.blit(text_params1, (20, 40))
    screen.blit(text_params2, (20, 60))
    if sandbox:
        valid = is_game_valid(G)
        text_proceed = my_font.render(
            'valid' if valid else 'invalid', False, GREEN if valid else RED)
        screen.blit(text_proceed, (20, 80))
    else:
        text_moves = my_font.render(f'#of moves = {num_moves}', False, WHITE)
        screen.blit(text_moves, (20, 80))


def display_nodes_edges(G):
    # nodes
    for node in G.nodes:
        pygame.draw.circle(screen, (255, 255, 255),
                           G.nodes[node]['pos'], NODERADIUS, 2)
    # edges
    for s, f in G.edges:
        pygame.draw.line(screen, (255, 255, 255),
                         G.nodes[s]['pos'],
                         G.nodes[f]['pos'], 2)


def SandboxWindow():
    pygame.display.set_caption('Game creation')
    running = True
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))

    G = DGGraph()
    cnt = count(0)
    # log = []
    btn_proceed = Button(topleft=(30, 450), size=(100, 40), text='Proceed')
    btn_proceed.is_active = is_game_valid(G)
    btn_discard = Button(topleft=(30, 510), size=(100, 40), text='Discard')

    # Game creation loop
    while running:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
                # print(down)
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if not field_rect.collidepoint(up):
                    if btn_proceed.hovering(up):
                        GameWindow(G)
                    if btn_discard.hovering(up):
                        # add discard confirmation
                        running = False
                else:
                    down_bool, node_down = mouse_on_node(G, down)
                    up_bool, node_up = mouse_on_node(G, up)
                    if event.button == 4:  # mousewheel up
                        if down_bool:
                            increase_value(G, node_down)
                    elif event.button == 5:  # mousewheel down
                        if down_bool:
                            decrease_value(G, node_down)
                    elif down_bool:
                        if up_bool:
                            if node_down == node_up:
                                remove_node(G, node_down)
                            else:
                                if (node_down, node_up) in G.edges:
                                    remove_edge(G, node_down, node_up)
                                else:
                                    create_edge(G, node_down, node_up)
                    else:
                        if dist(down, up) < NODERADIUS:
                            create_node(G, next(cnt), down)
                        else:
                            # temporary
                            print('Unknown command')

            elif event.type == pygame.QUIT:
                running = False

        btn_proceed.draw(screen, my_font)
        btn_proceed.is_active = is_game_valid(G)
        btn_discard.draw(screen, my_font)
        display_labels(G, sandbox=True)
        display_nodes_edges(G)
        # purple outline
        pygame.draw.rect(screen, (213, 88, 251), [0, 0, WIDTH, HEIGHT], 4)
        # sandbox field
        pygame.draw.rect(screen, (0, 0, 255), [
                         WIDTH*0.2, 4, WIDTH*0.8-4, HEIGHT-8], 2)
        pygame.display.update()


def OpenGameWindow():
    print('OpenGameWindow is opened')
    pygame.display.set_caption('Menu')
    files_rect = pygame.Rect((10, 10), (780, 530))
    btn_back = Button((10, 550), (100, 40), 'back')
    btn_randomgame = Button((130, 550), (100, 40), 'random')
    df = assemble_games_dataframe()
    panels = create_panels(df)
    start, finish = 0, 6
    panels6 = panels[start:finish]
    running_opengame = True

    while running_opengame:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 4:  # mousewheel up
                    print('mousewheel up')
                    start, finish = shift_panels(start, finish, shift=1, number_of_panels=len(panels))
                    panels6 = panels[start:finish]
                elif event.button == 5:  # mousewheel down
                    print('mousewheel down')
                    start, finish = shift_panels(start, finish, shift=-1, number_of_panels=len(panels))
                    panels6 = panels[start:finish]
                elif btn_back.hovering(up):
                    running_opengame = False
                elif btn_randomgame.hovering(up):
                    print('Starting a random game')
                    g, filename = get_random_game()
                    GameWindow(g, filename)
            elif event.type == pygame.QUIT:
                running_opengame = False
        
        btn_back.draw(screen, my_font)
        btn_randomgame.draw(screen, my_font)
        display_panels(panels6)
        pygame.draw.rect(screen, WHITE, [10, 10, 780, 530], 4)
        pygame.display.update()


def GameWindow(g, filename=None):
    val = filename or 'New'
    print(f'{val} game is started')
    pygame.display.set_caption('Game')
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))
    btn_save = Button(topleft=(30, 450), size=(100, 40), text='Save')
    btn_back = Button(topleft=(30, 510), size=(100, 40), text='Back')
    running_game = True
    is_victory = False
    only_once = True
    moves = []

    while running_game:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if not field_rect.collidepoint(up):
                    if btn_save.hovering(up):
                        if not moves:
                            print('Save empty game')
                            filename = save_new_game(g)
                            btn_save.is_active = False
                        elif is_victory:
                            save_finished_game(g, moves, filename)
                            btn_save.is_active = False
                    elif btn_back.hovering(up):
                        running_game = False
                        break
                elif not is_victory:
                    down_bool, node_down = mouse_on_node(g, down)
                    up_bool, node_up = mouse_on_node(g, up)
                    if down_bool:
                        if not up_bool:
                            if down[1] > up[1]:
                                print(f'Node {node_down} gives')
                                g.give(node_down)
                                moves.append((node_down, 'give'))
                            else:
                                print(f'Node {node_down} takes')
                                g.take(node_down)
                                moves.append((node_down, 'take'))
                    is_victory = g.is_victory()

            elif event.type == pygame.QUIT:
                running_game = False

        if is_victory and only_once:
            print('You won!')
            btn_save.is_active = True
            only_once = False

        if moves and not is_victory:
            btn_save.is_active = False

        btn_save.draw(screen, my_font)
        btn_back.draw(screen, my_font)
        display_labels(g, sandbox=False, num_moves=len(moves))
        display_nodes_edges(g)
        # orange outline (when not solved)
        pygame.draw.rect(screen, (254, 151, 0) if not is_victory else GREEN, [
                         0, 0, WIDTH, HEIGHT], 4)
        # play field
        pygame.draw.rect(screen, (0, 0, 255), [
                         WIDTH*0.2, 4, WIDTH*0.8-4, HEIGHT-8], 2)
        pygame.display.update()


def OptionsWindow():
    pass


def MenuWindow():
    pygame.display.set_caption('Menu')
    btn_play = Button((200, 50), (400, 100), 'PLAY')
    btn_play_create = Button((200, 50), (130, 100), 'create', is_active=False)
    btn_play_open = Button((333, 50), (130, 100), 'open', is_active=False)
    btn_play_back = Button((466, 50), (130, 100), 'back', is_active=False)
    btn_options = Button((200, 250), (400, 100), 'OPTIONS')
    btn_exit = Button((200, 450), (400, 100), 'EXIT')

    show_play_subbtns = False

    running_menu = True
    while running_menu:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if btn_play.hovering(up):
                    show_play_subbtns = True
                    btn_play.is_active = False
                    btn_play_create.is_active = True
                    btn_play_open.is_active = True
                    btn_play_back.is_active = True
                elif btn_options.hovering(up):
                    # OptionsWindow: show_nodes_ids
                    pass
                elif btn_exit.hovering(up):
                    running_menu = False
                    # pygame.quit()
                elif btn_play_back.hovering(up):
                    show_play_subbtns = False
                    btn_play.is_active = True
                    btn_play_create.is_active = False
                    btn_play_open.is_active = False
                    btn_play_back.is_active = False
                elif btn_play_create.hovering(up):
                    SandboxWindow()
                elif btn_play_open.hovering(up):
                    print('this should open a window to choose an existing game')
                    OpenGameWindow()
                # print(up)
            elif event.type == pygame.QUIT:
                running_menu = False

        if show_play_subbtns:
            btn_play_create.draw(screen, my_font)
            btn_play_open.draw(screen, my_font)
            btn_play_back.draw(screen, my_font)
        else:
            btn_play.draw(screen, my_font)

        # white outline
        pygame.draw.rect(screen, (255, 255, 255), [0, 0, WIDTH, HEIGHT], 4)

        btn_options.draw(screen, my_font)
        btn_exit.draw(screen, my_font)
        pygame.display.update()


if __name__ == '__main__':
    WIDTH, HEIGHT = 800, 600
    NODERADIUS = 20
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.font.init()
    my_font = pygame.font.SysFont('UASQUARE.ttf', 30)
    my_font_bigger = pygame.font.SysFont('UASQUARE.ttf', 36)

    # MenuWindow()
    # g = load_game('6.json')
    # GameWindow(g, '6.json')
    OpenGameWindow()
