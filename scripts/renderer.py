import pygame

from scripts.game_logic import G, M, C
import scripts.assets as assets



def render_grid(screen: pygame.Surface, grid: list[list[tuple[str, pygame.Surface]]], texture_pack: assets.TexturePack, x: int, y: int, cell_size: int) -> None:
    '''Renders the grid on the screen
    
    :param pygame.Surface screen: the screen to render on
    :param list[list[tuple[str, pygame.Surface]]] grid: the grid to render
    :param assets.TexturePack texture_pack: the texture pack to be used
    :param int x: the x position of the grid
    :param int y: the y position of the grid
    :param int cell_size: the size of a cell
    '''
    for i in range(len(grid)):
        for j in range(len(grid[i])):

            # Render the cell background
            screen.blit(
                pygame.transform.scale(texture_pack.CELL_BACKGROUND, (cell_size, cell_size)),
                (x + j * cell_size, y + i * cell_size)
            )
            # Render the cell if there is one
            if grid[i][j][1] is not None:
                screen.blit(grid[i][j][1], (x + j * cell_size, y + i * cell_size))


def render_score(screen: pygame.Surface, cells: list[C], objectives: list[int], scores: list[int], texture_pack: assets.TexturePack, grid_margin: int, cell_size: int) -> None:
    '''Renders the score at the top of the screen
    
    :param pygame.Surface screen: the screen to render on
    :param list[C] cells: the list of the different cell types
    :param list[int] objectives: the list of objectives, where each element is the number of cells of the corresponding type that need to be obtained
    :param list[int] scores: the list of scores, where each element is the number of cells of the corresponding type that have already been obtained
    :param assets.TexturePack texture_pack: the texture pack to be used
    :param int grid_margin: the grid's margin, in pixels
    :param int cell_size: the size of a cell
    '''
    for i in range(len(cells)):
        x = i * cell_size + grid_margin
        y = grid_margin // 2

        # Render the cell background
        screen.blit(
            pygame.transform.scale(texture_pack.SCORE_CELL_BACKGROUND, (cell_size, cell_size)),
            (x, y)
        )

        # Compute the progression
        completion = min(scores[i] / objectives[i], 1)
        height = cell_size * completion
        progression_rect = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        pygame.draw.rect(
            surface=progression_rect, 
            color=(0, 255, 0, 100),
            rect=(0, cell_size - height, cell_size, height)
        )

        if completion == 1: # Render the cell first if enough have been obtained
            screen.blit(cells[i][1], (x, y))
            screen.blit(progression_rect, (x, y))
            screen.blit(
                pygame.transform.scale(texture_pack.CHECKMARK_ICON, (cell_size, cell_size)),
                (x, y)
            )
        else: # Render the cell last
            screen.blit(progression_rect, (x, y))
            screen.blit(cells[i][1], (x, y))




def render_selector(screen: pygame.Surface, selector_pos: tuple[int, int], texture_pack: assets.TexturePack, cell_size: int, grid_size: tuple[int, int],  grid_margin: tuple[int, int]) -> None:
    '''Renders the selector on the screen aling with subselectors
    
    :param pygame.Surface screen: the screen to render on
    :param tuple[int, int] selector_pos: the position of the selector
    :param assets.TexturePack texture_pack: the texture pack to be used
    :param int cell_size: the size of a cell
    :param tuple[int, int] grid_size: the size of the grid
    :param tuple[int, int] grid_margin: the margin of the grid in the format (<left margin>, <top margin>)
    '''
    screen.blit(
        pygame.transform.scale(texture_pack.SELECTOR, (cell_size, cell_size)),
        (selector_pos[0] * cell_size + grid_margin[0], selector_pos[1] * cell_size + grid_margin[1])
    )
    for i, j in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        x, y = selector_pos[0] + i, selector_pos[1] + j
        if x >= 0 and x < grid_size[0] and y >= 0 and y < grid_size[1]:
            screen.blit(
                pygame.transform.scale(texture_pack.SUBSELECTOR, (cell_size, cell_size)),
                (x * cell_size + grid_margin[0], y * cell_size + grid_margin[1])
            )


def resize_cells(cells: list[C], cell_size: int) -> list[C]:
    '''Resizes all the cells to a new size
    
    :param list[C] cells: the cells to resize
    :param int cell_size: the new size of the cells
    :return list[C]: the resized cells
    '''
    c = []
    for cell in cells:
        name, sprite = cell
        c.append((name, pygame.transform.scale(sprite, (cell_size, cell_size))))
    return c



