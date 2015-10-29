#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# CognitiveScale Starfleet Mine Clearing Exercise Evaluator
#

import sys
import copy

class Ship(object):
    """ Represent the ship. """

    def __init__(self, field):
        """ The ship operates in a field, 'field'. """
        self.field = field
        # position ship in center of grid (assumed to be odd nr on
        # each side)
        self.origin_x = self.x = (len(field.grid[0])-1) / 2
        self.origin_y = self.y = (len(field.grid)-1) / 2

    def offset(self):
        """ Return (x, y) offset from origin. """
        return (self.origin_x - self.x, self.origin_y - self.y)

    def hit_mine(self):
        """ Return True if we hit a mine. """
        return self.field.hit_mine(self.x, self.y)

    def missed_mines(self):
        return self.field.missed_mines(self.x, self.y)

    def move(self, direction):
        if 'north' == direction: self.y -= 1
        elif 'south' == direction: self.y += 1
        elif 'east' == direction: self.x += 1
        elif 'west' == direction: self.x -= 1

    def do_down(self):
        """ 'Drop' 1Km. """
        self.field.do_down()

    def process_firing_pattern(self, pattern):
        for volley in pattern:
            x = self.x + volley[0]
            y = self.y + volley[1]
            if self.field.in_mined_space(x, y):
                self.field.fire_torpedo(x, y)

    def fire(self, pattern):
        if 'alpha' == pattern:
            self.process_firing_pattern([(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif 'beta' == pattern:
            self.process_firing_pattern([(-1, 0), (0, -1), (0, 1), (1, 0)])
        elif 'gamma' == pattern:
            self.process_firing_pattern([(-1, 0), (0, 0), (1, 0)])
        elif 'delta' == pattern:
            self.process_firing_pattern([(0, -1), (0, 0), (0, 1)])

class Field(object):
    """ Represent a 3-D cuboid "field". """

    def __init__(self, grid):
        """
        An 'a' character represents a mine that is 1km away; 'b' is a mine 2km
        away, through 'z' for a mine 26km away. An 'A' character represents a
        mine 27km away, through 'Z' for a mine 52km away. A . (period)
        represents empty space all the way through the cuboid. At most 1 mine
        can occupy a given coordinate in the cuboid. If two mines share x- and
        y-coordinates, but have different z- coordinates, only the closest of
        those mines is represented in the grid.
        """

        self.nr_mines = 0
        self.grid = []
        map(lambda row: self.grid.append(self.parse_row(row)), grid)

        self.max_x = len(self.grid[0])
        self.max_y = len(self.grid)

    def parse_row(self, row):
        """ Parse one row of the input grid e.g. '..a' """
        def xlate(c):
            if '.' == c: return None

            self.nr_mines += 1
            if ord(c) >= ord('a'): return ord(c) - ord('a') + 1
            elif ord(c) >= ord('A'): return ord(c) - ord('A') + 27

        row = map(xlate, row)
        return row

    def do_down(self):
        """ 'Drop' one step (1Km) e.g. adjust the distances by -1. """

        def dec_val(n):
            if n: return n - 1
            return None

        def dec_row(row):
            return map(dec_val, row)

        self.grid = map(dec_row, self.grid)

    def in_mined_space(self, x, y):
        """ Return True if within the initial grid coordinates else False. """
        if x >= 0 and x < self.max_x \
            and y >= 0 and y < self.max_y:
            return True
        return False

    def missed_mines(self, x, y):
        """ Return True if within the initial grid coordinates and
        mines on this level else False. """
        if self.in_mined_space(x, y):
            def check_row(row):
                return reduce(lambda x, y: x or y, map(lambda n: 0 == n, row))

            return reduce(lambda x, y: x or y, map(check_row, self.grid))
        return False

    def fire_torpedo(self, x, y):
        if self.grid[y][x]:
            # hit a mine
            self.grid[y][x] = None
            self.nr_mines -= 1

    def hit_mine(self, x, y):
        """ Return True if we hit a mine. """
        if 0 == self.grid[y][x]:
            return True
        return False

class Scorer(object):
    """ Keep score.

    The starting score is 10 times the initial number of mines in the
    cuboid.

    Subtract 5 points for every shot fired, but no more than 5 times the
    number of initial mines.

    Subtract 2 points for every km moved north, south east or west (not
    for kms dropped), but no more that 3 times the number of initial
    mines. """

    fire_penalty = 5
    move_penalty = 2

    def __init__(self, nr_mines):
        self.score = nr_mines * 10
        self.max_shots_fired_penalty = nr_mines * 5
        self.max_move_penalty = nr_mines * 3

    def fired(self):
        """ Adjust score due to firing. """
        if Scorer.fire_penalty <= self.max_shots_fired_penalty:
            self.max_shots_fired_penalty -= Scorer.fire_penalty
            self.score -= Scorer.fire_penalty
        pass

    def moved(self):
        """ Adjust score due to moving. """
        if Scorer.move_penalty <= self.max_move_penalty:
            self.max_move_penalty -= Scorer.move_penalty
            self.score -= Scorer.move_penalty

    def fail(self):
        """ A fail, zero the score. """
        self.score = 0

    def has_remaining(self):
        """ Passed, with remaining steps. """
        self.score = 1

class View(object):
    """ View object.

    When the grid is printed (before and after every move), it should be
    drawn so that the vessel is in the middle of the grid, and the grid
    should be no larger than necessary. """

    def __init__(self, ship, field):
        self.ship = ship
        self.field = field

    def normalize_grid(self):
        """ Return grid which is adjusted to account for ship movement. """
        offset_x, offset_y = self.ship.offset()
        grid = copy.deepcopy(self.field.grid)

        if offset_x > 0:
            # add columns to the "left"
            grid_ = []
            def prepend(row):
                row_ = [None] * offset_x * 2
                map(lambda el: row.insert(0, el), row_)
            map(lambda row: prepend(row), grid)

        elif offset_x < 0:
            # add columns to the "right"
            grid_ = []
            def append(row):
                row_ = [None] * abs(offset_x) * 2
                map(lambda el: row.append(el), row_)
            map(lambda row: append(row), grid)

        width = len(grid[0])
        if offset_y > 0:
            # add rows to the "top"
            grid_ = [[None] * width] * offset_y * 2
            map(lambda row: grid.insert(0, row), grid_)
            #grid = grid_

        elif offset_y < 0:
            # add rows to the "bottom"
            grid_ = [[None] * width] * abs(offset_y) * 2
            map(lambda row: grid.append(row), grid_)

        return grid

    def shrink(self, grid):
        """ Shrink the grid so it is no larger than necessary. """

        def empty(l):
            """ Return True if 'l' has no mines else False. """
            return reduce(lambda x, y: x and y, map(lambda n: n is None, l))

        def shrink_vert(grid):
            if len(grid) > 1 and empty(grid[0]) and empty(grid[-1]):
                return shrink_vert(grid[1:-1])
            return grid

        def shrink_horz(grid, n=0):
            def extract_col(grid, n):
                # Extract col 'n' from grid.
                return list(zip(*grid)[n])

            ln = len(grid[0])
            if ln > 1 and n < ln / 2:
                col_0 = extract_col(grid, n)
                col_n = extract_col(grid, ln-n-1)
                if empty(col_0) and empty(col_n):
                    return shrink_horz(grid, n+1)
                else:
                    if n == ln-n-1:
                        # extract single column
                        return map(lambda x: [x], list(zip(*grid)[n]))

            # extract multiple columns
            return map(lambda r: [e for e in r], zip(*zip(*grid)[n:ln-n]))

        grid = shrink_vert(grid)
        grid = shrink_horz(grid)

        return grid

    def print_grid(self):
        def xlate(n):
            if n is None: return '.'
            elif n >= 27: return chr(n-27+ord('A'))
            elif n >= 1: return chr(n-1+ord('a'))
            elif n == 0: return '*'
            else: print("unexpected, debug")

        def print_row(row):
            row = map(xlate, row)
            print ''.join(row)

        grid = self.normalize_grid()
        grid = self.shrink(grid)
        map(print_row, grid)

def process_script(script, ship, field):
    """ Process script on ship. """

    scorer = Scorer(field.nr_mines)
    view = View(ship, field)

    nr_step = 1
    for line in script:
        print('\nStep %d\n' % nr_step)
        view.print_grid()
        print('\n%s\n' % line)
        cmds = line.split()
        for cmd in cmds:
            if cmd.startswith('#'): pass
            elif cmd in ['north', 'south', 'east', 'west']:
                ship.move(cmd)
                scorer.moved()
            elif cmd in ['alpha', 'beta', 'gamma', 'delta']:
                ship.fire(cmd)
                scorer.fired()

            else: print('Unknown command: %s' % cmd)

        ship.do_down()
        view.print_grid()

        if ship.hit_mine():
            # 1) We hit a mine
            scorer.fail()
            break

        if ship.missed_mines():
            # 2) script completed but mines still remaining - fail (0 points)
            scorer.fail()
            break

        if 0 == field.nr_mines:
            # 3) all mines cleared, but steps remaining - pass (1 point)
            if nr_step < len(script):
                scorer.has_remaining()
            break

        nr_step += 1

    if field.nr_mines:
        # 2) script completed but mines still remaining - fail (0 points)
        scorer.fail()

    if 0 == scorer.score:
        print('\nfail (0)')
    else:
        print('\npass (%d)' % scorer.score)

def read_input(fname):
    lines = []
    with open(fname) as f:
        for line in f:
            lines.append(line.rstrip())

    return lines

def main(fnames):
    grid = read_input(fnames[0])
    script = read_input(fnames[1])

    field = Field(grid)
    ship = Ship(field)
    process_script(script, ship, field)

def die(msg):
    print('error: %s' % msg)
    sys.exit(-1)

def usage():
    print('Usage: %s field_file script_file' % sys.argv[0])

if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        die("Missing input")

    rc = main(sys.argv[1:])
    sys.exit(rc)
