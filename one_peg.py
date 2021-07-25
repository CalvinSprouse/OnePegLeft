from rich import print
import json
import os
import random
import re


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

    def set_space(self, pos_num: int, is_filled: bool):
        """ Changes a legal space. If True the space becomes filled else the space becomes empty """
        if self.is_legal_pos_num(pos_num):
            x, y = self.positions[pos_num]
            self.grid[y][x] = self.filled_space if is_filled else self.empty_space

    def get_pos_char(self, pos_num: int):
        """ Gets the character in the grid at a specified position number """
        if self.is_legal_pos_num(pos_num):
            x, y = self.positions[pos_num]
            return self.grid[y][x]
        return None

    def is_filled(self, pos_num: int):
        """ Returns true if the character at a position number is = the filled space character """
        return self.get_pos_char(pos_num) == self.filled_space

    def is_empty(self, pos_num: int):
        """ Returns true if the character at a position number is = the empty space character """
        return self.get_pos_char(pos_num) == self.empty_space

    def get_adjacent_positions(self, pos_num: int) -> list:
        """ Returns a list of adjacent position numbers to the position provided """
        adjacent_positions = []
        if self.is_legal_pos_num(pos_num):
            x, y = self.positions[pos_num]
            for adj_x, adj_y in [(1, 1), (1, -1), (2, 0), (-2, 0), (-1, 1), (-1, -1)]:
                new_pos = (x + adj_x, y + adj_y)
                if new_pos in self.positions:
                    adjacent_positions.append(self._coord_to_pos(new_pos[0], new_pos[1]))
        return adjacent_positions

    def show(self):
        """ Prints the grid """
        print(self.grid)

    def get_grid(self) -> list:
        return self.grid

    def get_positions(self) -> list:
        return self.positions

    def _coord_to_pos(self, x_pos: int, y_pos: int):
        return self.positions.index((x_pos, y_pos))


class OnePegGame(HexGrid):
    def __init__(self, board_size: int = 5, initial_board: str = None, **kwargs):
        """ The format of a saved board is a string of T and F where each one corresponds to a board position """
        self.board_size = board_size
        super().__init__(self.board_size, self.board_size, **kwargs)

        # configures a unique initial board position
        if initial_board:
            assert (len(initial_board) == len(self.get_positions())
                    and all([c in ["T", "F", "t", "f"] for c in initial_board]))
            for index, char in enumerate(initial_board):
                self.set_space(index, char.upper() == "T")
        else:
            for pos in range(1, len(self.get_positions())):
                self.set_space(pos, True)

    def is_legal_move(self, start_pos_num: int, end_pos_num: int) -> bool:
        """ Returns true if a start piece -> end piece move is legal """
        if not (self.is_filled(start_pos_num) and self.is_empty(end_pos_num)):
            return False
        matching_pos_list = self._get_matching_pos(start_pos_num, end_pos_num)
        if len(matching_pos_list) != 1:
            return False
        if start_pos_num in self.get_adjacent_positions(end_pos_num):
            return False
        return len(self._get_matching_pos(start_pos_num, end_pos_num)) == 1

    def move(self, start_pos_num: int, end_pos_num: int):
        """ Jumps the start piece to the end pos removing the piece that was hopped """
        if self.is_legal_move(start_pos_num, end_pos_num):
            self.set_space(start_pos_num, False)
            self.set_space(end_pos_num, True)
            self.set_space(self._get_matching_pos(start_pos_num, end_pos_num)[0], False)

    def get_legal_moves(self):
        """ Returns a list of legal moves in format """
        legal_moves = []
        empty_positions = [[pos, [adj_pos for adj_pos in self.get_adjacent_positions(pos) if self.is_filled(adj_pos)]]
                           for pos in range(len(self.positions)) if self.is_empty(pos)]
        for pos, adjacent_list in empty_positions:
            for second_adjacent_list in [self.get_adjacent_positions(adj) for adj in adjacent_list]:
                for second_adjacent in second_adjacent_list:
                    if self.is_legal_move(second_adjacent, pos):
                        legal_moves.append((second_adjacent, pos))
        return legal_moves

    def _get_matching_pos(self, start_pos_num: int, end_pos_num: int) -> list:
        """ Returns a list of positions that are adjacent to both start and end positions """
        matches = []
        if self.is_legal_pos_num(start_pos_num) and self.is_legal_pos_num(end_pos_num):
            start_positions = self.get_adjacent_positions(start_pos_num)
            end_positions = self.get_adjacent_positions(end_pos_num)
            matches = [pos for pos in start_positions if pos in end_positions]
        return matches

    def save_board(self):
        return {"size": self.board_size,
                "config": "".join(["T" if self.is_filled(pos) else "F" for pos in range(len(self.positions))])}