class LinearAnimation:

    def __init__(self, tile_name: str, sprite: pygame.Surface, x: int, y: int, new_x: int, new_y: int, duration: float =None, speed: float =None, delay: float =0) -> None:
        '''Initializes the movement animation
        Either duration or speed must be provided
        
        :param str tile_name: the name of the tile
        :param pygame.Surface sprite: the sprite to animate
        :param int x: the x position of the sprite
        :param int y: the y position of the sprite
        :param int new_x: the new x position of the sprite
        :param int new_y: the new y position of the sprite
        :param float duration: the duration of the animation, in seconds
        :param float speed: the speed of the animation, in pixels per second
        :param float delay: the delay before the animation starts, in seconds
        '''
        if duration is None and speed is None:
            raise ValueError('Either duration or speed must be provided')
        self.tile_name = tile_name
        self.sprite = sprite
        self.start_x , self.start_y = x, y
        self.new_x, self.new_y = new_x, new_y
        self.t = -delay
        if duration:
            self.duration = duration
        else:
            self.duration = ((new_x - x) ** 2 + (new_y - y) ** 2) ** 0.5 / speed


    @property
    def is_done(self) -> bool:
        '''Returns True if the animation is done, False otherwise
        
        :return bool:
        '''
        return self.t >= self.duration
    

    def update(self, t: float) -> tuple[pygame.Surface, tuple[int, int]]:
        '''Updates the animation and returns the new position and sprite of the animated object
        
        :param float t: the time elapsed since the last update, in seconds
        :return tuple[pygame.Surface, tuple[int, int]]: the sprite and the new position of the animated object
        '''
        self.t += t
        if self.t > self.duration:
            self.t = self.duration
        x = self.start_x + (self.new_x - self.start_x) * max(0, self.t) / self.duration
        y = self.start_y + (self.new_y - self.start_y) * max(0, self.t) / self.duration

        return self.sprite, (x, y)


    
    def destination_cell(self, cell_size: int, grid_margin: tuple[int, int]) -> tuple[tuple[int, int], tuple[str, pygame.Surface]]:
        '''Returns the destination cell of the animation, as a tuple of format:
        ((x, y), (tile_name, sprite))
        
        :param int cell_size: the size of a cell
        :param tuple[int, int] grid_margin: the margin of the grid in the format (<left margin>, <top margin>)
        :return tuple[tuple[int, int], tuple[str, pygame.Surface]]:
        '''
        return (
            (self.new_x - grid_margin[0]) // cell_size,
            (self.new_y - grid_margin[1]) // cell_size
        ), (self.tile_name, self.sprite)


    @classmethod
    def from_movements(cls, movements: M, cell_size: int, grid_margin: tuple[int, int],  duration: float =None, speed: float =None, delay: float =0) -> list:
        '''Creates a list of LinearAnimation objects from a list of movements
        Either duration or speed must be provided
        
        :param G grid: the game grid before the movements
        :param M movements: the list of movements
        :param int cell_size: the size of a cell
        :param tuple[int, int] grid_margin: the margin of the grid in the format (<left margin>, <top margin>)
        :param float duration: the duration of each animation, in seconds
        :param float speed: the speed of each animation, in pixels per second
        :param float delay: the delay between each animation, in seconds
        :return list[LinearAnimation]: the list of animations
        '''
        if duration is None and speed is None:
            raise ValueError('Either duration or speed must be provided')

        animations = []
        for i in range(len(movements)):
            x, y, new_x, new_y, cell = movements[i]
            time_name, sprite = cell

            if x is None or y is None:
                animations.append(cls(
                    tile_name=time_name,
                    sprite=sprite,
                    x=grid_margin[0] + new_x * cell_size,
                    y=-100,
                    new_x=grid_margin[0] + new_x * cell_size,
                    new_y=grid_margin[1] + new_y * cell_size,
                    duration=duration,
                    speed=speed,
                    delay=delay * i
                ))
            else:
                animations.append(cls(
                    tile_name=time_name,
                    sprite=sprite,
                    x=grid_margin[0] + x * cell_size,
                    y=grid_margin[1] + y * cell_size,
                    new_x=grid_margin[0] + new_x * cell_size,
                    new_y=grid_margin[1] + new_y * cell_size,
                    duration=duration,
                    speed=speed,
                    delay=delay * i
                ))
        return animations

    

class AnimationManager:

    def __init__(self) -> None:
        '''Initializes the animation manager
        '''
        self.animations = []
    
    
    @property
    def is_done(self) -> bool:
        '''Returns True if all the animations are done, False otherwise
        
        :return bool:
        '''
        return self.animations == []


    def add_animation(self, animation: LinearAnimation) -> None:
        '''Adds an animation to the manager
        
        :param LinearMovementAnimation animation: the animation to add
        '''
        self.animations.append(animation)


    def add_animations(self, animations: list[LinearAnimation]) -> None:
        '''Adds multiple animations to the manager
        
        :param list[LinearMovementAnimation] animations: the animations to add
        '''
        self.animations.extend(animations)


    def update(self, screen: pygame.Surface, t: float) -> None:
        '''Displays all the animations on the screen and removes the ones that are done
        
        :param pygame.Surface screen: the screen to display on
        :param float t: the time elapsed since the last update, in seconds
        '''
        for animation in self.animations:
            screen.blit(*animation.update(t))

    
    def finished_animations(self) -> list[LinearAnimation]:
        '''Returns the animations that are finished and removes them from the manager
        
        :return list[LinearAnimation]:
        '''
        animations = []
        for animation in self.animations:
            if animation.is_done:
                animations.append(animation)
                self.animations.remove(animation)
        return animations
