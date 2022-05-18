import pygame

class Button():
    def __init__(self, topleft, size, text, is_active=True):
        self.topleft = topleft
        self.size = size
        self.is_active = is_active
        self.text = text
        self.rect = pygame.Rect(topleft, size)


    def draw(self, screen, font):
        x, y = self.topleft
        wi, he = self.size
        color = (255, 255, 255) if self.is_active else (100, 100, 100)
        pygame.draw.rect(screen, color, [x, y, wi, he], 4)
        position = x + wi//8, y + he//4
        screen.blit(font.render(self.text, False, color), position)
    
    def hovering(self, pos): 
        res = self.rect.collidepoint(pos) and self.is_active
        if res:
            print(f'btn {self.text} is pressed')
        return res

PANEL_HEIGHT = 50


class Panel():
    def __init__(self, data, num=None):
        self.num = num # a number from 0 to 6
        self.data = data

    
    def draw(self, topleft, screen, font):
        x, y = topleft
        pygame.draw.rect(screen, (0,255,0), [x, y, 770, PANEL_HEIGHT], 4)
        screen.blit(font.render(str(self.data['game_number']), False, (255,255,255)), (x+10, y+10))
        screen.blit(font.render(str(self.data['difficulty']), False, (255,255,255)), (x+130, y+10))
        screen.blit(font.render(str(self.data['num_of_plays']), False, (255,255,255)), (x+270, y+10))
        screen.blit(font.render(str(self.data['best_score']), False, (255,255,255)), (x+400, y+10))
        screen.blit(font.render(str(self.data['date_created']), False, (255,255,255)), (x+560, y+10))
