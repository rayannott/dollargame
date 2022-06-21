from ast import arg
import pygame
from utils import THEME, PANEL_HEIGHT


class Button():
    def __init__(self, topleft, size, text, is_active=True, is_visible=True,
                 bg_color=THEME['button_default'], hover_text='this is helpful',  text_placement_specifier='default'):
        self.topleft = topleft
        self.size = size
        self.is_active = is_active
        self.text = text
        self.rect = pygame.Rect(topleft, size)
        self.is_visible = is_visible
        self.hover_text = hover_text
        self.bg_color = bg_color
        self.text_placement_specifier = text_placement_specifier

    def draw(self, screen, font):
        def color_active(col):
            return col if self.is_active else THEME['button_inactive']
        if self.is_visible:
            x, y = self.topleft
            wi, he = self.size
            color = color_active(self.bg_color)
            pygame.draw.rect(screen, (255, 255, 255), [x, y, wi, he], width=4)
            pygame.draw.rect(screen, color, [x+4, y+4, wi-8, he-8])
            if self.text_placement_specifier == 'text_input':

                position = x + he//4, y + he//4
            else:
                position = x + wi//8, y + he//4
            screen.blit(font.render(self.text, False,
                        (255, 255, 255)), position)

    def hovering(self, pos):
        res = self.rect.collidepoint(pos) and self.is_active
        return res


class Counter(Button):
    def __init__(self, topleft, size, text, is_active=True, is_visible=True, bg_color=THEME['button_default'], hover_text='a counter',  bounds=(-100, 100), value=0):
        super().__init__(topleft, size, text, is_active, is_visible, bg_color, hover_text)
        self.value = value
        self.bounds = bounds

    def hovering(self, pos, add=0):
        res = self.rect.collidepoint(pos) and self.is_active
        if res:
            if add < 0 and self.value > self.bounds[0] or add > 0 and self.value < self.bounds[1]:
                self.value += add
        return res

    def draw(self, screen, font):
        x, y = self.topleft
        wi, he = self.size
        pos = x + int(1.1*wi), y + he//4
        screen.blit(font.render(str(self.value),
                    False, THEME['counter_text']), pos)
        return super().draw(screen, font)


class HoverTooltip():
    def __init__(self, objects, topleft=(7, 7)):
        self.objects = objects
        self.topleft = topleft
        self.text = ''

    def display(self, pos, screen, font):
        for obj in self.objects:
            if obj.hovering(pos):
                self.text = obj.hover_text
                screen.blit(font.render(self.text, False,
                            (200, 200, 255)), self.topleft)
                return
        self.text = ''


class Panel():
    def __init__(self, data):
        self.data = data

    def draw(self, topleft, screen, font):
        x, y = topleft
        pygame.draw.rect(screen, THEME['open_game_panels'], [
                         x, y, 766, PANEL_HEIGHT], 4)
        screen.blit(font.render(
            str(self.data['game_number']), False, (255, 255, 255)), (x+10, y+10))
        screen.blit(font.render(
            '/'.join(map(str, self.data['graph'])), False, (255, 255, 255)), (x+130, y+10))
        screen.blit(font.render(
            str(self.data['num_of_plays']), False, (255, 255, 255)), (x+270, y+10))
        screen.blit(font.render(
            str(self.data['best_score']), False, (255, 255, 255)), (x+400, y+10))
        screen.blit(font.render(
            str(self.data['date_created']), False, (255, 255, 255)), (x+560, y+10))


class TextInput(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_mode = False
        self.text_placement_specifier = 'text_input'

    def draw(self, screen, font):
        self.bg_color = THEME['button_default'] if self.input_mode else THEME['button_inactive']
        super().draw(screen, font)
