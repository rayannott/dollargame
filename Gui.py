import json
import pygame
from copy import deepcopy
from itertools import count

from ui_elements import Button, HoverTooltip, Panel, Counter, TextInput
from Graph import DGGraph, load_game, generate_game, find_best, show_instruction
from utils import *
from commands import Commands


pygame_icon = pygame.image.load('icon.png')
pygame.display.set_icon(pygame_icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
default_font = pygame.font.SysFont('cambria', 20)
my_font = pygame.font.SysFont('UASQUARE.ttf', 30)
my_font_bigger = pygame.font.SysFont('UASQUARE.ttf', 36)
my_font_hover = pygame.font.SysFont('UASQUARE.ttf', 26)


# -----------display functions----------------

def create_panels(df):
    panels = []
    for dat in df:
        panels.append(Panel(data=dat))
    return panels


def display_panels(panels):
    for ind, panel in enumerate(panels):
        panel.draw(topleft=(17, PANEL_HEIGHT + ind*54),
                   screen=screen, font=my_font)


def display_prev_stats(game_number, best=None):
    dots = '...'
    screen.blit(my_font.render(
        f'Game #{game_number if game_number is not None else dots}', False, GREEN), (20, 110))
    if not best is None:
        screen.blit(my_font.render(f'Best = {best}', False, GREEN), (20, 130))


def display_labels(G, sandbox, num_moves=None, y_shift_genus_bank=False):
    # node values
    for n in G.nodes():
        current_value = G.nodes[n]['val']
        pos = G.nodes[n]['pos']
        screen.blit(my_font_bigger.render(str(current_value), False,
                    THEME['def'] if current_value >= 0 else RED), (pos[0]+20, pos[1]+12))
        if OPTIONS['show_node_ids']:
            text_node_indices = my_font.render(
                str(n), False, THEME['indices_text'])
            screen.blit(text_node_indices, (pos[0]-36, pos[1]-14))

    # display parameters (genus, bank) and indicator
    shift = 90 if y_shift_genus_bank else 0
    screen.blit(my_font.render(
        f'GENUS = {G.genus}', False, THEME['def']), (20, 40 + shift))
    screen.blit(my_font.render(
        f'BANK = {G.bank}', False, THEME['def']), (20, 60 + shift))

    # sandbox if .. True else game
    if sandbox:
        valid = is_game_valid(G)
        screen.blit(my_font.render(
            'valid' if valid else 'invalid', False, GREEN if valid else RED), (20, 80))
    else:
        if not y_shift_genus_bank:
            screen.blit(my_font.render(
                f'MOVES = {num_moves}', False, THEME['def']), (20, 80 + shift))


def display_nodes_edges(G):
    # nodes
    for node in G.nodes:
        pygame.draw.circle(screen, THEME['def'],
                           G.nodes[node]['pos'], 20, 2)
    # edges
    for s, f in G.edges:
        pygame.draw.line(screen, THEME['def'],
                         G.nodes[s]['pos'],
                         G.nodes[f]['pos'], 2)


# ----------------WINDOWS --------------------

def SandboxWindow():
    pygame.display.set_caption('Game creation')
    running = True
    holding_down = False
    holding_with_shift = False
    down_bool = False
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))

    G = DGGraph()
    cnt = count(0)
    btn_generate = Button(topleft=(15, 230), size=(135, 40),
                          text='Generate', hover_text='generate a new game')
    cnt_nodes = Counter(topleft=(15, 280), size=(110, 40), value=6, bounds=(3, 100),
                        text='Nodes', hover_text='enter the number of nodes')
    cnt_b_minus_g = Counter(topleft=(15, 330), size=(110, 40), value=2, bounds=(0, 100),
                            text='B-G', hover_text='bank - genus; 0 is the most difficult (no extra dollars)')
    btn_clear = Button(topleft=(30, 410), size=(100, 40),
                       text='Clear', hover_text='clears the field')
    btn_proceed = Button(topleft=(30, 460), size=(100, 40),
                         text='Proceed', is_active=False, hover_text='play!')
    btn_discard = Button(topleft=(30, 510), size=(100, 40), text='Discard',
                         hover_text='go back (loses progress)')
    hover = HoverTooltip(objects=[
                         btn_proceed, btn_discard, btn_generate, cnt_b_minus_g, cnt_nodes, btn_clear])

    # Game creation loop
    while running:
        screen.fill(THEME['background'])
        for event in pygame.event.get():
            if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    down = pygame.mouse.get_pos()
                    holding_down = True
                    down_bool, node_down = mouse_on_node(G, down)
                elif event.type == pygame.MOUSEBUTTONUP:

                    holding_down = False
                    up = pygame.mouse.get_pos()
                    if not field_rect.collidepoint(up):
                        if event.button == 1:
                            if btn_proceed.hovering(up):
                                GameWindow(G)
                                # pygame.display.set_caption('Game creation')
                                running = False
                            elif btn_generate.hovering(up):
                                print('Game was generated')
                                G = generate_game(number_of_nodes=cnt_nodes.value,
                                                  bank_minus_genus=cnt_b_minus_g.value,
                                                  display_layout=OPTIONS['layout'])
                                cnt = count(G.number_of_nodes())
                                btn_proceed.is_active = True
                            elif btn_discard.hovering(up):
                                running = False
                            elif btn_clear.hovering(up):
                                G = DGGraph()
                                cnt = count(0)
                        elif event.button in {4, 5}:
                            cnt_nodes.hovering(
                                up, add=1 if event.button == 4 else -1)
                            cnt_b_minus_g.hovering(
                                up, add=1 if event.button == 4 else -1)
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
                                    remove_node(G, node_up)
                                else:
                                    if (node_down, node_up) in G.edges:
                                        remove_edge(G, node_down, node_up)
                                    else:
                                        create_edge(G, node_down, node_up)
                        else:
                            if dist(down, up) < 20 and far_enough_from_nodes(G, down):
                                create_node(G, next(cnt), down)
                elif event.type == pygame.QUIT:
                    running = False
            else:
                # moving the nodes
                if event.type == pygame.MOUSEBUTTONDOWN:
                    down_shift = pygame.mouse.get_pos()
                    holding_with_shift = True
                    down_bool_shift, node_down_shift = mouse_on_node(
                        G, down_shift)
                elif event.type == pygame.MOUSEBUTTONUP:
                    holding_with_shift = False

        # moving the nodes
        if holding_with_shift and down_bool_shift:
            G.nodes[node_down_shift]['pos'] = pygame.mouse.get_pos()

        display_labels(G, sandbox=True)
        display_nodes_edges(G)

        # aesthetics (when drawing edges)
        if holding_down:
            pos = pygame.mouse.get_pos()
            if down_bool:
                hovering_node_bool, hovering_node_number = mouse_on_node(
                    G, pos)
                if hovering_node_bool:
                    color = RED if (
                        node_down, hovering_node_number) in G.edges else (120, 205, 0)
                    pygame.draw.line(screen, color,
                                     G.nodes[node_down]['pos'], G.nodes[hovering_node_number]['pos'], 2)
                else:
                    pygame.draw.line(screen, (150, 150, 150),
                                     G.nodes[node_down]['pos'], pos, 2)

        btn_proceed.is_active = is_game_valid(G)
        btn_proceed.draw(screen, my_font)
        btn_discard.draw(screen, my_font)
        btn_generate.draw(screen, my_font)
        btn_clear.draw(screen, my_font)
        cnt_nodes.draw(screen, my_font)
        cnt_b_minus_g.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # purple outline
        pygame.draw.rect(screen, (213, 88, 251), [0, 0, WIDTH, HEIGHT], 4)
        # sandbox field
        pygame.draw.rect(screen, THEME['field_outline'], [
            WIDTH*0.2, 4, WIDTH*0.8-4, HEIGHT-8], 2)
        pygame.display.update()


