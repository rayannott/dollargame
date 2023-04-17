

import pygame

from utils import *
from pygame_setup import *
from commands import Commands
from ui_elements import Button, HoverTooltip, Panel, Counter, TextInput
from sfx import bg_music_set_vol, play_bg_music, play_sfx, set_sfx_volume


def OptionsWindow():
    pygame.display.set_caption('Options')
    sort_by_num = SORTBY_LIST.index(OPTIONS['sort_by'])
    layout_num = LAYOUT_LIST.index(OPTIONS['layout'])
    theme_num = THEME_LIST.index(OPTIONS['theme'])
    cmdline = Commands()
    clock = pygame.time.Clock()

    btn_back = Button(topleft=(10, 550), size=(100, 40),
                        text='Back', hover_text='go back to the menu (you did click the save btn, right?)')
    btn_save = Button(topleft=(10, 500), size=(120, 40),
                        text='Save', hover_text='save the changes')
    btn_show_ind = Button(topleft=(10, 10), size=(120, 40),
                        text='Indices', hover_text='show nodes\' indices')
    btn_show_best_possible = Button(topleft=(10, 60), size=(120, 40),
                        text='Best', hover_text='show least possible number of moves for the current game')
    btn_sort_by = Button(topleft=(10, 110), size=(120, 40),
                        text='Sort by', hover_text='choose how to sort games in the game opening window')
    btn_layout = Button(topleft=(10, 160), size=(120, 40),
                        text='Layout', hover_text='choose a layout for a generated game')
    btn_theme = Button(topleft=(10, 210), size=(120, 40),
                        text='Theme', hover_text='change the theme (dark/light) (needs restarting)')
    btn_wiggle = Button(topleft=(10, 260), size=(120, 40),
                        text='Wiggle', hover_text='toggle button wiggle')
    btn_bezier_animation = Button(topleft=(10, 310), size=(120, 40),
                        text='Paths', hover_text='toggle animated paths between nodes')
    cnt_bg_music_volume = Counter(topleft=(10, 360), size=(110, 40), value=OPTIONS['bg_music_volume'], bounds=(0, 100),
                            text='Music', hover_text='background music volume')
    btn_next_bg_track = Button(topleft=(200, 360), size=(60, 40),
                        text='Next', hover_text='switch backgroung music track')
    cnt_sfx_volume = Counter(topleft=(10, 410), size=(110, 40), value=OPTIONS['sfx_volume'], bounds=(0, 100),
                            text='SFX', hover_text='sound effects volume')
    txt_console = TextInput(topleft=(330, 10), size=(460, 40),
                        text='', hover_text=f'this is the command line', text_placement_specifier='input_text')
    objects = [
        btn_back, btn_save, btn_show_ind,
        btn_sort_by, btn_layout, btn_show_best_possible, 
        txt_console, btn_theme, btn_wiggle, btn_bezier_animation, 
        cnt_bg_music_volume, cnt_sfx_volume, btn_next_bg_track
    ]
    hover = HoverTooltip(objects=objects, topleft=(130, 567))

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
                        play_sfx('click')
                        running_options = False
                    elif btn_save.hovering(up):
                        with open(OPTIONS_DIR, 'w') as f:
                            json.dump(OPTIONS, f)
                        cmdline.log('info: saved successfully')
                        print('Settings saved')
                        play_sfx('options_switch')
                    elif btn_show_ind.hovering(up):
                        OPTIONS['show_node_ids'] = not OPTIONS['show_node_ids']
                        play_sfx('options_switch')
                    elif btn_show_best_possible.hovering(up):
                        OPTIONS['show_best_possible'] = not OPTIONS['show_best_possible']
                        play_sfx('options_switch')
                    elif btn_sort_by.hovering(up):
                        sort_by_num += 1
                        OPTIONS['sort_by'] = SORTBY_LIST[sort_by_num % len(SORTBY_LIST)]
                        play_sfx('options_switch')
                    elif btn_layout.hovering(up):
                        layout_num += 1
                        OPTIONS['layout'] = LAYOUT_LIST[layout_num % len(LAYOUT_LIST)]
                        play_sfx('options_switch')
                    elif btn_theme.hovering(up):
                        theme_num += 1
                        OPTIONS['theme'] = THEME_LIST[theme_num % len(THEME_LIST)]
                        cmdline.log(
                            f'info: save and then restart the game to & update the theme to [{OPTIONS["theme"]}]')
                        play_sfx('options_switch')
                    elif btn_wiggle.hovering(up):
                        OPTIONS['wiggle'] = not OPTIONS['wiggle']
                        play_sfx('options_switch')
                    elif btn_bezier_animation.hovering(up):
                        OPTIONS['bezier_animation'] = not OPTIONS['bezier_animation']
                        play_sfx('options_switch')
                    elif btn_next_bg_track.hovering(up):
                        play_bg_music()
                        play_sfx('options_switch')
                    elif txt_console.hovering(up):
                        txt_console.input_mode = not txt_console.input_mode
                elif event.button in {4, 5}:
                    if cnt_bg_music_volume.hovering(up, add=1 if event.button == 4 else -1) or \
                    cnt_sfx_volume.hovering(up, add=1 if event.button == 4 else -1):
                        play_sfx('scroll_short_click')
                        OPTIONS['bg_music_volume'] = cnt_bg_music_volume.value
                        bg_music_set_vol(OPTIONS['bg_music_volume']/100)
                        OPTIONS['sfx_volume'] = cnt_sfx_volume.value
                        set_sfx_volume(OPTIONS['sfx_volume']/100)
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

        for obj in objects:
            obj.draw(screen, my_font)

        # hover tooltips
        mouse = pygame.mouse.get_pos()
        hover.display(mouse, screen, my_font_hover)

        # some text
        x, y = btn_show_ind.topleft  
        blit(str(OPTIONS['show_node_ids']), (x + btn_show_ind.size[0] + 5, y + 13), GREEN if OPTIONS['show_node_ids'] else RED)
        blit(str(OPTIONS['show_best_possible']), (x + btn_show_ind.size[0] + 5, y + 60), GREEN if OPTIONS['show_best_possible'] else RED)
        blit(OPTIONS['sort_by'], (x + btn_show_ind.size[0] + 5, y + 108), THEME['def'])
        blit(OPTIONS['layout'], (x + btn_show_ind.size[0] + 5, y + 160))
        blit(OPTIONS['theme'], (x + btn_show_ind.size[0] + 5, y + 210), THEME['def'])
        blit(str(OPTIONS['wiggle']), (x + btn_show_ind.size[0] + 5, y + 260), GREEN if OPTIONS['wiggle'] else RED)
        blit(str(OPTIONS['bezier_animation']), (x + btn_show_ind.size[0] + 5, y + 310), GREEN if OPTIONS['bezier_animation'] else RED)

        # light yellow outline
        pygame.draw.rect(screen, THEME['options_outline'], [
                         0, 0, WIDTH, HEIGHT], 4)
        # console logs
        pygame.draw.rect(screen, THEME['def'], [330, 60, 460, 530], 4)
        for i, log in enumerate(cmdline.console_log[-22:]):
            screen.blit(my_font.render(log, False, THEME['def']),
                        (337, 65 + i*23))
        pygame.display.update()
        clock.tick(FRAMERATE)
