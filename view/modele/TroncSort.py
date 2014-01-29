# -*- coding: utf-8 -*-
#Classe représentant les troncons sortant du réseau
class TroncSort(object):
    def __init__(self, nom, vitesse, longueur, destination, origine):
        self.nom = nom
        self.vitesse = vitesse
        self.longueur = longueur
        self.destination = destination
        self.cout = longueur / vitesse
        self.origine = origine