def OpenGameWindow():
    print('OpenGameWindow is opened')
    btn_back = Button((10, 550), (100, 40), 'back',
                      hover_text='go back to menu')
    btn_randomgame = Button((120, 550), (100, 40), 'random',
                            hover_text='start with a random saved game')
    btn_shiftdown = Button((745, 550), (45, 40), '  d')
    btn_shiftup = Button((690, 550), (45, 40), '  u')
    update = True
    hover = HoverTooltip(
        objects=[btn_back, btn_randomgame], topleft=(240, 570))

    running_opengame = True
    while running_opengame:
        screen.fill(THEME['background'])
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
                        if g is not None:
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
                            opened_game = panels9[panel_number].data
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
                                   THEME['def']), (15+10, 15))
        screen.blit(my_font.render('Nodes/Edges', False,
                                   THEME['def']), (15+130, 15))
        screen.blit(my_font.render('# of plays', False,
                                   THEME['def']), (15+270, 15))
        screen.blit(my_font.render('Least # of moves',
                                   False, THEME['def']), (15+400, 15))
        screen.blit(my_font.render('Date created', False,
                                   THEME['def']), (15+575, 15))

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        pygame.draw.rect(screen, THEME['def'], [10, 10, 780, 530], 4)
        pygame.display.update()


