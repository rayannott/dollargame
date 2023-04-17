from copy import deepcopy

import pygame
from graph import find_best, show_instruction, node_gives, node_takes

from utils import *
from pygame_setup import *
from ui_elements import Button, HoverTooltip, Panel, Counter, TextInput
import animation
from sfx import play_sfx



def GameWindow(g, filename=None):
    pygame.display.set_caption('Game')
    field_rect = pygame.Rect((WIDTH*0.2, 4), (WIDTH*0.8-4, HEIGHT-8))

    btn_best = Button(topleft=(30, 390), size=(100, 40),
                      text='Best', is_active=OPTIONS['show_best_possible'], hover_text='show solution by algo')
    btn_save = Button(topleft=(30, 450), size=(100, 40), text='Save', hover_text='save this solution')
    btn_back = Button(topleft=(30, 510), size=(100, 40), text='Back', hover_text='go back (looses progress)')
    btns = [btn_best, btn_save, btn_back]
    hover = HoverTooltip(objects=btns)
    clock = pygame.time.Clock()

    if filename is None:
        # in case the filename is so far unknown
        val = None
        best = None
    else:
        # in case an existing game is opened
        btn_save.is_active = False
        val = int(filename[:-5])
        with open(os.path.join(GAMES_DIR, filename)) as f:
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
    g_not_solved = deepcopy(g)
    once = True

    anim = animation.Animation()
    moves_best = None

    kb_controls = -1; prev_node_index = None


    while running_game:
        screen.fill(THEME['background'])
        dt = clock.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                down = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                up = pygame.mouse.get_pos()
                if event.button == 1:
                    if not field_rect.collidepoint(up):
                        if btn_save.hovering(up):
                            play_sfx('click')
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
                            play_sfx('click')
                            running_game = False
                            break
                        elif btn_best.hovering(up):
                            play_sfx('click')
                            show_best_moves = not show_best_moves
                    elif not is_victory:
                        # this code makes old controls possible
                        down_bool, node_down = mouse_on_node(g, down)
                        up_bool, node_up = mouse_on_node(g, up)
                        if down_bool:
                            if not up_bool:
                                if down[1] > up[1]:
                                    node_gives(node_down, g, anim, moves)
                                else:
                                    node_takes(node_down, g, anim, moves)
                        is_victory = g.is_victory()
                else:
                    down_bool, node_down = mouse_on_node(g, down)
                    up_bool, _ = mouse_on_node(g, up)
                    if down_bool and not is_victory:
                        if event.button == 4:
                            node_gives(node_down, g, anim, moves)
                        elif event.button == 5:
                            node_takes(node_down, g, anim, moves)
                    is_victory = g.is_victory()

            elif event.type == pygame.QUIT:
                running_game = False
            
            elif event.type == pygame.KEYDOWN:
                if is_victory:
                    continue
                pressed_number = PYGAME_KEYS.get(event.key)
                if pressed_number is not None:
                    if kb_controls == -1:
                        kb_controls = pressed_number
                    else:
                        kb_controls *= 10; kb_controls += pressed_number
                else:
                    if event.key == pygame.K_UP:
                        chosen_node = None
                        if kb_controls != -1:
                            chosen_node = kb_controls
                        elif prev_node_index is not None:
                            chosen_node = prev_node_index
                        if not chosen_node in g.nodes:
                            kb_controls = -1
                            continue
                        node_gives(chosen_node, g, anim, moves)
                        prev_node_index = chosen_node
                        kb_controls = -1
                    elif event.key == pygame.K_DOWN:
                        chosen_node = None
                        if kb_controls != -1:
                            chosen_node = kb_controls
                        elif prev_node_index is not None:
                            chosen_node = prev_node_index
                        if not chosen_node in g.nodes:
                            kb_controls = -1
                            continue
                        node_takes(chosen_node, g, anim, moves)
                        prev_node_index = chosen_node
                        kb_controls = -1
                    elif event.key == pygame.K_RETURN:
                        if moves_best is None or moves: continue
                        print('solving...')
                        for node, move in moves_best.items():
                            if move > 0:
                                for _ in range(abs(move)):
                                    node_takes(node, g, anim, moves, silent=True)
                            elif move < 0:
                                for _ in range(abs(move)):
                                    node_gives(node, g, anim, moves, silent=True)
                    is_victory = g.is_victory()

        if is_victory and only_once:
            print('You won!')
            play_sfx('victory')
            btn_save.is_active = True
            only_once = False

        btn_save.draw(screen, my_font)
        btn_back.draw(screen, my_font)
        mouse = pygame.mouse.get_pos()
        _, on_node = mouse_on_node(g, mouse)
        hover.display(mouse, screen, my_font_hover)
        display_prev_stats(val, best)
        display_nodes_edges(g, on_node)
        display_labels(g, sandbox=False, num_moves=len(moves))
        anim.draw(screen)
        anim.tick()

        screen.blit(my_font.render(
            f'[{kb_controls if kb_controls != -1 else (prev_node_index if prev_node_index is not None else "")}]', 
            False, '#FFFFFF'), 
            (10, HEIGHT-24))

        if moves_best is not None and OPTIONS['show_best_possible']:
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

        if once and OPTIONS['show_best_possible']:
                moves_best, min_num_moves = find_best(g, N=100)
                # output optimal strategy to the console
                print(', '.join(show_instruction(moves_best)))
                once = False
