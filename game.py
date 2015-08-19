import collections
import random


START_MAX_VALUE = 3
MAX_HEALTH = 5
MINIMUM_COLLAPSE = 3
HEIGHT = 5
WIDTH = 5


class GameBoard(object):
    def __init__(self):
        self.board = [
            [
                random.randint(1, START_MAX_VALUE)
                for _ in range(WIDTH)
            ] for _ in range(HEIGHT)
        ]
        self._highest = START_MAX_VALUE  # TODO?
        self.last_collapsed = None
        self.score = 0
        self.health = MAX_HEALTH

        # Starting board is pre-collapsed.
        for _ in self._collapse_all():
            pass

        self.score = 0

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
        self.health -= 1
        if len(collapse_set) < MINIMUM_COLLAPSE:
            self._highest = max(self._highest, self.board[r][c])
            return
        # Otherwise collapse it, and start looking for more to collapse.
        yield from self._collapse(collapse_set, (r, c))
        yield from self._collapse_all()

    def _collapse_all(self):
        while True:
            matches = self._find_matches()
            if not matches:
                break
            r_c, collapse_set = matches
            yield from self._collapse(collapse_set, r_c)

    def _collapse(self, collapse_set, r_c):
        """
        Collapse the elements in collapse_set into the point r_c, drop
        the cells above into the new spaces, and fill the empty top
        with new cells.
        """
        # The board is easier to work with if we flip it on its side.
        board = list(map(list, zip(*self.board)))
        y, x = r_c
        value = board[x][y]
        for y, x in collapse_set:
            if (y, x) == r_c:
                board[x][y] += 1
                self._highest = max(self._highest, board[x][y])
            else:
                board[x][y] = None

        self.board = list(map(list, zip(*board)))
        self.last_collapsed = r_c
        self.score += len(collapse_set) * value
        self.health = min(self.health + 1, MAX_HEALTH)
        yield self

        for column in board:
            column[:] = [elem for elem in column if elem is not None]
            column[:] = [
                random.randint(1, self._highest - 1)
                for _ in range(HEIGHT - len(column))
            ] + column
        self.board = list(map(list, zip(*board)))
        self.last_collapsed = None
        yield self