def GameWindow(g, filename=None):
    # TODO: display best possible score (optional)
    pygame.display.set_caption('Game')
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))

    btn_best = Button(topleft=(30, 390), size=(100, 40),
                      text='Best', is_active=OPTIONS['show_best_possible'])
    btn_save = Button(topleft=(30, 450), size=(100, 40), text='Save')
    btn_back = Button(topleft=(30, 510), size=(100, 40), text='Back')
    hover = HoverTooltip(objects=[btn_best, btn_save, btn_back])

    if filename is None:
        # in case the filename is so far unknown
        val = None
        best = None
    else:
        # in case an existing game is opened
        btn_save.is_active = False
        val = int(filename[:-5])
        with open(f'games/{val}.json',) as f:
            dat = json.load(f)
        if len(dat['plays']) > 0:
            best = min([len(play['moves']) for play in dat['plays']])
        else:
            best = None

    print(f'Game #{val} is started')
    running_game = True
    is_victory = False
    only_once = True
    show_best_moves = False
    moves = []
    g_not_solved = deepcopy(g)  # what the fuck is a deepcopy????

    if OPTIONS['show_best_possible']:
        moves_best, min_num_moves = find_best(g, N=100)
        # output optimal strategy to the console
        print(', '.join(show_instruction(moves_best)))
        # TODO: threading?

    while running_game:
        screen.fill(THEME['background'])
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if not field_rect.collidepoint(up):
                        if btn_save.hovering(up):
                            if is_victory:
                                filename = save_finished_game(
                                    g_not_solved, moves, filename)
                                btn_save.is_active = False
                            else:
                                print('Save empty game')
                                filename = save_new_game(g_not_solved)
                                btn_save.is_active = False
                            val = int(filename[:-5])
                        elif btn_back.hovering(up):
                            running_game = False
                            break
                        elif btn_best.hovering(up):
                            show_best_moves = not show_best_moves
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
                    up_bool, _ = mouse_on_node(g, up)
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

        btn_save.draw(screen, my_font)
        btn_back.draw(screen, my_font)
        display_prev_stats(val, best)
        display_labels(g, sandbox=False, num_moves=len(moves))
        display_nodes_edges(g)

        if OPTIONS['show_best_possible']:
            btn_best.draw(screen, my_font)
            screen.blit(my_font.render(
                f'best possible', False, YELLOW), (20, 157))
            screen.blit(my_font.render(
                f'score: {min_num_moves}', False, YELLOW), (20, 175))

            if show_best_moves:
                for i, hint in enumerate(show_instruction(moves_best)):
                    screen.blit(default_font.render(f'{hint}', False, YELLOW),
                                (15 + i//10 * 72, 193 + (i-i//10*10)*18))

        # orange outline (when not solved)
        pygame.draw.rect(screen, THEME['playing_outline'] if not is_victory else THEME['won_outline'], [
                         0, 0, WIDTH, HEIGHT], 4)
        # play field
        pygame.draw.rect(screen, THEME['field_outline'], [
                         WIDTH*0.2, 4, WIDTH*0.8-4, HEIGHT-8], 2)
        pygame.display.update()


def OptionsWindow():
    pygame.display.set_caption('Options')
    show_indices = OPTIONS['show_node_ids']
    show_best_possible = OPTIONS['show_best_possible']
    sort_by = OPTIONS['sort_by']
    sort_by_num = SORTBY_LIST.index(sort_by)
    layout = OPTIONS['layout']
    layout_num = LAYOUT_LIST.index(layout)
    theme = OPTIONS['theme']
    theme_num = THEME_LIST.index(theme)
    cmdline = Commands()

    btn_back = Button(topleft=(10, 550), size=(100, 40),
                      text='back', hover_text='go back to the menu (you did click the save btn, right?)')
    btn_save = Button(topleft=(10, 500), size=(120, 40),
                      text='save', hover_text='save the changes')
    btn_show_ind = Button(topleft=(10, 10), size=(120, 40),
                          text='indices', hover_text='show nodes\' indices')
    btn_show_best_possible = Button(topleft=(10, 60), size=(120, 40),
                                    text='Best', hover_text='show least possible number of moves for the current game')
    btn_sort_by = Button(topleft=(10, 110), size=(120, 40),
                         text='sort by', hover_text='choose how to sort games in the game opening window')
    btn_layout = Button(topleft=(10, 160), size=(120, 40),
                        text='layout', hover_text='choose a layout for a generated game')
    btn_theme = Button(topleft=(10, 210), size=(120, 40),
                       text='theme', hover_text='change the theme (dark/light) (needs restarting)')
    txt_console = TextInput(topleft=(330, 10), size=(460, 40),
                            text='', hover_text=f'this is the command line', text_placement_specifier='input_text')

    hover = HoverTooltip(objects=[btn_back, btn_save, btn_show_ind,
                                  btn_sort_by, btn_layout, btn_show_best_possible, txt_console, btn_theme], topleft=(130, 567))

    running_options = True
    while running_options:
        screen.fill(THEME['background'])
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
                txt_console.input_mode = False
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if btn_back.hovering(up):
                        running_options = False
                    elif btn_save.hovering(up):
                        print('Settings saved')
                        OPTIONS['show_node_ids'] = show_indices
                        OPTIONS['sort_by'] = sort_by
                        OPTIONS['layout'] = layout
                        OPTIONS['show_best_possible'] = show_best_possible
                        OPTIONS['theme'] = theme
                        with open('options.json', 'w') as f:
                            json.dump(OPTIONS, f)
                        cmdline.log('info: saved successfully')
                    elif btn_show_ind.hovering(up):
                        show_indices = not show_indices
                    elif btn_show_best_possible.hovering(up):
                        show_best_possible = not show_best_possible
                    elif btn_sort_by.hovering(up):
                        sort_by_num += 1
                        sort_by = SORTBY_LIST[sort_by_num % len(SORTBY_LIST)]
                    elif btn_layout.hovering(up):
                        layout_num += 1
                        layout = LAYOUT_LIST[layout_num % len(LAYOUT_LIST)]
                    elif btn_theme.hovering(up):
                        theme_num += 1
                        theme = THEME_LIST[theme_num % len(THEME_LIST)]
                        cmdline.log(
                            f'info: save and then restart the game to & update the theme to [{theme}]')

                    elif txt_console.hovering(up):
                        txt_console.input_mode = not txt_console.input_mode
            elif event.type == pygame.KEYDOWN:
                if txt_console.input_mode:
                    if event.key == pygame.K_BACKSPACE:
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            tmp = txt_console.text.split()
                            if tmp:
                                tmp.pop()
                                txt_console.text = ' '.join(tmp)
                        else:
                            txt_console.text = txt_console.text[:-1]
                    elif event.key == pygame.K_RETURN and txt_console.text:
                        # commands processing
                        try:
                            cmdline.log('>'+txt_console.text)
                            cmdline.console_history.append(txt_console.text)
                            command, params, options = cmdline.process(
                                txt_console.text)
                            if command != 'clear':
                                messages = cmdline.cmds[command]['function'](
                                    params, options)
                                cmdline.log(messages)
                            else:
                                cmdline.console_log = []
                        except KeyError as e:
                            print('error:', e)
                            cmdline.log(str(e)[1:-1])
                        txt_console.text = ''
                    elif event.key == pygame.K_ESCAPE:
                        txt_console.input_mode = False
                    elif event.key == pygame.K_UP:
                        txt_console.text = cmdline.last_command()
                    elif event.key == pygame.K_DOWN:
                        txt_console.text = ''
                    else:
                        txt_console.text += event.unicode if event.unicode in ALLOWED_SYMBOLS and len(
                            txt_console.text) < 33 else ''
                elif event.key == pygame.K_RETURN:
                    txt_console.input_mode = True
            elif event.type == pygame.QUIT:
                running_options = False

        btn_back.draw(screen, my_font)
        btn_save.draw(screen, my_font)
        btn_show_ind.draw(screen, my_font)
        btn_show_best_possible.draw(screen, my_font)
        btn_sort_by.draw(screen, my_font)
        btn_layout.draw(screen, my_font)
        btn_theme.draw(screen, my_font)
        txt_console.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # some text
        x, y = btn_show_ind.topleft
        screen.blit(my_font.render(str(show_indices), False, GREEN if show_indices else RED),
                    (x + btn_show_ind.size[0] + 5, y + 13))
        screen.blit(my_font.render(str(show_best_possible), False, GREEN if show_best_possible else RED),
                    (x + btn_show_ind.size[0] + 5, y + 60))
        screen.blit(my_font.render(sort_by, False, THEME['def']),
                    (x + btn_show_ind.size[0] + 5, y + 108))
        screen.blit(my_font.render(layout, False, THEME['def']),
                    (x + btn_show_ind.size[0] + 5, y + 160))
        screen.blit(my_font.render(theme, False, THEME['def']),
                    (x + btn_show_ind.size[0] + 5, y + 210))

        # light yellow outline
        pygame.draw.rect(screen, THEME['options_outline'], [
                         0, 0, WIDTH, HEIGHT], 4)
        # console logs
        pygame.draw.rect(screen, THEME['def'], [330, 60, 460, 530], 4)
        for i, log in enumerate(cmdline.console_log[-22:]):
            screen.blit(my_font.render(log, False, THEME['def']),
                        (337, 65 + i*23))
        pygame.display.update()


def MenuWindow():
    pygame.display.set_caption('Menu')
    D, d, h = 50, 44, 90
    btn_create = Button((200, D + (h+d)*0), (400, h),
                        'CREATE', hover_text='open a sandbox')
    btn_open = Button((200, D + (h+d)*1), (400, h), 'OPEN',
                      hover_text='open an existing game')
    btn_options = Button((200, D + (h+d)*2), (400, h),
                         'OPTIONS', hover_text='configure soem shit')
    btn_exit = Button((200, D + (h+d)*3), (400, h), 'EXIT')
    hover = HoverTooltip(objects=[btn_options, btn_create, btn_open])

    running_menu = True
    while running_menu:
        screen.fill(THEME['background'])
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if btn_options.hovering(up):
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
        btn_options.draw(screen, my_font)
        btn_exit.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # white outline
        pygame.draw.rect(screen, THEME['def'], [0, 0, WIDTH, HEIGHT], 4)
        pygame.display.update()


if __name__ == '__main__':
    MenuWindow()
