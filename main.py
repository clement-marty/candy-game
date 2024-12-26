import pygame
import configparser

from scripts.game_logic import generate_grid, fill_grid, movements_from_grid,  detect_alignments, special_cell_interaction, ScoreManager
from scripts.renderer import render_grid, render_score, render_selector, resize_cells, AnimationManager, LinearAnimation
import scripts.assets as assets



def read_config() -> None:
    '''Reads the configuration file'''
    config = configparser.ConfigParser()
    config.read('config.ini')
    global GAME_FPS, TPACK, GRID_SIZE, CELL_SIZE, GRID_MARGIN, SCORE_OBJECTIVES, MAX_RAINBOW_CELLS
    GAME_FPS = config.getint('general', 'frames_per_second')
    try:
        TPACK = assets.TexturePack(f'assets/{config.get('general', 'texture_pack')}')
    except FileNotFoundError:
        raise ValueError(f'Invalid texture pack: {config.get('general', 'texture_pack')}')
    GRID_SIZE = (
        config.getint('graphics', 'grid_width'),
        config.getint('graphics', 'grid_height')
    )
    CELL_SIZE = config.getint('graphics', 'cell_size')
    GRID_MARGIN = config.getint('graphics', 'grid_margin')
    SCORE_OBJECTIVES = []
    for i in ['red_cells', 'green_cells', 'blue_cells', 'yellow_cells', 'purple_cells', 'pink_cells']:
        SCORE_OBJECTIVES.append(config.getint('game-objectives', i))
    MAX_RAINBOW_CELLS = config.getint('game', 'max_rainbow_cells')

    
# Initialize the game
read_config()
pygame.init()
# pygame.font.init()
# font = pygame.font.SysFont('Ubuntu', CELL_SIZE)


grid = generate_grid(*GRID_SIZE)
screen_size = (
    GRID_MARGIN * 2 + CELL_SIZE * GRID_SIZE[0],
    GRID_MARGIN * 2 + CELL_SIZE * GRID_SIZE[1] + CELL_SIZE
)

cells = resize_cells(TPACK.CELLS, CELL_SIZE)
rainbow_cells_nb = 0
movements, grid = fill_grid(grid, cells)

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Candy Game')
animation_manager = AnimationManager()
score_manager = ScoreManager(cells, SCORE_OBJECTIVES)
selector = (None, None)

# Make sure the first generated grid does not contain any alignments
aligned_cells, _, grid = detect_alignments(
    g=grid,
    cells=cells,
    rainbow_cell=resize_cells([('rainbow', TPACK.RAINBOW_CELL)], CELL_SIZE)[0], 
    add_special_cells=False
)
while aligned_cells:
    movements, grid = fill_grid(grid, cells)
    for mov in movements:
        x, y, cell = mov[2], mov[3], mov[4]
        grid[y][x] = cell
    aligned_cells, _, grid = detect_alignments(
        g=grid,
        cells=cells,
        rainbow_cell=resize_cells([('rainbow', TPACK.RAINBOW_CELL)], CELL_SIZE)[0],
        add_special_cells=False
    )

movements = movements_from_grid(grid)
grid = generate_grid(*GRID_SIZE)
animation_manager.add_animations(LinearAnimation.from_movements(movements, CELL_SIZE, (GRID_MARGIN, GRID_MARGIN+CELL_SIZE), speed=1000, delay=0.01))

