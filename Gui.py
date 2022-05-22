import json
import pygame
from graph import DGGraph, load_game
from itertools import count
from math import sqrt
from ui_elements import Button, HoverTooltip, Panel, Counter, PANEL_HEIGHT
import os
from datetime import datetime
from random import choice
from copy import deepcopy

# renamed file

WHITE, GREEN, RED = (255, 255, 255), (0, 255, 0), (255, 0, 0)
RECTS = [pygame.Rect([15, PANEL_HEIGHT + ind*(PANEL_HEIGHT + 4), 770, PANEL_HEIGHT])
         for ind in range(9)]
WIDTH, HEIGHT = 800, 600
SORTBY_LIST = ['date_created', 'num_of_plays', 'best_score']

pygame_icon = pygame.image.load('icon.png')
pygame.display.set_icon(pygame_icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
my_font = pygame.font.SysFont('UASQUARE.ttf', 30)
my_font_bigger = pygame.font.SysFont('UASQUARE.ttf', 36)
my_font_hover = pygame.font.SysFont('UASQUARE.ttf', 26)

with open('options.json', 'r') as f:
    OPTIONS = json.load(f)


def get_list_of_game_files():
    return [el for el in os.listdir('games') if el.endswith('.json')]


def get_random_game():
    games0 = get_list_of_game_files()
    filename = choice(games0)
    return load_game(filename), filename


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
        df.sort(key=lambda x : datetime.strptime(x['date_created'], '%d/%m/%Y %H:%M:%S'), reverse=True)
    elif OPTIONS['sort_by'] == 'num_of_plays':
        df.sort(key=lambda x : x['num_of_plays']) # sort by the number of plays
    elif OPTIONS['sort_by'] == 'best_score':
        df.sort(key=lambda x : x['best_score'] if type(x['best_score'])==int else -1, reverse=True)
    return df


def create_panels(df):
    panels = []
    for dat in df:
        panels.append(Panel(data=dat))
    return panels


def display_panels(panels):
    for ind, panel in enumerate(panels):
        panel.draw(topleft=(15, PANEL_HEIGHT + ind*54),
                   screen=screen, font=my_font)


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


def display_prev_stats(game_number, best=None):
    if not best is None:
        screen.blit(my_font.render(f'Best = {best}', False, GREEN), (20, 130))
    screen.blit(my_font.render(f'Game #{game_number}', False, GREEN), (20, 110))


def display_labels(G, sandbox, num_moves=None):
    # node values
    for n in G.nodes():
        current_value = G.nodes[n]['val']
        text_node_vals = my_font_bigger.render(str(current_value), False,
                                               WHITE if current_value >= 0 else RED)
        pos = G.nodes[n]['pos']
        screen.blit(text_node_vals, (pos[0]+20, pos[1]+12))
        if OPTIONS['show_node_ids']:
            text_node_indices = my_font.render(str(n), False, (225, 240, 129))
            screen.blit(text_node_indices, (pos[0]-36, pos[1]-8))
    
    # display parameters (genus, bank) and indicator
    text_params1 = my_font.render(f'GENUS = {G.genus}', False, WHITE)
    text_params2 = my_font.render(f'BANK = {G.bank}', False, WHITE)
    screen.blit(text_params1, (20, 40))
    screen.blit(text_params2, (20, 60))

    # sandbox if .. True else game
    if sandbox:
        valid = is_game_valid(G)
        text_proceed = my_font.render(
            'valid' if valid else 'invalid', False, GREEN if valid else RED)
        screen.blit(text_proceed, (20, 80))
    else:
        text_moves = my_font.render(f'MOVES = {num_moves}', False, WHITE)
        screen.blit(text_moves, (20, 80))


def display_nodes_edges(G):
    # nodes
    for node in G.nodes:
        pygame.draw.circle(screen, (255, 255, 255),
                           G.nodes[node]['pos'], 20, 2)
    # edges
    for s, f in G.edges:
        pygame.draw.line(screen, (255, 255, 255),
                         G.nodes[s]['pos'],
                         G.nodes[f]['pos'], 2)




# ----------------WINDOWS --------------------

def SandboxWindow():
    pygame.display.set_caption('Game creation')
    running = True
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))

    G = DGGraph()
    cnt = count(0)
    btn_proceed = Button(topleft=(30, 450), size=(100, 40), 
                        text='Proceed', is_active=False, hover_text='play!')
    btn_discard = Button(topleft=(30, 510), size=(100, 40), text='Discard',
                        hover_text='go back (loses progress)')
    hover = HoverTooltip(objects=[btn_proceed, btn_discard])
    
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
                        # pygame.display.set_caption('Game creation')
                        running = False
                    if btn_discard.hovering(up):
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
                        if dist(down, up) < 20:
                            create_node(G, next(cnt), down)

            elif event.type == pygame.QUIT:
                running = False
        btn_proceed.is_active = is_game_valid(G)
        btn_proceed.draw(screen, my_font)
        btn_discard.draw(screen, my_font)
        display_labels(G, sandbox=True)
        display_nodes_edges(G)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # purple outline
        pygame.draw.rect(screen, (213, 88, 251), [0, 0, WIDTH, HEIGHT], 4)
        # sandbox field
        pygame.draw.rect(screen, (0, 0, 255), [
                         WIDTH*0.2, 4, WIDTH*0.8-4, HEIGHT-8], 2)
        pygame.display.update()


