#!/usr/bin/env python2

from XMLParser import XMLParser

parserTest = XMLParser('resources/plan20x20.xml')
for element in parserTest.listNoeuds:
    for truc in element.listeTroncSort:
        print(truc.longueur)
