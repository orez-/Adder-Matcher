# coding=utf-8
from __future__ import print_function

import collections
import random
import time

import get_key


try:
    range = xrange
except:
    pass


START_MAX = 3
MINIMUM_COLLAPSE = 3
HEIGHT = 5
WIDTH = 5



ab = '\x1b[48;5;{}m'
af = '\x1b[38;5;{}m'
clear = '\x1b[0m'
# B: "\033[0;36m▒",
# Y: "\033[0;33m▒",
# R: "\033[0;31m▒",
# G: "\033[0;32m▒",
# P: "\033[0;35m▒",


class GameBoard(object):
    def __init__(self):
        self.board = [
            [
                random.randint(1, START_MAX)
                for _ in range(WIDTH)
            ] for _ in range(HEIGHT)
        ]
        self._highest = START_MAX  # TODO?

        # Starting board is pre-collapsed.
        self._collapse_all()


    def _neighbors(self, r, c):
        return [
            ((r1, c1), self.board[r1][c1]) for r1, c1 in
            [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)]
            if 0 <= r1 < HEIGHT and 0 <= c1 < WIDTH
        ]

    def _find_matches(self):
        """
        Find the first contiguous set of tiles whose values match in
        a sizeable group (as determined by MINIMUM_COLLAPSE) and return
        the coordinate to which they should collapse and their set.

        Search order is reading order: left to right, top to bottom.
        """
        seen_set = set()
        for r, row in enumerate(self.board):
            for c, number in enumerate(row):
                if (r, c) in seen_set:
                    continue
                collapse_set = self._get_matches_at(r, c)
                if len(collapse_set) >= MINIMUM_COLLAPSE:
                    return (r, c), collapse_set
                seen_set |= collapse_set
        return None

    def _get_matches_at(self, r, c):
        """
        Get the contiguous set of tiles whose values match those at the
        given coordinate.
        """
        # BFS
        number = self.board[r][c]
        collapse_set = set()
        queue = collections.deque([(r, c)])
        while queue:
            r, c = queue.popleft()
            for coord, elem in self._neighbors(r, c):
                if elem == number and coord not in collapse_set:
                    queue.append(coord)
                    collapse_set.add(coord)
        return collapse_set

    def advance_tile(self, r, c):
        self.board[r][c] += 1
        collapse_set = self._get_matches_at(r, c)
        if len(collapse_set) < MINIMUM_COLLAPSE:
            self._highest = max(self._highest, self.board[r][c])
            # TODO: Take a damage.
            return
        # Otherwise collapse it, and start looking for more to collapse.
        self._collapse(collapse_set, (r, c))
        self._collapse_all()

    def _collapse_all(self):
        while True:
            matches = self._find_matches()
            if not matches:
                break
            r_c, collapse_set = matches
            self._collapse(collapse_set, r_c)

    def _collapse(self, collapse_set, r_c):
        """
        Collapse the elements in collapse_set into the point r_c, drop
        the cells above into the new spaces, and fill the empty top
        with new cells.
        """
        # The board is easier to work with if we flip it on its side.
        board = list(map(list, zip(*self.board)))
        for y, x in collapse_set:
            if (y, x) == r_c:
                board[x][y] += 1
                self._highest = max(self._highest, board[x][y])
            else:
                board[x][y] = None

        for column in board:
            column[:] = [elem for elem in column if elem is not None]
            column[:] = [
                random.randint(1, self._highest - 1)
                for _ in range(HEIGHT - len(column))
            ] + column
        self.board = list(map(list, zip(*board)))


def get_color(elem):
    return ((elem - 1) % 7) + 1


def display_tty(board, selector=None):
    for r, row in enumerate(board.board):
        for c, elem in enumerate(row):
            if selector == (r, c):
                print("\033[4{elem};3{elem}m".format(elem=get_color(elem)), end=str(elem))
                print(clear, end='')
            else:
                print("\033[3{}m".format(get_color(elem)), end=str(elem))
        print(clear)
    print()


if __name__ == '__main__':
    board = GameBoard()
    r, c = 0, 0

    dir_lookup = {
        'w': (-1, 0),
        'a': (0, -1),
        's': (1, 0),
        'd': (0, 1),
    }

    key = 0
    while key != '\x03':
        display_tty(board, (r, c))
        key = get_key.getch()
        if key in dir_lookup:
            rd, cd = dir_lookup[key]
            r = sorted([0, r + rd, HEIGHT - 1])[1]
            c = sorted([0, c + cd, WIDTH - 1])[1]
        elif key == 'e':
            board.advance_tile(r, c)
