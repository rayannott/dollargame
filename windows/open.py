import pygame

from utils import *
from pygame_setup import *
from ui_elements import Button, HoverTooltip
from sfx import play_sfx
from windows.game import GameWindow
from graph import get_random_game, load_game



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
    clock = pygame.time.Clock()
    mouse = None
    
    kb_controls = -1; existing_game_file = False
    GAME_FILES = get_list_of_game_files()

    games_previews_cache: dict[int, tuple[np.array, np.array]] = {} # game_number -> (nodes_positions, edges)

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
                        play_sfx('click')
                        running_opengame = False
                    elif btn_randomgame.hovering(up):
                        play_sfx('click')
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
                    play_sfx('scroll_short_click')
                    wheel_up = event.button == 4
                    start, finish = shift_panels(
                        start, finish, shift=(1 if wheel_up else -1), number_of_panels=len(panels))
                    panels9 = panels[start:finish]
            elif event.type == pygame.QUIT:
                running_opengame = False
            elif event.type == pygame.KEYDOWN:
                pressed_number = PYGAME_KEYS.get(event.key)
                if pressed_number is not None:
                    if kb_controls == -1:
                        kb_controls = pressed_number
                    else:
                        kb_controls *= 10; kb_controls += pressed_number
                else:
                    if event.key == pygame.K_RETURN:
                        if existing_game_file:
                            filename = f'{kb_controls}.json'
                            g = load_game(filename)
                            GameWindow(g, filename)
                            update = True
                            kb_controls = -1
                        else:
                            kb_controls = -1
                    elif event.key == pygame.K_BACKSPACE:
                        if kb_controls != -1:
                            kb_controls //= 10
                        if kb_controls == 0:
                            kb_controls = -1
                    elif event.key == pygame.K_ESCAPE:
                        kb_controls = -1
                existing_game_file = f'{kb_controls}.json' in GAME_FILES
                    

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
        blit('Game #', (15+10, 15), THEME['def'])
        blit('Nodes/Edges', (15+130, 15), THEME['def'])
        blit('# of plays', (15+270, 15), THEME['def'])
        blit('Least # of moves', (15+400, 15), THEME['def'])
        blit('Date created', (15+575, 15), THEME['def'])
        blit(f'{kb_controls if kb_controls != -1 else ""}', (608, 562), GREEN if existing_game_file else RED)
        
        pygame.draw.rect(screen, THEME['def'], [10, 10, 780, 530], 4)

        if mouse and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            panel_number = what_rect_hover(mouse)
            if panel_number is not None:
                game_number = panels9[panel_number].data['game_number']
                filename = f'{game_number}.json'

                graph_to_display = games_previews_cache.get(game_number)
                if graph_to_display is None:
                    graph_to_display = pull_transform_positions_edges_from_gamefile(filename)
                    games_previews_cache[game_number] = graph_to_display
                
                display_graph_preview(*graph_to_display, current_mouse_pos=np.array(mouse, dtype=float))        

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        pygame.display.update()
        clock.tick(FRAMERATE)



