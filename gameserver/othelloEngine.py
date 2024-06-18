# Code that allows you to play othello.
# A board is a row-major 2d array
# Each space on the board is represented by a single character '-', 'B', or 'W'

from typing import NewType, List  # For type hints
import sys

# Custom type for type hints. Don't remove unless you're going to remove all of the type hints as well.
Board = NewType('Board', List[List[str]])


def string_to_array(board_string: str):
    board_array = []
    for i in range(0, len(board_string), 8):
        row = board_string[i:i+8]
        board_array.append(list(row))
    return board_array


def array_to_string(board: Board):
    boardstring = ""
    for row in board:
        for char in row:
            boardstring = boardstring + char
    return boardstring


def get_possible_moves(board: Board, player: str):
    possible_moves = []
    for i in range(8):
        for j in range(8):
            if board[i][j] == "-":
                # Check all adjacent cells for potential moves
                for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if is_valid_move(board, player, i, j, d_row, d_col):
                        possible_moves.append((i, j))
                        break
    return possible_moves


def is_valid_move(board: Board, player: str, row: int, col: int, d_row: int, d_col: int):
    if player == "B":
        opponent = "W"
    else:
        opponent = "B"

    if board[row][col] != "-":
        return False
    # Move to adjacent cell
    row += d_row
    col += d_col

    # Check if adjacent cell is in board boundaries and has opponent color
    if not (0 <= row < 8 and 0 <= col < 8) or board[row][col] != opponent:
        return False
    # Keep goingin the same direction until reaching a cell with the player's color
    while 0 <= row < 8 and 0 <= col < 8:
        # If cell with the player's color is found, move is valid
        if board[row][col] == player:
            return True
        # If an empty cell is found then the move is not valid
        elif board[row][col] == "-":
            return False
        row += d_row
        col += d_col
    return False


def get_flips(board: Board, move_row: int, move_col: int):  # removed player from params
    flips = []

    player = board[move_row][move_col]

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for d_row, d_col in directions:
        row, col = move_row + d_row, move_col + d_col
        temp_flips = []

        # Keep moving in current direction until edge of the board or an empty cell is reached
        while 0 <= row < 8 and 0 <= col < 8 and board[row][col] != "-":
            if board[row][col] == player:
                flips.extend(temp_flips)
                break
            else:
                temp_flips.append((row, col))
            row += d_row
            col += d_col

    return flips


def flip_pieces(board: Board, flips: List[tuple]):
    for row, col in flips:
        if board[row][col] == "B":
            board[row][col] = "W"
        else:
            board[row][col] = "B"
    return board


def print_board(board: Board):
    for row in board:
        print(file=sys.stderr)
        for piece in row:
            print(piece, end=' ', file=sys.stderr)
    print()


def replace_at_coord_for_strings(string: str, char: str, row: int, col: int):
    index = row*8 + col
    string = string[:index] + char + string[index+1:]
    return string


def replace_at_coord(board: Board, char: str, row: int, col: int):
    board[row][col] = char
    return board


def calculate_winner(board: Board):
    black_count: 0
    white_count: 0
    if black_count > white_count:
        return "B"
    return "W"


def start_board():
    return "---------------------------WB------BW---------------------------"


def is_endgame(board: Board):
    empty_spaces = 0
    black_count = 0
    white_count = 0

    for row in board:
        for cell in row:
            if cell == "-":
                empty_spaces += 1
            elif cell == "B":
                black_count += 1
            elif cell == "W":
                white_count += 1

    if empty_spaces == 0:
        if black_count > white_count:
            return "B"
        elif white_count > black_count:
            return "W"
        else:
            return "Tie"
    else:
        # Check if neither player can play a move
        black_moves = get_possible_moves(board, "B")
        white_moves = get_possible_moves(board, "W")

        if len(black_moves) == 0 and len(white_moves) == 0:
            if black_count > white_count:
                return "B"
            elif white_count > black_count:
                return "W"
            else:
                return "T"
        else:
            return "0"


def get_best_move(possible_moves: list, board: Board, player: str) -> list:
    edge_moves = []
    max_flips = -1
    best_move = None
    if len(possible_moves) <= 1:
        return possible_moves
    # Check for edge moves
    for move in possible_moves:
        if move[0] == 0 or move[0] == 7 or move[1] == 0 or move[1] == 7:
            edge_moves.append(move)

    # If there are edge moves, find the one that flips the most pieces
    if edge_moves:
        max_flips = -1
        best_move = None
        for move in edge_moves:
            flips = count_flips(board, move, player)
            if flips > max_flips:
                max_flips = flips
                best_move = move
        possible_moves.remove(best_move)
        possible_moves.insert(0, best_move)
        return possible_moves

    max_flips = -1
    best_move = None

    # Find the move that flips the most pieces
    for move in possible_moves:
        flips = count_flips(board, move, player)
        if flips > max_flips:
            max_flips = flips
            best_move = move
    # Move the best move to the front of the list
    possible_moves.remove(best_move)
    possible_moves.insert(0, best_move)
    return possible_moves


def count_flips(board: Board, move: tuple, player: str) -> int:
    flips_count = 0
    move_row, move_col = move
    opponent = "B" if player == "W" else "W"  # Determine opponent's player
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for delta_row, delta_col in directions:
        row, col = move_row + delta_row, move_col + delta_col
        # Keep moving in current direction until edge of the board or an empty cell is reached
        while 0 <= row < 8 and 0 <= col < 8 and board[row][col] == opponent:
            flips_count += 1
            row += delta_row
            col += delta_col
            # Break if the player's piece is found after a sequence of opponent's pieces
            if 0 <= row < 8 and 0 <= col < 8 and board[row][col] == player:
                break


    return flips_count