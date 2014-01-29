# -*- coding: utf-8 -*-
#Classe représentant les noeuds du réseau
class Noeud(object):
    def __init__(self, idNoeud, x, y, setTroncSort):
        self.idNoeud = idNoeud
        self.x = x
        self.y = y
        self.setTroncSort = setTroncSort
	self.parent = None
