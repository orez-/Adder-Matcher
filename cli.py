import os
import time

if os.name == 'nt':  # Windows
    import colorama
    colorama.init()

import game
import get_key


SLEEP_TIME = 0.5
RED = 31
YELLOW = 33
GREEN = 32

clear = '\x1b[0m'


def get_color(elem):
    return ((elem - 1) % 7) + 1


num_representation = ' 123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def display_tty(board, selector=None):
    print("Score: {:,}".format(board.score * 10))
    print(("\033[{}m" + "o" * board.health).format({
        1: RED,
        game.MAX_HEALTH: GREEN,
    }.get(board.health, YELLOW)))
    for r, row in enumerate(board.board):
        for c, elem in enumerate(row):
            if elem is None:
                print(end=' ')
            elif selector == (r, c):
                print(
                    "\033[4{};30m".format(get_color(elem)),
                    end=num_representation[elem],
                )
                print(clear, end='')
            else:
                print("\033[3{}m".format(get_color(elem)), end=num_representation[elem])
        print(clear)
    print('\n')


def play_game():
    board = game.GameBoard()
    r, c = 0, 0

    dir_lookup = {
        'w': (-1, 0),
        'a': (0, -1),
        's': (1, 0),
        'd': (0, 1),
        get_key.UP_ARROW: (-1, 0),
        get_key.LEFT_ARROW: (0, -1),
        get_key.DOWN_ARROW: (1, 0),
        get_key.RIGHT_ARROW: (0, 1),
    }

    key = 0
    while key != '\x03':
        display_tty(board, (r, c))
        key = get_key.getch()
        if key in dir_lookup:
            rd, cd = dir_lookup[key]
            r = sorted([0, r + rd, game.HEIGHT - 1])[1]
            c = sorted([0, c + cd, game.WIDTH - 1])[1]
        elif key in set('e \r'):
            for b in board.advance_tile(r, c):
                display_tty(board, board.last_collapsed)
                time.sleep(SLEEP_TIME)
            if not board.health:
                display_tty(board)
                board.score += sum(map(sum, board.board))
                print("Game Over! Final score: {:,}".format(board.score * 10))
                break
