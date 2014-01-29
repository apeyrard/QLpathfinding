# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from Noeud import Noeud
from TroncSort import TroncSort

#Classe permettant de parser un fichier XML et de créer les noeuds et troncons du graphe
class XMLParser(object):


    def __init__(self, pathToXMLFile):
        #on charge le xml sous forme d'un element tree
        self.tree = ET.parse(pathToXMLFile)
        self.root = self.tree.getroot()
        self.setNoeuds = set()

        #pour chaque noeud
        for node in self.root:
            setTroncons = set()
            #pour chaque troncon partant de ce noeud
            for troncon in node:
                #on créé le troncon et on l'ajoute a la liste de troncons du noeud
                newTroncSort = TroncSort(troncon.attrib['nomRue'], float(troncon.attrib['vitesse']), float(troncon.attrib['longueur']), int(troncon.attrib['destination']), int(node.attrib['id']))
                setTroncons.add(newTroncSort)
            #on ajoute le noeud a la liste de noeud
            newNode = Noeud(int(node.attrib['id']), int(node.attrib['x']), int(node.attrib['y']), setTroncons)
            self.setNoeuds.add(newNode)