def GenerateGameWindow():
    pygame.display.set_caption('Game generation')
    btn_back = Button(topleft=(10, 550), size=(100, 40), 
                            text='Back', hover_text='go back')
    btn_generate = Button(topleft=(10, 500), size=(120, 40), 
                            text='Generate', hover_text='generate a new graph')
    cnt_nodes = Counter(topleft=(10, 30), size=(100, 40), 
                            text='Nodes', hover_text='enter a number of nodes')
    cnt_edges = Counter(topleft=(10, 80), size=(100, 40), 
                            text='Edges', hover_text='enter a number of edges')
    hover = HoverTooltip(objects=[btn_back, btn_generate, cnt_nodes, cnt_edges], topleft=(165, 570))

    running_generation = True
    while running_generation:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if btn_back.hovering(up):
                        running_generation = False
                    elif btn_generate.hovering(up):
                        print('Game generated')
                    elif cnt_nodes.hovering(up, press=True):
                        print('Value is', cnt_nodes.value)
                    elif cnt_edges.hovering(up, press=True):
                        print('Value is', cnt_edges.value)
                elif event.button in {4,5}:
                    cnt_nodes.hovering(up, add=1 if event.button == 4 else -1)
                    cnt_edges.hovering(up, add=1 if event.button == 4 else -1)
            elif event.type == pygame.QUIT:
                running_generation = False
        

        btn_back.draw(screen, my_font)
        btn_generate.draw(screen, my_font)
        cnt_nodes.draw(screen, my_font)
        cnt_edges.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # blue outline
        pygame.draw.rect(screen, (38, 205, 235), [0, 0, WIDTH, HEIGHT], 4)
        # field
        pygame.draw.rect(screen, (0, 0, 255), [WIDTH*0.2, 4, WIDTH*0.8-4, HEIGHT-8], 2)
        pygame.display.update()


