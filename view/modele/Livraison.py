# -*- coding: utf-8 -*-
#Classe représentant les livraisons
class Livraison(object):
    def __init__(self, idLivr, x, y, volume):
        self.idLivr = idLivr
        self.x = x
        self.y = y
        self.volume = volume
