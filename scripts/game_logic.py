import pygame
import random



C = tuple[str, pygame.Surface] # Type alias for the type of the elements in the grid
G = list[list[C]] # Type alias for the grid
M = list[tuple[int, int, int, int, C]] # Type alias for the movements


def generate_grid(w: int, h: int) -> G:
    '''Generates a 2D grid of size w x h with all elements set to (None, None)
    The format of each element is (type, texture)
    - type: str or None
    - texture: pygame.Surface or None

    :param int w: the width of the grid 
    :param int h: the height of the grid
    :return G: the generated grid
    '''
    grid = []
    for i in range(h):
        grid.append([(None, None)] * w)
    return grid

def copy_grid(g: G) -> G:
    '''Copies a grid

    :param G g: the grid to copy
    :return G: the copied grid
    '''
    new_grid = []
    for i in g:
        new_grid.append(i.copy())
    return new_grid


def generate_filled_grid(size: tuple[int, int], cells: list[C], rainbow_cell: C, cross_cell: C) -> G:
    '''Generates a filled grid of the specified size with the specified cells
    
    :param tuple[int, int] size: the size of the grid
    :param list[C] cells: the list of cells to use
    :param C rainbow_cell: the rainbow cell type
    :param C cross_cell: the cross cell type
    :return G: the generated grid
    '''
    grid = generate_grid(*size)
    movements, grid = fill_grid(grid, cells)
    for mov in movements:
        x, y, cell = mov[2], mov[3], mov[4]
        grid[y][x] = cell
    aligned_cells, _, _, grid = detect_alignments(
        g=grid,
        cells=cells,
        rainbow_cell=rainbow_cell,
        cross_cell=cross_cell,
        add_rainbow_cells=False,
        add_cross_cells=False
    )
    # Make sure the generated grid does not contain any alignment
    while aligned_cells:
        movements, grid = fill_grid(grid, cells)
        for mov in movements:
            x, y, cell = mov[2], mov[3], mov[4]
            grid[y][x] = cell
        aligned_cells, _, _, grid = detect_alignments(
            g=grid,
            cells=cells,
            rainbow_cell=rainbow_cell,
            cross_cell=cross_cell,
            add_rainbow_cells=False,
            add_cross_cells=False
        )
    return grid


def fill_grid(g: G, cells: list[C]) -> tuple[M, G]:
    '''Fills the holes in the grid by moving all the elements down and adding new random elements at the top
    
    :param G g: the grid to fill
    :param list[C] cells: the list of elements to add to the grid
    :return tuple[M, G]: a list of all the movements that were made and an intermediate grid
        The format of each element of the movement list is (x, y, new_x, new_y)
        If the cell is a new one, x and y are None
        The intermediate grid is the grid of all unaffected cells
    '''
    new_grid = copy_grid(g)
    intermediate_grid = copy_grid(g)
    movements = []

    # Apply gravity to the grid
    for y in range(len(g)-1, -1, -1):
        for x in range(len(g[y])):
            if new_grid[y][x][0] is None:
                found_a_cell = False
                i = y-1
                while i >= 0 and not found_a_cell:
                    if new_grid[i][x][0] is not None:
                        found_a_cell = True
                        movements.append((x, i, x, y, g[i][x]))
                        new_grid[y][x], new_grid[i][x] = new_grid[i][x], (None, None)
                        intermediate_grid[i][x] = (None, None) # We remove the moved cell in the intermediate grid
                    else:
                        i -= 1
    
    # add new elements to the grid
    for y in range(len(g)-1, -1, -1):
        for x in range(len(g[y])):
            if new_grid[y][x][0] is None:
                new_grid[y][x] = random.choice(cells)
                movements.append((None, None, x, y, new_grid[y][x]))
    
    return movements, intermediate_grid


def movements_from_grid(g: G) -> M:
    '''Converts a grid to a list of movements

    :param G g: the grid to convert
    :return M: the list of movements
    '''
    movements = []
    for y in range(len(g)-1, -1, -1):
        for x in range(len(g[y])):
            if g[y][x][0] is not None:
                movements.append((None, None, x, y, g[y][x]))
    
    return movements



