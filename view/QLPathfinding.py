#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import wx, thread, os, Heuristiques, settings
from modele.XMLParser import XMLParser
from math import ceil
from itertools import permutations
from modele.Drone import Drone
from modele.Livraison import Livraison
from modele.k_mean import kmeans, Point
from astar import aStar, nodeSetSearchId


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        self.parser = None
        self.start = None
        self.end = None
        self.visitedNodes = set()
        self.setDrones = set()
        self.path = set()

        # verrou général
        self.lock = thread.allocate_lock()

        self.statusbar = self.CreateStatusBar()
        self.panel = wx.Panel(self, size=(900, 800))
        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", " Choose XML File to open")
        menuAStar = filemenu.Append(wx.ID_PRINT, "Launch", " Launch pathfinding")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)

        self.heurChoice = wx.Choice(self.panel, pos=(800, 100), size=(100, 30), choices=["Dijkstra", "Standard", "Relaxed"])
        self.heurChoice.Bind(wx.EVT_CHOICE, self.OnHeurChoice)

        self.volTxt = wx.TextCtrl(self.panel, pos=(780, 300), size=(150, 30))

        self.heurChoice.Bind(wx.EVT_CHOICE, self.OnHeurChoice)

        self.modeChoice = wx.Choice(self.panel, pos=(800, 200), size=(100, 30), choices=["aStar", "TSP", "Commandes"])
        self.mode = "aStar"
        self.modeChoice.Bind(wx.EVT_CHOICE, self.OnModeChoice)

        self.heuristique = Heuristiques.StandardHeur

        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.Bind(wx.EVT_MENU, self.OnLaunch, menuAStar)
        self.Fit()
        self.Center()
        self.Show(True)

    def OnHeurChoice(self, event):
        #choix de l'heuristique
        self.lock.acquire()
        if self.heurChoice.GetCurrentSelection() == 0:
            self.heuristique = Heuristiques.DijkstraHeur
        elif self.heurChoice.GetCurrentSelection() == 1:
            self.heuristique = Heuristiques.StandardHeur
        elif self.heurChoice.GetCurrentSelection() == 2:
            self.heuristique = Heuristiques.RelaxedHeur
        self.lock.release()

    def OnModeChoice(self, event):
        #choix du mode
        self.lock.acquire()
        self.start = None
        self.end = None
        self.livr = list()
        self.RAZ()
        if self.modeChoice.GetCurrentSelection() == 0:
            self.mode = "aStar"
        elif self.modeChoice.GetCurrentSelection() == 1:
            self.end = list()
            self.mode = "TSP"
        elif self.modeChoice.GetCurrentSelection() == 2:
            self.mode = "Commandes"
        self.lock.release()

    def OnPaint(self, event):
        self.lock.acquire()
        dc = wx.PaintDC(self.panel)

        if self.mode != "Commandes":

            if self.parser is not None:
                for element in self.parser.setNoeuds:
                        dc.SetPen(wx.Pen('blue', 4))
                        dc.DrawCircle(element.x, element.y, 4)
                        for arc in element.setTroncSort:
                            dc.SetPen(wx.Pen('blue', 3))
                            origine = nodeSetSearchId(self.parser, arc.origine)
                            destination = nodeSetSearchId(self.parser, arc.destination)
                            dc.DrawLine(origine.x, origine.y, destination.x, destination.y)

            if self.visitedNodes:
                for element in self.visitedNodes:
                    dc.SetPen(wx.Pen('yellow', 4))
                    dc.DrawCircle(element.x, element.y, 4)

            if self.path:
                for element in self.path:
                    dc.SetPen(wx.Pen('cyan', 4))
                    dc.DrawCircle(element.x, element.y, 4)

            if self.end is not None:
                if self.mode == "aStar":
                    dc.SetPen(wx.Pen('red', 4))
                    dc.DrawCircle(self.end.x, self.end.y, 4)
                elif self.mode == "TSP":
                    for element in self.end:
                        dc.SetPen(wx.Pen('red', 4))
                        dc.DrawCircle(element.x, element.y, 4)

            if self.start is not None:
                dc.SetPen(wx.Pen('green', 4))
                dc.DrawCircle(self.start.x, self.start.y, 4)

        else:
            if self.livr:
                dc.Clear()
                os.system('cls' if os.name == 'nt' else 'clear')
                for livraison in self.livr:
                    dc.SetPen(wx.Pen('blue', 4))
                    dc.DrawCircle(livraison.x, livraison.y, 4)
                    print('-----------------------')
                    print(livraison.idLivr)
                    print(str(livraison.x) + " ; " + str(livraison.y))
                    print(livraison.volume)
            if self.setDrones:
                for element in self.setDrones:
                    if element.idDrone == 0:
                        dc.SetPen(wx.Pen('red', 4))
                    elif element.idDrone == 1:
                        dc.SetPen(wx.Pen('green', 4))
                    elif element.idDrone == 2:
                        dc.SetPen(wx.Pen('blue', 4))
                    elif element.idDrone == 3:
                        dc.SetPen(wx.Pen('yellow', 4))
                    elif element.idDrone == 4:
                        dc.SetPen(wx.Pen('cyan', 4))
                    elif element.idDrone == 5:
                        dc.SetPen(wx.Pen('white', 4))
                    elif element.idDrone == 6:
                        dc.SetPen(wx.Pen('gray', 4))
                    elif element.idDrone == 7:
                        dc.SetPen(wx.Pen('pink', 4))
                    elif element.idDrone == 8:
                        dc.SetPen(wx.Pen('purple', 4))
                    elif element.idDrone == 9:
                        dc.SetPen(wx.Pen('brown', 4))
                    else:
                        dc.SetPen(wx.Pen('black', 4))
                    for point in element.listLivr:
                        dc.DrawCircle(point.x, point.y, 4)

        self.lock.release()

    def RAZ(self):
        self.setDrones = set()
        self.visitedNodes.clear()
        self.path.clear()
        if self.parser is not None:
            for noeud in self.parser.setNoeuds:
                noeud.parent = None
        self.Refresh()

    def OnLeftClick(self, event):
        self.RAZ()

        #en mode commande, on ajoute une livraison
        if self.mode == "Commandes":
            x, y = event.GetPositionTuple()
            try:
                newLivr = Livraison(len(self.livr), x, y, int(self.volTxt.GetValue()))
                self.livr.append(newLivr)
            except ValueError:
                errorDial = wx.MessageDialog(None, 'Incorrect value', 'Error', wx.OK | wx.ICON_ERROR)
                errorDial.ShowModal()

        #sinon, on deplace le départ au noeud le plus proche
        elif self.parser is not None:
            x, y = event.GetPositionTuple()
            dist = None
            closest = None
            for node in self.parser.setNoeuds:
                if dist is None or (x - node.x) * (x - node.x) + (y - node.y) * (y - node.y) < dist:
                    dist = (x - node.x) * (x - node.x) + (y - node.y) * (y - node.y)
                    closest = node
            self.start = closest
            self.Refresh()
        event.Skip()

    def OnRightClick(self, event):
        self.RAZ()
        if self.mode != "Commandes":
            if self.parser is not None:
                x, y = event.GetPositionTuple()
                dist = None
                closest = None
                for node in self.parser.setNoeuds:
                    if dist is None or (x - node.x) * (x - node.x) + (y - node.y) * (y - node.y) < dist:
                        dist = (x - node.x) * (x - node.x) + (y - node.y) * (y - node.y)
                        closest = node
                if self.mode == "aStar":
                    self.end = closest
                elif self.mode == "TSP":
                    if closest in self.end:
                        self.end.remove(closest)
                    else:
                        self.end.append(closest)
                self.Refresh()
        event.Skip()

    def OnExit(self, event):
        self.Close(True)

    def OnOpen(self, event):
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.xml", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.parser = XMLParser(self.dirname + '/' + self.filename)
            self.toDrawSet = self.parser.setNoeuds
            self.Refresh()
        dlg.Destroy()

    def OnLaunch(self, event):
        if self.mode == "aStar":
            self.RAZ()
            if self.parser is not None and self.start is not None and self.end is not None:
                thread.start_new_thread(aStar, (self.parser, self.start, self.end, self.heuristique, self))
                self.Refresh()

        elif self.mode == "TSP":
            if self.end:
                meilleurCout = None
                cout = 0
                it = permutations(self.end)
                for permut in it:
                    self.RAZ()
                    cout += aStar(self.parser, self.start, permut[0], self.heuristique, self)
                    for x in range(0, len(permut)):
                        for noeud in self.parser.setNoeuds:
                            noeud.parent = None
                        if permut[x] == permut[(len(permut) - 1)]:
                            cout += aStar(self.parser, permut[x], self.start, self.heuristique, self)
                        else:
                            cout += aStar(self.parser, permut[x], permut[x + 1], self.heuristique, self)
                    if meilleurCout is None or meilleurCout < cout:
                        meilleurCout = cout

        elif self.mode == "Commandes":
            volTotal = 0
            points = list()
            for livraison in self.livr:
                volTotal += livraison.volume
                points.append(Point(livraison.x, livraison.y))
            nbMinDrone = int(ceil(float(volTotal) / settings.DRONE_CAPACITY))

            ok = False
            nbRate = 0
            while(ok is False):
                self.setDrones = set()
                if nbRate >= settings.NB_ESSAI:
                    nbMinDrone += 1
                    nbRate = 0

                ok = True

                clusters = kmeans(points, nbMinDrone, settings.EPSILON)

                for i, c in enumerate(clusters):
                    listLivr = list()
                    vol = 0
                    for p in c.points:
                        for commande in self.livr:
                            if commande.x == p.x and commande.y == p.y:
                                listLivr.append(commande)
                                vol += commande.volume
                    if vol > settings.DRONE_CAPACITY:
                        nbRate += 1
                        print('trop lourd')
                        ok = False
                    self.setDrones.add(Drone(i, listLivr))

                    for drone in self.setDrones:
                        distance = 0
                        for x in range(len(drone.listLivr)):
                            if x != len(drone.listLivr) - 1:
                                distance += abs(drone.listLivr[x].x - drone.listLivr[x + 1].x) + abs(drone.listLivr[x].y - drone.listLivr[x + 1].y)
                            else:
                                distance += abs(drone.listLivr[x].x - drone.listLivr[0].x) + abs(drone.listLivr[x].y - drone.listLivr[0].y)
                        if distance > settings.DRONE_AUTONOMY:
                            print('trop long')
                            nbRate += 1
                            ok = False

            self.livr = list()
            self.Refresh()

app = wx.App(False)
frame = MyFrame(None, 'QLPathfinding')
app.MainLoop()
