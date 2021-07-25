from rich import print


class HexGrid:
    def __init__(self, width: int, height: int,
                 empty_space: str = "0", filled_space: str = "X", illegal_space: str = "-"):
        """
        Creates a "hex" grid where 'O' = legal empty space, 'X' = legal filled space, and '-' = illegal space
        Only legal positions in the shape of a triangle can be accessed and are defined sequentially top-down left-right
        by number. Pos 1 will be the second legal position (due to lists)
        """
        self.empty_space = empty_space
        self.filled_space = filled_space
        self.illegal_space = illegal_space

        self.width = width * 2 - 1
        self.height = height if height % 2 == 1 else height + 1
        self.positions = []
        self.grid = [[self.empty_space if x % 2 == y % 2 else self.illegal_space for x in
                      range(width if width % 2 == 1 else width + 1)]
                     for y in range(self.height)]

        self.positions = []

        # TODO: Find optimization for grid illegal space filling and duplicating
        for row_i, row in enumerate(self.grid):
            for col_i, col in enumerate(row):
                if row_i + col_i + 1 < width:
                    self.grid[row_i][col_i] = self.illegal_space
            self.grid[row_i] = self.grid[row_i] + list(reversed(self.grid[row_i]))[1:]

        for y, row in enumerate(self.grid):
            for x, col in enumerate(row):
                if self.grid[y][x] != self.illegal_space:
                    self.positions.append((x, y))

    def is_legal_pos_num(self, pos_num: int):
        """ Returns True of the pos_num is a real position in the position list (prevents index errors) """
        return 0 <= pos_num <= len(self.positions)

    def get_pos_char(self, pos_num: int):
        """ Gets the character in the grid at a specified position number """
        if self.is_legal_pos_num(pos_num):
            x, y = self.positions[pos_num]
            return self.grid[y][x]

    def is_filled(self, pos_num: int):
        """ Returns true if the character at a position number is = the filled space character """
        return self.get_pos_char(pos_num) == self.filled_space

    def is_empty(self, pos_num: int):
        """ Returns true if the character at a position number is = the empty space character """
        return self.get_pos_char(pos_num) == self.empty_space

    def set_space(self, pos_num: int, is_filled: bool):
        """ Changes a legal space. If True the space becomes filled else the space becomes empty """
        if self.is_legal_pos_num(pos_num):
            x, y = self.positions[pos_num]
            self.grid[y][x] = self.filled_space if is_filled else self.empty_space

    def _coord_to_pos(self, x_pos: int, y_pos: int):
        """ Convert x and y coordinates to positions (since I cant figure out adjacency) """
        # TODO: Figure out how to get adjacent tiles and change this to an is adjacent checker
        return self.positions.index((x_pos, y_pos))

    def show(self):
        """ Prints the grid """
        print(self.grid)

    def get_grid(self) -> list:
        return self.grid

    def get_positions(self) -> list:
        return self.positions


class OnePegGame(HexGrid):
    def __init__(self, board_size: int = 5, initial_board: list = None, **kwargs):
        super().__init__(board_size, board_size, **kwargs)

        if initial_board:
            assert (len(initial_board) == len(self.get_positions())
                    and all([type(b) == bool for b in initial_board]))
            for index, tile in enumerate(initial_board):
                self.set_space(index, tile)
        else:
            for pos in range(len(self.get_positions())[1:]):
                self.set_space(pos, True)

    def is_legal_move(self, start_pos_num: int, end_pos_num: int) -> bool:
        if not (self.is_legal_pos_num(start_pos_num) and self.is_legal_pos_num(end_pos_num)):
            return False

        start_x, start_y = self.positions[start_pos_num]
        end_x, end_y = self.positions[end_pos_num]

        if min(start_x, end_x) + 2 == max(start_x, start_y) and min(start_y, end_y) + 2 == max(start_y, end_y):
            mid_x = start_x + 1
            mid_y = start_y + 1
            if start_x > end_x:
                mid_x = start_x - 1
            if start_y > end_y:
                mid_y = start_y - 1
            return self.is_filled(self._coord_to_pos(mid_x, mid_y))
        elif min(start_x, end_x) + 4 == max(start_x, end_x) and start_y == end_y:
            return self.is_filled(self._coord_to_pos(min(start_x, end_x) + 2, start_y))
        return False

    def hop(self, start_pos_num: int, end_pos_num: int):
        if self.is_legal_move(start_pos_num, end_pos_num):
            self.set_space(start_pos_num, False)
            self.set_space(end_pos_num, True)
            # TODO: Set mid pos to empty

    def get_legal_moves(self):
        # TODO: Find format for legal moves such as tuple[start_pos_num, end_pos_num]
        pass

    def get_between_piece(self, start_pos: int, end_pos: int):
        # TODO: Get pos num of the piece between two positions (if such a thing exists)
        pass


game = OnePegGame()
game.show()

# TODO: Create game bot which will take the legal moves determine the best one
# TODO: Extrapolate game out x moves in advance
# TODO: Save board positions and legal moves
# TODO: Save wins as a sequence of moves
# TODO: When a board position is seen in a sequence of winning moves enter that sequence
# TODO: Define "win level" based on how many pegs are left, if a "winning sequence" results in more than 1 peg make it a percent change of being used