def detect_alignments(g: G, cells: list[C], rainbow_cell: C, cross_cell: C, add_rainbow_cells: bool = True, add_cross_cells: bool = True) -> tuple[dict[str, int], int, int, G]:
    '''Detects all the aligned cells in the grid and removes them

    :param G g: the grid to check
    :param list[C] cells: the list of normal cell types
    :param C rainbow_cell: the rainbow cell type
    :param C cross_cell: the cross cell type
    :param bool add_rainbow_cells: Does the function has to create rainbow cells?
    :param bool add_cross_cells: Does the function has to create cross cells?
    :return tuple[dict[str, int], int, int, G]:
        - the number of aligned cells per type
        - the number of rainbow cells added
        - the number of cross cells added
        - the new grid
    '''
    aligned_cells = set()
    rainbow_cells = set()
    cross_cells = set()

    # Check horizontal alignments
    for y in range(len(g)):
        for x in range(len(g[y])):
            if g[y][x] in cells:

                # Check hotizontal alignment
                n = 1
                while x+n < len(g[y]) and g[y][x][0] == g[y][x+n][0]: n += 1
                if n >= 3:
                    for i in range(n): aligned_cells.add((x+i, y))
                if n >= 5:
                    i = random.randint(0, n-1)
                    rainbow_cells.add((x+i, y))
                elif n == 4:
                    i = random.randint(0, n-1)
                    cross_cells.add((x+i, y))

                # Check vertical alignment
                n = 1
                while y+n < len(g) and g[y][x][0] == g[y+n][x][0]: n += 1
                if n >= 3:
                    for i in range(n): aligned_cells.add((x, y+i))
                if n >= 5:
                    i = random.randint(0, n-1)
                    rainbow_cells.add((x, y+i))
                elif n == 4:
                    i = random.randint(0, n-1)
                    cross_cells.add((x, y+i))

                # Check diagonal alignments
                n = 1
                while y+n < len(g) and x+n < len(g[y]) and g[y][x][0] == g[y+n][x+n][0]: n += 1
                if n >= 3:
                    for i in range(n): aligned_cells.add((x+i, y+i))
                if n >= 5:
                    i = random.randint(0, n-1)
                    rainbow_cells.add((x+i, y+i))
                elif n == 4:
                    i = random.randint(0, n-1)
                    cross_cells.add((x+i, y+i))

                n = 1
                while y+n < len(g) and x-n >= 0 and g[y][x][0] == g[y+n][x-n][0]: n += 1
                if n >= 3:
                    for i in range(n): aligned_cells.add((x-i, y+i))
                if n >= 5:
                    i = random.randint(0, n-1)
                    rainbow_cells.add((x-i, y+i))
                elif n == 4:
                    i = random.randint(0, n-1)
                    cross_cells.add((x-i, y+i))



    # Remove aligned cells
    new_grid = copy_grid(g)
    for y in range(len(g)):
        for x in range(len(g[y])):
            if (x, y) in aligned_cells:
                new_grid[y][x] = (None, None)

    # Add the specials cells
    if add_rainbow_cells:
        for x, y in rainbow_cells:
            new_grid[y][x] = rainbow_cell
    if add_cross_cells:
        for x, y in cross_cells:
            new_grid[y][x] = cross_cell

    # Count the number of aligned cells per type
    aligned_cells_count = {}
    for x, y in aligned_cells:
        if g[y][x][0] in aligned_cells_count:
            aligned_cells_count[g[y][x][0]] += 1
        else:
            aligned_cells_count[g[y][x][0]] = 1
    
    return (
        aligned_cells_count,
        len(rainbow_cells) if add_rainbow_cells else 0,
        len(cross_cells) if add_cross_cells else 0,
        new_grid
    )