clock = pygame.time.Clock()
can_play = False
has_won = False
running = True
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            x = (mouse_x - GRID_MARGIN) // CELL_SIZE
            y = (mouse_y - GRID_MARGIN - CELL_SIZE) // CELL_SIZE
            if x >= 0 and x < GRID_SIZE[0] and y >= 0 and y < GRID_SIZE[1]:
                
                if can_play and selector != (None, None):
                    if (x == selector[0] and abs(y - selector[1]) == 1) or (y == selector[1] and abs(x - selector[0]) == 1):

                        # Check if this is an interaction with a rainbow cell,
                        # and that the second cell is not a rainbow cell
                        if (grid[y][x][0] == 'rainbow' or grid[selector[1]][selector[0]][0] == 'rainbow') \
                            and (grid[y][x][0] != grid[selector[1]][selector[0]][0]):

                            rainbow_coords: tuple[int, int]
                            other_coords: tuple[int, int]
                            if grid[y][x][0] == 'rainbow':
                                rainbow_coords = (x, y)
                                other_coords = selector
                            else:
                                rainbow_coords = selector
                                other_coords = (x, y)
                            aligned_cells, grid = special_cell_interaction(
                                g=grid,
                                x=rainbow_coords[0],
                                y=rainbow_coords[1],
                                rainbow_cell=grid[rainbow_coords[1]][rainbow_coords[0]],
                                other_cell=grid[other_coords[1]][other_coords[0]]
                            )
                            score_manager.update_score_from_dict(aligned_cells)
                            rainbow_cells_nb -= 1
                            
                        # Otherwise, swap the two selected cells
                        else: 
                            animation_manager.add_animations(LinearAnimation.from_movements(
                                [(x, y, selector[0], selector[1], grid[y][x]), (selector[0], selector[1], x, y, grid[selector[1]][selector[0]])],
                                CELL_SIZE, (GRID_MARGIN, GRID_MARGIN+CELL_SIZE), speed=500
                            ))
                            grid[y][x], grid[selector[1]][selector[0]] = (None, None), (None, None)
                        selector = (None, None)

                        
                    else:
                        selector = (x, y)

                selector = (x, y)

    # Fill the background with assets.BACKGROUND_IMAGE
    screen.blit(
        pygame.transform.scale(TPACK.BACKGROUND_IMAGE, screen_size), (0, 0)
    )

    render_grid(
        screen=screen, 
        grid=grid,
        texture_pack=TPACK,
        x=GRID_MARGIN,
        y=GRID_MARGIN+CELL_SIZE,
        cell_size=CELL_SIZE
    )
    render_score(
        screen=screen,
        cells=score_manager.cells,
        objectives=score_manager.objectives,
        scores=score_manager.scores,
        texture_pack=TPACK,
        grid_margin=GRID_MARGIN,
        cell_size=CELL_SIZE
    )
    animation_manager.update(screen, 1/GAME_FPS)


    # Place the finished animations back into the grid
    finished_anims = animation_manager.finished_animations()
    for anim in finished_anims:
        cell_pos, cell = anim.destination_cell(CELL_SIZE, (GRID_MARGIN, GRID_MARGIN+CELL_SIZE))
        grid[cell_pos[1]][cell_pos[0]] = cell


    has_won = score_manager.check_completion()
    can_play = animation_manager.is_done and not has_won


    if not can_play: # If the animations are not done, we can't play
        selector = (None, None)

    else: # If the animations are done, we check for alignments
        aligned_cells, rainbow_cells, grid = detect_alignments(
            g=grid,
            cells=cells,
            rainbow_cell=resize_cells([('rainbow', TPACK.RAINBOW_CELL)], CELL_SIZE)[0],
            add_special_cells= True if rainbow_cells_nb < MAX_RAINBOW_CELLS else False
        )
        rainbow_cells_nb += rainbow_cells
        score_manager.update_score_from_dict(aligned_cells)
        movements, grid = fill_grid(grid, cells)
        animation_manager.add_animations(LinearAnimation.from_movements(movements, CELL_SIZE, (GRID_MARGIN, GRID_MARGIN+CELL_SIZE), speed=1000, delay=0.01))


    if selector != (None, None):
        render_selector(screen, selector, TPACK, CELL_SIZE, GRID_SIZE, (GRID_MARGIN, GRID_MARGIN+CELL_SIZE))

    # if has_won:
    #     screen.blit(font.render('You won!', False, (0, 0, 0)), (GRID_MARGIN, GRID_MARGIN//2))

    # Update the display
    pygame.display.flip()
    clock.tick(GAME_FPS)
