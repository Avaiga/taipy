
import pandas as pd


GAME_DATA = pd.read_csv("../data/games.csv")


def get_file_number(column):
    """
    Get file number

    Args:
    file (str): The file

    Returns:
    int: The file number
    """

    match column:
        case "a":
            return 0
        case "b":
            return 1
        case "c":
            return 2
        case "d":
            return 3
        case "e":
            return 4
        case "f":
            return 5
        case "g":
            return 6
        case "h":
            return 7
        case _:
            return -1

def get_square(move):
    """
    Get the square of the move

    Args:
    move (str): The move

    Returns:
    list: The square
    """

    color = "w" if move[0] == move[0].upper() else "b"

    if "O-O" in move:
        return [6, 0, 5, 0] if color == "w" else [6, 7, 5, 7]
    elif "O-O-O" in move:
        return [2, 0, 3, 0] if color == "w" else [2, 7, 3, 7]

    if "=" in move:
        if "x" in move:
            move = move[2:4]
        else:
            move = move[0:2]
    elif move[-1] == "+" or move[-1] == "#":
        move = move[-3:-1]
    else:
        move = move[-2:]

    file_number = get_file_number(move[0])
    rank = 8 - int(move[1])

    return [file_number, rank]




def get_heatmap_data():
    """
    Get heatmap data

    Returns:
    list: The heatmap data
    """

    heatmap_data = [[0 for _ in range(8)] for _ in range(8)]

    for _, row in GAME_DATA.iterrows():
        moves = row['moves'].split(" ")
        for move in moves:
            square = get_square(move)
            heatmap_data[square[1]][square[0]] += 1
            if len(square) > 2:
                heatmap_data[square[2]][square[3]] += 1

    return heatmap_data


def get_first_move_data():
    """
    Get first move data

    Returns:
    list: The first move data
    """

    first_move_data = [[0 for _ in range(8)] for _ in range(8)]

    for _, row in GAME_DATA.iterrows():
        moves = row['moves'].split(" ")
        white_move = moves[0]
        white_square = get_square(white_move)
        first_move_data[white_square[1]][white_square[0]] += 1
        if len(moves) < 2:
            continue
        
        black_move = moves[1]
        black_square = get_square(black_move)
        first_move_data[black_square[1]][black_square[0]] += 1

    return first_move_data

def get_piece_from_move(move):
    """
    Get the piece from the move

    Args:
    move (str): The move

    Returns:
    str: The piece
    """

    match move[0]:
        case "N":
            return "N"
        case "B":
            return "B"
        case "R":
            return "R"
        case "Q":
            return "Q"
        case "K":
            return "K"
        case _:
            return "P"

def get_first_move_data_by_piece(piece):
    """
    Get first move data

    Returns:
    list: The first move data
    """

    first_move_data = [[0 for _ in range(8)] for _ in range(8)]

    for _, row in GAME_DATA.iterrows():
        moves = row['moves'].split(" ")
        white_move = moves[0]
        white_square = get_square(white_move)
        if get_piece_from_move(white_move) == piece:
            first_move_data[white_square[1]][white_square[0]] += 1

        if len(moves) < 2:
            continue
        
        black_move = moves[1]
        black_square = get_square(black_move)
        if get_piece_from_move(black_move) == piece:
            first_move_data[black_square[1]][black_square[0]] += 1

    return first_move_data
if __name__ == "__main__":
    with open('board_heatmap_data.txt', 'w') as f:
        f.write(str(get_heatmap_data()))
    
    with open('first_move_data.txt', 'w') as f:
        f.write(str(get_first_move_data()))
    
    with open('first_pawn_move_data.txt', 'w') as f:
        f.write(str(get_first_move_data_by_piece("P")))
    
    with open('first_knight_move_data.txt', 'w') as f:
        f.write(str(get_first_move_data_by_piece("N")))
