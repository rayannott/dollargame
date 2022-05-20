import pygame

class Button():
    def __init__(self, topleft, size, text, is_active=True, 
                    is_visible=True, hover_text='this is helpful'):
        self.topleft = topleft
        self.size = size
        self.is_active = is_active
        self.text = text
        self.rect = pygame.Rect(topleft, size)
        self.is_visible = is_visible
        self.hover_text = hover_text


    def draw(self, screen, font):
        if self.is_visible:
            x, y = self.topleft
            wi, he = self.size
            color = (255, 255, 255) if self.is_active else (100, 100, 100)
            pygame.draw.rect(screen, color, [x, y, wi, he], 4)
            position = x + wi//8, y + he//4
            screen.blit(font.render(self.text, False, color), position)
    
    def hovering(self, pos, press=True): 
        res = self.rect.collidepoint(pos) and self.is_active
        if res and press:
            print(f'Button [{self.text}] is pressed')
        return res

class Counter(Button):
    def __init__(self, topleft, size, text, is_active=True, is_visible=True, hover_text='a counter', value=0):
        super().__init__(topleft, size, text, is_active, is_visible, hover_text)
        self.value = value
    
    def hovering(self, pos, press=False, add=0):
        res = self.rect.collidepoint(pos) and self.is_active
        if res:
            if press:
                print(f'Counter [{self.text}] is pressed')
            self.value += add
        return res
    
    def draw(self, screen, font):
        x, y = self.topleft
        wi, he = self.size
        pos = x + int(1.1*wi), y + he//4
        screen.blit(font.render(str(self.value), False, (45, 113, 168)), pos)
        return super().draw(screen, font)
    

class HoverTooltip():
    def __init__(self, objects, topleft=(7,7)):
        self.objects = objects
        self.topleft = topleft
        self.text = ''

    def display(self, pos, screen, font):
        for obj in self.objects:
            if obj.hovering(pos, press=False):
                self.text = obj.hover_text
                screen.blit(font.render(self.text, False, (200, 200, 255)), self.topleft)
                return
        self.text = ''
        

PANEL_HEIGHT = 50

class Panel():
    def __init__(self, data):
        self.data = data

    
    def draw(self, topleft, screen, font):
        x, y = topleft
        pygame.draw.rect(screen, (0,255,0), [x, y, 770, PANEL_HEIGHT], 4)
        screen.blit(font.render(str(self.data['game_number']), False, (255,255,255)), (x+10, y+10))
        screen.blit(font.render('/'.join(map(str, self.data['graph'])), False, (255,255,255)), (x+130, y+10))
        screen.blit(font.render(str(self.data['num_of_plays']), False, (255,255,255)), (x+270, y+10))
        screen.blit(font.render(str(self.data['best_score']), False, (255,255,255)), (x+400, y+10))
        screen.blit(font.render(str(self.data['date_created']), False, (255,255,255)), (x+560, y+10))