def rainbow_cell_interaction(g: G, x: int, y: int, rainbow_cell: C, other_cell: C) -> tuple[dict[str, int], G]:
    '''Applies the effect of a rainbow cell on the grid, 
    by removing all cells of the same type of the one that was interacted with

    :param G g: the grid to check
    :param int x: the x coordinate of the special cell
    :param int y: the y coordinate of the special cell
    :param C rainbow_cell: the rainbow cell
    :param C other_cell: the other cell
    :return tuple[dict[str, int], G]: the number of aligned cells per type and the new grid
    '''
    new_grid = copy_grid(g)
    new_grid[y][x] = (None, None) # Remove the special cell

    # Remove all occurences of the interacted cell
    cell_type = other_cell[0]
    aligned_cell_count = {cell_type: 0}
    for y in range(len(g)):
        for x in range(len(g[y])):
            if g[y][x][0] == cell_type:
                new_grid[y][x] = (None, None)
                aligned_cell_count[cell_type] += 1

    return aligned_cell_count, new_grid    


def cross_cell_interaction(g: G, cross_cell_pos: tuple[int, int], other_cell_pos: tuple[int, int]) -> tuple[dict[str, int], G]:
    '''Applies the effect of a cross cell on the grid, 
    by removing all cells in the same row or column as the one that was interacted with

    :param G g: the grid to check
    :param tuple[int, int] cross_cell_pos: the position of the cross cell
    :param tuple[int, int] other_cell_pos: the position of the other cell
    :return tuple[dict[str, int], G]: the number of aligned cells per type and the new grid
    '''
    new_grid = copy_grid(g)
    new_grid[cross_cell_pos[1]][cross_cell_pos[0]] = (None, None) # Remove the special cell
    aligned_cell_count = {}

    if cross_cell_pos[0] == other_cell_pos[0]: # The cells are on the same column

        # Remove all cells in the column
        for y in range(len(g)):
            if g[y][cross_cell_pos[0]][0] in aligned_cell_count:
                aligned_cell_count[g[y][cross_cell_pos[0]][0]] += 1
            else:
                aligned_cell_count[g[y][cross_cell_pos[0]][0]] = 1
            new_grid[y][cross_cell_pos[0]] = (None, None)

    elif cross_cell_pos[1] == other_cell_pos[1]: # The cells are on the same row

        # Remove all cells in the row
        for x in range(len(g[0])):
            if g[cross_cell_pos[1]][x][0] in aligned_cell_count:
                aligned_cell_count[g[cross_cell_pos[1]][x][0]] += 1
            else:
                aligned_cell_count[g[cross_cell_pos[1]][x][0]] = 1
            new_grid[cross_cell_pos[1]][x] = (None, None)
    
    return aligned_cell_count, new_grid



class ScoreManager:

    def __init__(self, cells: list[C], objectives: list[int]) -> None:
        '''Initializes the score manager
        
        :param list[C] cells: the list of cells
        :param list[int] objectives: the list of objectives, where each element is the number of cells of the corresponding type that need to be obtained
        '''
        self.cells = cells
        self.objectives = objectives
        self.scores = [0] * len(self.objectives)

    def check_completion(self) -> bool:
        '''Checks if all the objectives have been completed

        :return bool: True if all the objectives have been completed, False otherwise
        '''
        completed = True
        i = 0
        while completed and i < len(self.objectives):
            if self.scores[i] < self.objectives[i]:
                completed = False
            i += 1
        return completed
    
    def update_score(self, cell_name: str, amount: int) -> None:
        '''Updates the score by adding the specified amount of cells of the specified type

        :param str cell_name: the name of the cell
        :param int amount: the amount of cells to add
        '''
        i = 0
        while i < len(self.cells) and self.cells[i][0] != cell_name:
            i += 1
        if i < len(self.cells):
            self.scores[i] += amount
        # else: # The cell is not in the list
        #     raise ValueError('The cell is not in the list of cells')
        
    def update_score_from_dict(self, cell_dict: dict[str, int]) -> None:
        '''Updates the score from a dictionary of cells

        :param dict[str, int] cell_dict: the dictionary of cells
        '''
        for cell_name, amount in cell_dict.items():
            self.update_score(cell_name, amount)
