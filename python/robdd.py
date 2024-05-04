#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ite import Ite
from sys import maxsize


class Robdd:
    # static helper methods
    @staticmethod
    def init_build_true():
        return Robdd.init_build(Ite(1, 1, 1))

    @staticmethod
    def init_build_false():
        return Robdd.init_build(Ite(1, 0, 0))

    @staticmethod
    def init_build_x(i):
        return Robdd.init_build(Ite(i, 1, 0))

    @staticmethod
    def init_build_not_x(i):
        return Robdd.init_build(Ite(i, 0, 1))

    @staticmethod
    def init_build(_ite):
        r = Robdd()
        r.build(_ite)
        return r

    # instance definition
    def __init__(self):
        self.clear()

    def clear(self):
        # T & H tables, T for recording the order of node initializaiton, 
        # H used to check if a ite has been made before
        self.items = []
        self.inverse = {}

        # these are just for stats
        self.variables = []
        self.insert_attempts = 0
        self.insert_distinct = 0
        # this is to init the T table like suggested in report
        # root is the index of items and it represents the root of the DAG
        self.root = None  # root of the robdd tree
        self._make(maxsize, None, None)  # inserts a node for False
        self._make(maxsize, None, None)  # inserts a node for True

    # builds a structure from a Ite expression
    def build(self, expression):
        if not isinstance(expression, Ite):
            raise "Expression is not an Ite class object"
        self.root = self._build(expression)

    def _build(self, expression):
        # recursive call to build the tree, make from bottom up
        inserting_t = (
            expression.t if expression.t_is_bool() else self._build(expression.t)
        )
        inserting_f = (
            expression.f if expression.f_is_bool() else self._build(expression.f)
        )
        return self.make(expression.i, inserting_t, inserting_f)

    # inserts nodes w/ redundancy check
    # Num i - variable number
    # Num t - variable number of the T child
    # Num f - variable number of the F child
    def make(self, i, t, f):
        # this function coresponds to MK function in tutorial
        self.insert_variable(i)
        self.insert_attempts += 1

        if t == f:
            # the t and the f children are equal,
            # so the i variable can be ignored
            return t

        # check if this is a redundant node
        n = self.lookup(i, t, f)

        if n == None:
            n = self._make(i, t, f)
            self.insert_distinct += 1
        return n

    def insert_variable(self, i):
        if i in self.variables:
            return
        self.variables.append(i)

    def _make(self, v, t, f):
        index = len(self.items)
        self.items.append((v, t, f))
        self.inverse[(v, t, f)] = index
        return index

    def lookup(self, v, t, f):
        return self.inverse[(v, t, f)] if (v, t, f) in self.inverse else None

    def __str__(self):
        return self.show(self.root)

    def show(self, index, ident=0):
        ident_str = ident * " "

        if index <= 1:
            return ident_str + str(index)

        i, t, f = self.items[index]

        return ident_str + "x{}\n".format(i) + self.show(t) + "\n" + self.show(f)

    def list(self):
        result = ""

        for index in range(len(self.items)):
            i, t, f = self.items[index]
            result += "{} ({}, {}, {})\n".format(index, i, t, f)

        return result

    def get_root(self):
        return (len(self.items) - 1) if self.root == None else self.root

    def solutions_len(self):
        return self._solutions_len(self.get_root())

    def _solutions_len(self, index):
        if index < 0:
            raise "invalid index"

        if index < 2:
            return index

        i, t, f = self.items[index]

        return self._solutions_len(t) + self._solutions_len(f)

    def get_solutions(self):
        return self._get_solutions(self.get_root())

    def _get_solutions(self, index):
        result = []

        i, t, f = self.items[index]

        result.extend(self._get_solutions_in_child(i, t, True))
        result.extend(self._get_solutions_in_child(i, f, False))

        return result

    def _get_solutions_in_child(self, current_index, child_index, child_type):
        if child_index < 0:
            raise "Invalid index in T child"

        if child_index == 1:
            return [{current_index: child_type}]

        if child_index == 0:
            return []

        # now child index is greater than 1

        child_solutions = self._get_solutions(child_index)
        result = []

        for solution in child_solutions:
            solution[current_index] = child_type
            result.append(solution)

        return result
