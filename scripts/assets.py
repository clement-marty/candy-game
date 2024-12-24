import pygame


CELL_BACKGROUND = pygame.Surface((64, 64))
CELL_BACKGROUND.fill((200, 200, 200))
pygame.draw.rect(CELL_BACKGROUND, (255, 255, 255), (0, 0, 64, 64), 2)


SCORE_CELL_BACKGROUND = CELL_BACKGROUND

SELECTOR = pygame.Surface((64, 64), pygame.SRCALPHA)
pygame.draw.rect(SELECTOR, (100, 100, 100, 128), (0, 0, 64, 64), 10)

SUBSELECTOR = pygame.Surface((64, 64), pygame.SRCALPHA)
pygame.draw.rect(SUBSELECTOR, (150, 150, 150, 128), (0, 0, 64, 64), 10)



class TexturePack:

    PATHS = {
        'BACKGROUND_IMAGE': 'background.png',
        'CHECKMARK_ICON': 'checkmark_icon.png',
        'RED_CELL': 'cells/red_cell.png',
        'GREEN_CELL': 'cells/green_cell.png',
        'BLUE_CELL': 'cells/blue_cell.png',
        'YELLOW_CELL': 'cells/yellow_cell.png',
        'PURPLE_CELL': 'cells/purple_cell.png',
        'PINK_CELL': 'cells/pink_cell.png'
    }

    def __init__(self, path: str) -> None:
        '''Initializes the texture pack

        :param str path: the path to the texture pack
        '''
        self.path = path
        for texture, file_path in self.PATHS.items():
            self.__dict__[texture] = pygame.image.load(f'{self.path}/{file_path}')

        self.SELECTOR = SELECTOR
        self.SUBSELECTOR = SUBSELECTOR
        self.CELL_BACKGROUND = CELL_BACKGROUND
        self.SCORE_CELL_BACKGROUND = SCORE_CELL_BACKGROUND

        self.CELLS = [
            ('red', self.RED_CELL),
            ('green', self.GREEN_CELL),
            ('blue', self.BLUE_CELL),
            ('yellow', self.YELLOW_CELL),
            ('purple', self.PURPLE_CELL),
            ('pink', self.PINK_CELL)
        ]




CANDY_PACK = TexturePack('assets/CandyTexturePack')