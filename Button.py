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

