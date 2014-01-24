import xml.etree.ElementTree as ET
from Noeud import Noeud
from TroncSort import TroncSort


class XMLParser(object):

    def __init__(self, pathToXMLFile):
        #on charge le xml sous forme d'un element tree
        self.tree = ET.parse(pathToXMLFile)
        self.root = self.tree.getroot()
        self.listNoeuds = list()

        for node in self.root:
            listTroncons = list()
            for troncon in node:
                newTroncSort = TroncSort(troncon.attrib['nomRue'], float(troncon.attrib['vitesse']), float(troncon.attrib['longueur']), int(troncon.attrib['destination']))
                listTroncons.append(newTroncSort)
            newNode = Noeud(int(node.attrib['id']), int(node.attrib['x']), int(node.attrib['y']), listTroncons)
            self.listNoeuds.append(newNode)
