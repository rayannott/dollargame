import json
import pygame
from Graph import DGGraph, load_game, generate_game
from utils import *
from itertools import count
from math import sqrt
from ui_elements import Button, HoverTooltip, Panel, Counter, PANEL_HEIGHT
from datetime import datetime
from random import choice
from copy import deepcopy

WHITE, GREEN, RED = (255, 255, 255), (0, 255, 0), (255, 0, 0)
RECTS = [pygame.Rect([15, PANEL_HEIGHT + ind*(PANEL_HEIGHT + 4), 770, PANEL_HEIGHT])
         for ind in range(9)]
WIDTH, HEIGHT = 800, 600
SORTBY_LIST = ['date_created', 'num_of_plays', 'best_score']
LAYOUT_LIST = ['planar', 'shell']

pygame_icon = pygame.image.load('icon.png')
pygame.display.set_icon(pygame_icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
my_font = pygame.font.SysFont('UASQUARE.ttf', 30)
my_font_bigger = pygame.font.SysFont('UASQUARE.ttf', 36)
my_font_hover = pygame.font.SysFont('UASQUARE.ttf', 26)

with open('options.json', 'r') as f:
    OPTIONS = json.load(f)


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


def display_labels(G, sandbox, num_moves=None, y_shift_genus_bank=False):
    # node values
    for n in G.nodes():
        current_value = G.nodes[n]['val']
        pos = G.nodes[n]['pos']
        screen.blit(my_font_bigger.render(str(current_value), False,
                    WHITE if current_value >= 0 else RED), (pos[0]+20, pos[1]+12))
        if OPTIONS['show_node_ids']:
            text_node_indices = my_font.render(str(n), False, (225, 240, 129))
            screen.blit(text_node_indices, (pos[0]-36, pos[1]-8))
    
    # display parameters (genus, bank) and indicator
    shift = 90 if y_shift_genus_bank else 0
    screen.blit(my_font.render(f'GENUS = {G.genus}', False, WHITE), (20, 40 + shift))
    screen.blit(my_font.render(f'BANK = {G.bank}', False, WHITE), (20, 60 + shift))

    # sandbox if .. True else game
    if sandbox:
        valid = is_game_valid(G)
        screen.blit(my_font.render(
            'valid' if valid else 'invalid', False, GREEN if valid else RED), (20, 80))
    elif not y_shift_genus_bank:
        screen.blit(my_font.render(f'MOVES = {num_moves}', False, WHITE), (20, 80 + shift))


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
    pygame.display.set_caption('Generate game...')
    btn_back = Button(topleft=(10, 550), size=(100, 40), 
                            text='Back', hover_text='go back')
    btn_generate = Button(topleft=(10, 500), size=(120, 40), 
                            text='Generate', hover_text='generate a new graph')
    btn_proceed = Button(topleft=(10, 450), size=(120, 40), is_active=False, 
                            text='Proceed', hover_text='pick this game')
    cnt_nodes = Counter(topleft=(10, 30), size=(100, 40), value=6,
                            text='Nodes', hover_text='enter a number of nodes')
    cnt_b_minus_g = Counter(topleft=(10, 80), size=(100, 40), value=2,
                            text='B-G', hover_text='bank - genus')
    
    hover = HoverTooltip(objects=[btn_back, btn_generate, btn_proceed, cnt_nodes, cnt_b_minus_g], 
                        topleft=(165, 570))
    
    # current generated game to display
    G = None

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
                        # TODO: generate only winnable games
                        print('Game was generated')
                        G = generate_game(number_of_nodes=cnt_nodes.value, 
                                            bank_minus_genus=cnt_b_minus_g.value, 
                                            display_layout=OPTIONS['layout'])
                        btn_proceed.is_active = True
                    elif btn_proceed.hovering(up):
                        GameWindow(G)
                    elif cnt_nodes.hovering(up, press=True):
                        print('Value is', cnt_nodes.value)
                    elif cnt_b_minus_g.hovering(up, press=True):
                        print('Value is', cnt_b_minus_g.value)
                elif event.button in {4,5}:
                    cnt_nodes.hovering(up, add=1 if event.button == 4 else -1)
                    cnt_b_minus_g.hovering(up, add=1 if event.button == 4 else -1)
            elif event.type == pygame.QUIT:
                running_generation = False
        

        btn_back.draw(screen, my_font)
        btn_generate.draw(screen, my_font)
        btn_proceed.draw(screen, my_font)
        cnt_nodes.draw(screen, my_font)
        cnt_b_minus_g.draw(screen, my_font)
        
        # display graph
        if not G is None:
            display_nodes_edges(G)
            display_labels(G, sandbox=False, y_shift_genus_bank=True)
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
    btn_shiftdown = Button((745, 550), (45, 40), '  d')
    btn_shiftup = Button((690, 550), (45, 40), '  u')
    update = True
    hover = HoverTooltip(objects=[btn_back, btn_randomgame], topleft=(350, 570))

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
                    if scroll_down_pressed or scroll_up_pressed:
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
    layout = OPTIONS['layout']
    layout_num = LAYOUT_LIST.index(layout)
    dummy = OPTIONS['dummy']

    btn_back = Button(topleft=(10, 550), size=(100, 40), 
                            text='Back', hover_text='go back to the menu (you clicked the save btn, right?)')
    btn_save = Button(topleft=(10, 500), size=(120, 40), 
                            text='Save', hover_text='saves the changes')
    btn_show_ind = Button(topleft=(15, 30), size=(120, 40), 
                            text='Indices', hover_text='when set to True shows nodes\' indices')
    btn_sort_by = Button(topleft=(15, 80), size=(120, 40), 
                            text='Sortby', hover_text='choose how to sort games in the game opening window')
    btn_layout = Button(topleft=(15, 130), size=(120, 40), 
                            text='Layout', hover_text='choose a layout for a generated game')
    cnt_dummy = Counter(topleft=(15, 180), size=(120, 40), 
                            text='dummy', value=dummy, hover_text='a dummy counter')
    
    hover = HoverTooltip(objects=[btn_back, btn_save, btn_show_ind, btn_sort_by, btn_layout, cnt_dummy])

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
                        OPTIONS['layout'] = layout
                        with open('options.json', 'w') as f:
                            json.dump(OPTIONS, f)
                    elif btn_show_ind.hovering(up):
                        show_indices = not show_indices
                    elif btn_sort_by.hovering(up):
                        sort_by_num += 1
                        sort_by = SORTBY_LIST[sort_by_num % len(SORTBY_LIST)]
                    elif btn_layout.hovering(up):
                        layout_num += 1
                        layout = LAYOUT_LIST[layout_num % len(LAYOUT_LIST)]
                elif event.button in {4,5}:
                    cnt_dummy.hovering(up, add=1 if event.button == 4 else -1)
                    dummy = cnt_dummy.value
            elif event.type == pygame.QUIT:
                running_options = False
        

        btn_back.draw(screen, my_font)
        btn_save.draw(screen, my_font)
        btn_show_ind.draw(screen, my_font)
        btn_sort_by.draw(screen, my_font)
        btn_layout.draw(screen, my_font)
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
        screen.blit(my_font.render(layout, False, WHITE), 
                    (x + btn_show_ind.size[0] + 5, y + 103))

        # light yellow outline
        pygame.draw.rect(screen, (225, 240, 129), [0, 0, WIDTH, HEIGHT], 4)
        pygame.display.update()


def MenuWindow():
    pygame.display.set_caption('Menu')
    D, d, h = 50, 30, 76
    btn_create = Button((200, D +(h+d)*0), (400, h), 'CREATE', hover_text='click to open a sandbox')
    btn_generate = Button((200, D +(h+d)*1), (400, h), 'GENERATE', hover_text='generate a game')
    btn_open = Button((200, D +(h+d)*2), (400, h), 'OPEN', hover_text='open an existing game')
    btn_options = Button((200, D +(h+d)*3), (400, h), 'OPTIONS', hover_text='lol indeed')
    btn_exit = Button((200, D +(h+d)*4), (400, h), 'EXIT', hover_text='you can click the red X btn though')
    hover = HoverTooltip(objects=[btn_generate, btn_options, btn_exit, btn_create, btn_open])

    running_menu = True
    while running_menu:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if btn_generate.hovering(up):
                    GenerateGameWindow()
                    pygame.display.set_caption('Menu')
                elif btn_options.hovering(up):
                    print('Options')
                    OptionsWindow()
                    pygame.display.set_caption('Menu')
                elif btn_exit.hovering(up):
                    running_menu = False
                    # pygame.quit()
                elif btn_create.hovering(up):
                    SandboxWindow()
                    pygame.display.set_caption('Menu')
                elif btn_open.hovering(up):
                    OpenGameWindow()
                    pygame.display.set_caption('Menu')
            elif event.type == pygame.QUIT:
                running_menu = False
                

        btn_create.draw(screen, my_font)
        btn_open.draw(screen, my_font)
        btn_generate.draw(screen, my_font)
        btn_options.draw(screen, my_font)
        btn_exit.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # white outline
        pygame.draw.rect(screen, WHITE, [0, 0, WIDTH, HEIGHT], 4)
        pygame.display.update()


if __name__ == '__main__':
    MenuWindow()
