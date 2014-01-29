# -*- coding: utf-8 -*-
from math import sqrt


def StandardHeur(node, end):
    return (sqrt((end.x - node.x) ** 2 + (end.y - node.y) ** 2))


def DijkstraHeur(node, end):
    return 0


def RelaxedHeur(node, end):
    return (abs(end.x - node.x) + abs(end.y - node.y))