def OpenGameWindow():
    print('OpenGameWindow is opened')
    btn_back = Button((10, 550), (100, 40), 'back', hover_text='go back to menu')
    btn_randomgame = Button((120, 550), (100, 40), 'random', hover_text='start with a random saved game')
    btn_generate_game = Button((230, 550), (110, 40), 'generate', hover_text='open a game generation window')
    btn_shiftdown = Button((745, 550), (45, 40), '  d')
    btn_shiftup = Button((690, 550), (45, 40), '  u')
    update = True
    hover = HoverTooltip(objects=[btn_back, btn_randomgame, btn_generate_game], topleft=(350, 570))

    running_opengame = True
    while running_opengame:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    scroll_down_pressed = btn_shiftdown.hovering(up)
                    scroll_up_pressed = btn_shiftup.hovering(up)
                    if btn_back.hovering(up):
                        running_opengame = False
                    elif btn_randomgame.hovering(up):
                        print('Starting a random game')
                        g, filename = get_random_game()
                        GameWindow(g, filename)
                        update = True
                    if btn_generate_game.hovering(up):
                        GenerateGameWindow()
                    elif scroll_down_pressed or scroll_up_pressed:
                        start, finish = shift_panels(
                            start, finish, shift=(-1 if scroll_down_pressed else 1), number_of_panels=len(panels))
                        panels9 = panels[start:finish]
                    else:
                        # here we handle clicking the panels
                        panel_number = what_rect_hover(up)
                        if panel_number is not None:
                            opened_game =  panels9[panel_number].data
                            game_number = opened_game['game_number']
                            filename = f'{game_number}.json'
                            g = load_game(filename)
                            GameWindow(g, filename)
                            update = True
                elif event.button in {4, 5}:  # mousewheel
                    wheel_up = event.button == 4
                    start, finish = shift_panels(
                        start, finish, shift=(1 if wheel_up else -1), number_of_panels=len(panels))
                    panels9 = panels[start:finish]

            elif event.type == pygame.QUIT:
                running_opengame = False
        
        if update:
            pygame.display.set_caption('Open game...')
            print('DF assembled')
            df = assemble_games_dataframe()
            panels = create_panels(df)
            start, finish = 0, 9
            panels9 = panels[start:finish]
            update = False
        
        btn_back.draw(screen, my_font)
        btn_randomgame.draw(screen, my_font)
        btn_shiftdown.draw(screen, my_font)
        btn_shiftup.draw(screen, my_font)
        btn_generate_game.draw(screen, my_font)

        display_panels(panels9)
        screen.blit(my_font.render('Game #', False,
                                   (255, 255, 255)), (15+10, 15))
        screen.blit(my_font.render('Nodes/Edges', False,
                                   (255, 255, 255)), (15+130, 15))
        screen.blit(my_font.render('# of plays', False,
                                   (255, 255, 255)), (15+270, 15))
        screen.blit(my_font.render('Least # of moves',
                                   False, (255, 255, 255)), (15+400, 15))
        screen.blit(my_font.render('Date created', False,
                                   (255, 255, 255)), (15+575, 15))

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        pygame.draw.rect(screen, WHITE, [10, 10, 780, 530], 4)
        pygame.display.update()


def GameWindow(g, filename=None):
    if filename is None:
        # in case the filename is so far unknown
        val = None
        best = None
    else:
        # in case an existing game is opened
        val = int(filename[:-5])
        with open(f'games/{val}.json',) as f:
            dat = json.load(f)
        if len(dat['plays']) > 0:
            best = min([len(play['moves']) for play in dat['plays']])
        else:
            best = None
    print(f'Game #{val} is started')

    pygame.display.set_caption('Game')
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))
    btn_save = Button(topleft=(30, 450), size=(100, 40), text='Save')
    btn_back = Button(topleft=(30, 510), size=(100, 40), text='Back')
    running_game = True
    is_victory = False
    only_once = True
    moves = []
    g_not_solved = deepcopy(g) # what the fuck is a deepcopy????

    while running_game:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if not field_rect.collidepoint(up):
                        if btn_save.hovering(up):
                            if not moves:
                                print('Save empty game')
                                filename = save_new_game(g)
                                btn_save.is_active = False
                            elif is_victory:
                                filename = save_finished_game(g_not_solved, moves, filename)
                                btn_save.is_active = False
                            val = int(filename[:-5])
                        elif btn_back.hovering(up):
                            running_game = False
                            break
                    elif not is_victory:
                        # this code makes old controls possible
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
                        # --------------------
                else:
                    down_bool, node_down = mouse_on_node(g, down)
                    up_bool, node_up = mouse_on_node(g, up)
                    if down_bool and not is_victory:
                        if event.button == 4:
                            print(f'Node {node_down} gives')
                            g.give(node_down)
                            moves.append((node_down, 'give'))
                        elif event.button == 5:
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
        display_prev_stats(val, best)
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
    pygame.display.set_caption('Options')

    show_indices = OPTIONS['show_node_ids']
    sort_by = OPTIONS['sort_by']
    sort_by_num = SORTBY_LIST.index(sort_by)
    print(sort_by_num)
    dummy = OPTIONS['dummy']

    btn_back = Button(topleft=(10, 550), size=(100, 40), 
                            text='Back', hover_text='go back to the menu (you clicked the save btn, right?)')
    btn_save = Button(topleft=(10, 500), size=(120, 40), 
                            text='Save', hover_text='saves the changes')
    btn_show_ind = Button(topleft=(15, 30), size=(120, 40), 
                            text='Indices', hover_text='when set to True shows nodes indices')
    btn_sort_by = Button(topleft=(15, 80), size=(120, 40), 
                            text='Sortby', hover_text='how...')
    cnt_dummy = Counter(topleft=(15, 130), size=(120, 40), 
                            text='dummy', value=dummy, hover_text='dummy counter')
    
    hover = HoverTooltip(objects=[btn_back, btn_save, btn_show_ind, btn_sort_by, cnt_dummy])

    running_options = True
    while running_options:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if btn_back.hovering(up):
                        running_options = False
                    elif btn_save.hovering(up):
                        print('Settings saved')
                        OPTIONS['show_node_ids'] = show_indices
                        OPTIONS['dummy'] = dummy
                        OPTIONS['sort_by'] = sort_by
                        with open('options.json', 'w') as f:
                            json.dump(OPTIONS, f)
                    elif btn_show_ind.hovering(up):
                        show_indices = not show_indices
                    elif btn_sort_by.hovering(up):
                        sort_by_num += 1
                        sort_by = SORTBY_LIST[sort_by_num % len(SORTBY_LIST)]
                elif event.button in {4,5}:
                    cnt_dummy.hovering(up, add=1 if event.button == 4 else -1)
                    dummy = cnt_dummy.value
            elif event.type == pygame.QUIT:
                running_options = False
        

        btn_back.draw(screen, my_font)
        btn_save.draw(screen, my_font)
        btn_show_ind.draw(screen, my_font)
        btn_sort_by.draw(screen, my_font)
        cnt_dummy.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # some text
        x, y = btn_show_ind.topleft
        screen.blit(my_font.render(str(show_indices), False, GREEN if show_indices else RED), 
                    (x + btn_show_ind.size[0] + 5, y + 13))
        screen.blit(my_font.render(sort_by, False, WHITE), 
                    (x + btn_show_ind.size[0] + 5, y + 58))

        # light yellow outline
        pygame.draw.rect(screen, (225, 240, 129), [0, 0, WIDTH, HEIGHT], 4)
        pygame.display.update()


