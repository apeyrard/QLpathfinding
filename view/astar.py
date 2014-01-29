# -*- coding: utf-8 -*-
from time import sleep
from math import sqrt
import settings


def aStar(parser, start, end, heuristique, parent=None):
    if parent.lock is not None:
        parent.lock.acquire()
    openSet = set()
    closedSet = set()

    g_score = {}
    f_score = {}

    g_score[start.idNoeud] = 0
    f_score[start.idNoeud] = g_score[start.idNoeud] + heuristique(start, end)

    openSet.add(start)
    while openSet:

        score = None
        for item in openSet:
            if score is None or f_score[item.idNoeud] < score:
                current = item
                score = f_score[item.idNoeud]

        if current == end:
            return retracePath(current, g_score[current.idNoeud], parent)
        openSet.remove(current)
        closedSet.add(current)

        if parent.lock is not None:
            if parent.mode == "aStar":
                parent.visitedNodes.add(current)
                parent.lock.release()
                parent.Refresh()
                sleep(settings.DEFAULT_SLEEP_TIME)
                parent.lock.acquire()

        for arc in current.setTroncSort:
            node = nodeSetSearchId(parser, arc.destination)
            if node not in closedSet:
                tentative_g_score = g_score[current.idNoeud] + (sqrt((node.x - current.x) ** 2 + (node.y - current.y) ** 2))
                if node not in openSet or tentative_g_score < g_score[node.idNoeud]:
                    node.parent = current
                    g_score[node.idNoeud] = tentative_g_score
                    f_score[node.idNoeud] = g_score[node.idNoeud] + heuristique(node, end)
                    if node not in openSet:
                        openSet.add(node)
    if parent.lock is not None:
        parent.lock.release()
    return []


def retracePath(c, cout, parent=None):
    path = [c]
    while c.parent is not None:
        c = c.parent
        path.append(c)
    path.reverse()
    #si on a un parent, on ajoute path a parent.path et on retourne le cout
    #sinon on retourne le path
    if parent is not None:
        for item in path:
            parent.path.add(item)
        if parent.lock is not None:
            parent.lock.release()
        parent.Refresh()
        return cout
    else:
        return path


def nodeSetSearchId(parser, idNoeud):
    for element in parser.setNoeuds:
        if element.idNoeud == idNoeud:
            return element
    return None
