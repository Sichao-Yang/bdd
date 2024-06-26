#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ite import Ite
from robdd import Robdd
from apply import app
from operators import Bdd


def queens(n):
    solution = Robdd.init_build_true()
    # create the rule "there must be at least one queen at each line"
    for j in range(1, n + 1):
        line = Robdd.init_build_false()
        for i in range(1, n + 1):
            queen = Robdd.init_build_x(index_of(i, j))
            line = app(line, Bdd.OR, queen)
        solution = app(solution, Bdd.AND, line)

    # create a list of "NOT" expressions
    not_expressions = {}
    for j in range(1, n + 1):
        for i in range(1, n + 1):
            not_expressions[(i, j)] = Robdd.init_build_not_x(index_of(i, j))

    # create conditions for each position
    for j in range(1, n + 1):
        for i in range(1, n + 1):
            queen = queen_conditions(not_expressions, i, j, n)
            solution = app(solution, Bdd.AND, queen)

    return solution


def queen_conditions(not_x, i, j, n):
    queen = Robdd.init_build_x(index_of(i, j))
    # creates the rule "none in the same column"
    a = Robdd.init_build_true()
    for y in range(1, n + 1):
        if y == j:
            continue
        a_ = app(queen, Bdd.IMPL, not_x[(i, y)])
        a = app(a, Bdd.AND, a_)

    # creates the rule "none in the same line"
    b = Robdd.init_build_true()
    for x in range(1, n + 1):
        if x == i:
            continue
        b_ = app(queen, Bdd.IMPL, not_x[(x, j)])
        b = app(b, Bdd.AND, b_)

    # creates the rule "none in the diagonals"
    c = Robdd.init_build_true()
    x = 1
    while (i - x) > 0 and (j - x) > 0:
        c_ = app(queen, Bdd.IMPL, not_x[(i - x, j - x)])
        c = app(c, Bdd.AND, c_)
        x += 1
    x = 1
    while (i + x) <= n and (j + x) <= n:
        c_ = app(queen, Bdd.IMPL, not_x[(i + x, j + x)])
        c = app(c, Bdd.AND, c_)
        x += 1

    d = Robdd.init_build_true()
    x = 1
    while (i - x) > 0 and (j + x) <= n:
        d_ = app(queen, Bdd.IMPL, not_x[(i - x, j + x)])
        d = app(d, Bdd.AND, d_)
        x += 1

    x = 1
    while (i + x) <= n and (j - x) > 0:

        d_ = app(queen, Bdd.IMPL, not_x[(i + x, j - x)])
        d = app(d, Bdd.AND, d_)
        x += 1

    return app(app(a, Bdd.AND, b), Bdd.AND, app(c, Bdd.AND, d))


def index_of(i, j):
    return i + ((j - 1) * n)


def display_solution(sol, n):
    for k, v in sol.items():
        if v:
            sign = '+'
        else:
            sign = 'o'
        print("{} ".format(sign), end="")
        if (k-1) % n == 0:
            print()
            
if __name__ == "__main__":
    from time import time

    for n in range(8, 9):
        start = time()
        result = queens(n)
        elapsed = time() - start

        if n == 8:
            assert result.solutions_len() == 92
        
        print("N =".format(n))
        print("   solutions       ={}".format(result.solutions_len()))
        print("   elapsed time    = {:.2f}s".format(elapsed))
        print("   variables       ={}".format(len(result.variables)))
        print("   nodes (reduced) ={}".format(result.insert_distinct))
        print("   nodes (attempts)={}".format(result.insert_attempts))
        print("   resolution: ")
        display_solution(result.get_solutions()[0], n)