def MenuWindow():
    pygame.display.set_caption('Menu')
    btn_play = Button((200, 50), (400, 100), 'PLAY', hover_text='splits into create/open/back')
    btn_play_create = Button((200, 50), (130, 100), 'create', is_active=False, 
                                is_visible=False, hover_text='click to open a sandbox')
    btn_play_open = Button((335, 50), (130, 100), 'open', is_active=False, 
                                is_visible=False, hover_text='open an existing game')
    btn_play_back = Button((470, 50), (130, 100), 'back', is_active=False, is_visible=False, hover_text='collapse')
    btn_options = Button((200, 250), (400, 100), 'OPTIONS', hover_text='lol indeed')
    btn_exit = Button((200, 450), (400, 100), 'EXIT', hover_text='you can click the red X btn though')
    hover = HoverTooltip(objects=[btn_play, btn_options, btn_exit, btn_play_back, 
                                        btn_play_create, btn_play_open])

    lol = False

    running_menu = True
    while running_menu:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if btn_play.hovering(up):
                    btn_play.is_active = False
                    btn_play.is_visible = False
                    btn_play_create.is_active = True
                    btn_play_open.is_active = True
                    btn_play_back.is_active = True
                    btn_play_create.is_visible = True
                    btn_play_open.is_visible = True
                    btn_play_back.is_visible = True
                elif btn_options.hovering(up):
                    print('Options')
                    OptionsWindow()
                    pygame.display.set_caption('Menu')
                elif btn_exit.hovering(up):
                    running_menu = False
                    # pygame.quit()
                elif btn_play_back.hovering(up):
                    btn_play.is_active = True
                    btn_play.is_visible = True
                    btn_play_create.is_active = False
                    btn_play_open.is_active = False
                    btn_play_back.is_active = False
                    btn_play_create.is_visible = False
                    btn_play_open.is_visible = False
                    btn_play_back.is_visible = False
                elif btn_play_create.hovering(up):
                    SandboxWindow()
                    pygame.display.set_caption('Menu')
                elif btn_play_open.hovering(up):
                    OpenGameWindow()
                    pygame.display.set_caption('Menu')
            elif event.type == pygame.QUIT:
                running_menu = False
                

        btn_play_create.draw(screen, my_font)
        btn_play_open.draw(screen, my_font)
        btn_play_back.draw(screen, my_font)
        btn_play.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # white outline
        pygame.draw.rect(screen, WHITE, [0, 0, WIDTH, HEIGHT], 4)
        if lol:
            screen.blit(my_font.render('lol', False, (255,255,255)), (500, 260))

        btn_options.draw(screen, my_font)
        btn_exit.draw(screen, my_font)
        pygame.display.update()


if __name__ == '__main__':
    MenuWindow()