class LearningPegGame:
    def __init__(self, save_dir: str = "_memory", board_size: int = 5):
        self.save_dir = os.path.abspath(save_dir)
        os.makedirs(self.save_dir, exist_ok=True)

        self.board_size = board_size

    def play_blind_game(self):
        """ Play a random game with no data """
        game = OnePegGame(self.board_size)
        initial = game.save_board()
        move_list = []
        options = game.get_legal_moves()
        while len(options) > 0:
            selection = random.choice(options)
            game.move(selection[0], selection[1])
            move_list.append(f"{selection[0]}>{selection[1]}-" + game.save_board()["config"])
            options = game.get_legal_moves()
        score = len([pos for pos in range(len(game.get_positions())) if game.is_filled(pos)])
        return {"score": score, "size": initial["size"], "initial": initial["config"], "moves": move_list}

    def play_blind_games(self, count: int):
        """ Plays a number of blind games as a form of dumb data collection """
        best_game = (15, [])
        for i in range(count):
            game = self.play_blind_game()
            if game["score"] < best_game[0] or game["score"] == best_game[0] and len(game["moves"]) < len(best_game[1]):
                best_game = (game["score"], game["moves"])
            self.save_game(game)
            print("Game", i, "Score", game["score"], "Final Config", game["moves"][-1])
        print("Best Game\nScore", best_game[0], "Moves", len(best_game[1]), best_game[1])

    def play_smart_game(self):
        """ Play a game where the computer uses collected data """
        pass

    def play_learning_game(self):
        """ Play a game where the computer tries to make new choices and discover new boards """
        pass

    def save_game(self, game: dict):
        game_save_file = os.path.join(self.save_dir, "games.js")
        if not os.path.exists(game_save_file):
            open(game_save_file, "w").write(json.dumps({}, indent=4))

        if all(key in game for key in ["score", "size", "initial", "moves"]):
            game_dict = json.load(open(game_save_file, "r"))
            unique_key = str(game["size"]) + "-" + game["initial"]
            game_history = {"score": game["score"], "moves": game["moves"]}
            if unique_key not in game_dict:
                game_dict[unique_key] = {"games": [game_history]}
            else:
                game_dict[unique_key]["games"].append(game_history)
            json.dump(game_dict, open(game_save_file, "w"), indent=4)

    def load_moves(self, str_move_list: list):
        """ Converts the move list from a game into understandable data """
        move_list = []
        for move in str_move_list:
            move_search = re.search(r"(?P<start_pos>\d*)>(?P<end_pos>\d*)-(?P<board>.*)", move,
                                    re.IGNORECASE)
            move_list.append([(int(move_search.group("start_pos")), int(move_search.group("end_pos"))), [True if c.upper() == "T" else False for c in move_search.group("board")]])
        return move_list


if __name__ == "__main__":
    game = LearningPegGame()
    game.play_blind_games(100)

# TODO: Create game bot which will take the legal moves determine the best one
# TODO: Extrapolate game out x moves in advance
# TODO: When a board position is seen in a sequence of winning moves enter that sequence
# TODO: Define "win level" based on how many pegs are left, if a "winning sequence" results in more than 1 peg make it a percent change of being used
# TODO: Create "move tree" that has a start position and shows every possible board using data collected in the games
