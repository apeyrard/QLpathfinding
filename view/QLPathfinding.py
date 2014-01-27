#!/usr/bin/env python2.7

import wx
from modele.XMLParser import XMLParser
import thread
from time import sleep
from math import sqrt, ceil
from itertools import permutations
from modele.Drone import Drone
from modele.Livraison import Livraison
import os
from modele.k_mean import kmeans, Point

# Create a new frame class, derived from the wxPython Frame.
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        self.parser = None
        self.start = None
        self.end = None
        self.visitedNodes = set()
        self.drawLock = thread.allocate_lock()
        self.path = set()
        self.statusbar = self.CreateStatusBar()
        self.panel = wx.Panel(self, size=(900, 800))
        self.setDrones = set()
        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", " Choose XML File to open")
        menuAStar = filemenu.Append(wx.ID_PRINT, "Launch", " Launch pathfinding")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
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

        self.heuristique = self.StandardHeur

        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.Bind(wx.EVT_MENU, self.OnLaunch, menuAStar)
        self.Fit()
        self.Center()
        self.Show(True)

    def OnHeurChoice(self, event):
        self.drawLock.acquire()
        if self.heurChoice.GetCurrentSelection() == 0:
            self.heuristique = self.DijkstraHeur
        elif self.heurChoice.GetCurrentSelection() == 1:
            self.heuristique = self.StandardHeur
        elif self.heurChoice.GetCurrentSelection() == 2:
            self.heuristique = self.RelaxedHeur
        self.drawLock.release()

    def OnModeChoice(self, event):
        self.drawLock.acquire()
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
        self.drawLock.release()

    def StandardHeur(self, node, end):
        return (sqrt((end.x - node.x) ** 2 + (end.y - node.y) ** 2))

    def DijkstraHeur(self, node, end):
        return 0

    def RelaxedHeur(self, node, end):
        return (abs(end.x - node.x) + abs(end.y - node.y))

    def OnPaint(self, event):
        self.drawLock.acquire()
        dc = wx.PaintDC(self.panel)

        
        if self.mode != "Commandes":
            
            if self.parser is not None:
                for element in self.parser.setNoeuds:
                        dc.SetPen(wx.Pen('blue', 4))
                        dc.DrawCircle(element.x, element.y, 4)
                        for arc in element.setTroncSort:
                            dc.SetPen(wx.Pen('blue', 3))
                            origine = self.nodeSetSearchId(arc.origine)
                            destination = self.nodeSetSearchId(arc.destination)
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
                os.system('cls' if os.name=='nt' else 'clear')
                for i in self.livr:
                    dc.SetPen(wx.Pen('blue', 4))
                    dc.DrawCircle(i.x, i.y, 4)
                    print('-----------------------')
                    print(i.idLivr)
                    print(str(i.x) + " ; " + str(i.y))
                    print(i.volume)
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
                    else:
                        dc.SetPen(wx.Pen('black', 4))
                    for point in element.listLivr:
                        print(1)
                        dc.DrawCircle(point.x, point.y, 4)


        self.drawLock.release()

    def RAZ(self):
        self.setDrones=set()
        self.visitedNodes.clear()
        self.path.clear()
        for item in self.parser.setNoeuds:
            item.parent = None
        self.Refresh()

    def OnLaunch(self, event):
        if self.mode == "aStar":
            self.RAZ()
            if self.parser is not None and self.start is not None and self.end is not None:
                thread.start_new_thread(self.aStar, (self.parser.setNoeuds, self.start, self.end))
                self.Refresh()
        elif self.mode == "TSP":
            if self.end:
                meilleurCout = None
                cout = 0
                it = permutations(self.end)
                for item in it:
                    self.RAZ()
                    cout += self.aStar(self.parser.setNoeuds, self.start, item[0])
                    for x in range(0, len(item)):
                        for item in self.parser.setNoeuds:
                            item.parent = None
                        if item[x] == item[len(item)-1]:
                            cout += self.aStar(self.parser.setNoeuds, item[x], self.start)
                        else:
                            cout += self.aStar(self.parser.setNoeuds, item[x], item[x+1])
                    if meilleurCout is None or meilleurCout < cout:
                        meilleurCout = cout
                        actPath = self.path
        elif self.mode == "Commandes":
            volTotal = 0
            points = list()
            for item in self.livr:
                volTotal += item.volume
                points.append(Point([item.x, item.y]))
            nbMinDrone = int(ceil(float(volTotal)/50.0))
           
            ok = False
            while(ok == False):
                ok = True
                cutoff = 0.5
                
                clusters = kmeans(points, nbMinDrone, cutoff)

                for i,c in enumerate(clusters):
                    listLivr = list()
                    for p in c.points:
                        vol = 0
                        for commande in self.livr:
                            if commande.x == p.coords[0] and commande.y == p.coords[1]:
                                listLivr.append(commande)
                                vol += commande.volume
                        if vol > 50:
                            ok = False
                    self.setDrones.add(Drone(i, listLivr))
                    
                
            self.livr=list()
            self.Refresh()

    def OnLeftClick(self, event):
        self.RAZ()
        if self.mode == "Commandes":
            x, y = event.GetPositionTuple()
            newLivr = Livraison(len(self.livr),x,y,int(self.volTxt.GetValue()))
            self.livr.append(newLivr)
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
                    self.end.append(closest)
                self.Refresh()
        event.Skip()

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "Logiciel pour la visualisation des algorithmes de pathfinding du projet QL", "About QLPathfinding", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Close(True)

    def OnOpen(self, event):
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.xml", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.statusbar.SetStatusText('Parsing...')
            self.parser = XMLParser(self.dirname + '/' + self.filename)
            self.toDrawSet = self.parser.setNoeuds
            self.statusbar.SetStatusText('')
            self.Refresh()
        dlg.Destroy()

    def nodeSetSearchId(self, idNoeud):
        for element in self.parser.setNoeuds:
            if element.idNoeud == idNoeud:
                return element
        return None

    def aStar(self, graph, start, end):
        if self.mode == "aStar":
            self.drawLock.acquire()
        openSet = set()
        closedSet = set()

        g_score = {}
        f_score = {}

        g_score[start.idNoeud] = 0
        f_score[start.idNoeud] = g_score[start.idNoeud] + self.heuristique(start, end)

        def retracePath(c, cout):
            path = [c]
            while c.parent is not None:
                c = c.parent
                path.append(c)
            path.reverse()
            for item in path:
                self.path.add(item)
            if self.mode == "aStar":
                self.drawLock.release()
            self.Refresh()
            return cout

        openSet.add(start)
        while openSet:

            score = None
            for item in openSet:
                if score is None or f_score[item.idNoeud] < score:
                    current = item
                    score = f_score[item.idNoeud]

            if current == end:
                return retracePath(current, g_score[current.idNoeud])
            openSet.remove(current)
            closedSet.add(current)
            
            if self.mode == "aStar":
                self.visitedNodes.add(current)
                self.drawLock.release()
                self.Refresh()
                sleep(0.01)
                self.drawLock.acquire()
            
            for arc in current.setTroncSort:
                node = self.nodeSetSearchId(arc.destination)
                if node not in closedSet:
                    tentative_g_score = g_score[current.idNoeud] + (sqrt((node.x - current.x) ** 2 + (node.y - current.y) ** 2))
                    if node not in openSet or tentative_g_score < g_score[node.idNoeud]:
                        node.parent = current
                        g_score[node.idNoeud] = tentative_g_score
                        f_score[node.idNoeud] = g_score[node.idNoeud] + self.heuristique(node, end)
                        if node not in openSet:
                            openSet.add(node)
        if self.mode == "aStar":
            self.drawLock.release()
        return []

app = wx.App(False)
frame = MyFrame(None, 'QLPathfinding')
app.MainLoop()
