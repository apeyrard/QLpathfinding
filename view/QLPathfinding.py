#!/usr/bin/env python2

import wx
import heapq
from modele.XMLParser import XMLParser


# Create a new frame class, derived from the wxPython Frame.
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        self.parser = None
        self.start = None
        self.end = None
        self.path = None
        self.visitedNodes = set()
        self.visitedArcs = set()
        self.statusbar = self.CreateStatusBar()
        self.panel = wx.Panel(self, size=(800, 800))

        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", " Choose XML File to open")
        menuAStar = filemenu.Append(wx.ID_PRINT, "aStar", " Launch pathfinding")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.Bind(wx.EVT_MENU, self.OnLaunch, menuAStar)
        self.Fit()
        self.Show(True)

    def OnPaint(self, event):
        dc = wx.PaintDC(self.panel)

        if self.parser is not None:
            for element in self.parser.setNoeuds:
                    dc.SetPen(wx.Pen('blue', 4))
                    dc.DrawCircle(element.x, element.y, 4)
                    for arc in element.setTroncSort:
                        dc.SetPen(wx.Pen('blue', (arc.vitesse - 3) * 2))
                        origine = self.nodeSetSearchId(arc.origine)
                        destination = self.nodeSetSearchId(arc.destination)
                        dc.DrawLine(origine.x, origine.y, destination.x, destination.y)

        if self.path:
            for element in self.path:
                dc.SetPen(wx.Pen('green', 4))
                dc.DrawCircle(self.start.x, self.start.y, 4)

        if self.visitedNodes:
            for element in self.visitedNodes:
                dc.SetPen(wx.Pen('yellow', 4))
                dc.DrawCircle(element.x, element.y, 4)

        if self.visitedArcs:
            for element in self.visitedArcs:
                dc.SetPen(wx.Pen('yellow', (element.vitesse - 3) * 2))
                origine = self.nodeSetSearchId(element.origine)
                destination = self.nodeSetSearchId(element.destination)
                dc.DrawLine(origine.x, origine.y, destination.x, destination.y)

        if self.start is not None:
            dc.SetPen(wx.Pen('green', 4))
            dc.DrawCircle(self.start.x, self.start.y, 4)

        if self.end is not None:
            dc.SetPen(wx.Pen('red', 4))
            dc.DrawCircle(self.end.x, self.end.y, 4)

    def OnLaunch(self, event):
        if self.parser is not None and self.start is not None and self.end is not None:
            self.visitedNodes.clear()
            self.path = None
            self.path = self.aStar(self.parser.setNoeuds, self.start, self.end)
            self.Refresh()

    def OnLeftClick(self, event):
        if self.parser is not None:
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
        if self.parser is not None:
            x, y = event.GetPositionTuple()
            dist = None
            closest = None
            for node in self.parser.setNoeuds:
                if dist is None or (x - node.x) * (x - node.x) + (y - node.y) * (y - node.y) < dist:
                    dist = (x - node.x) * (x - node.x) + (y - node.y) * (y - node.y)
                    closest = node
            self.end = closest
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

    def aStar(self, graph, current, end):
        self.statusbar.SetStatusText('Computing...')
        openSet = set()
        openHeap = []
        closedSet = set()

        def retracePath(c):
            path = [c]
            while c.parent is not None:
                c = c.parent
                path.append(c)
            path.reverse()
            for item in path:
                self.visitedNodes.add(item)
            return path

        openSet.add(current)
        openHeap.append((0, current))
        while openSet:
            current = heapq.heappop(openHeap)[1]
            if current == end:
                self.statusbar.SetStatusText('')
                return retracePath(current)
            openSet.remove(current)
            closedSet.add(current)
            for arc in current.setTroncSort:
                node = self.nodeSetSearchId(arc.destination)
                if node not in closedSet:
                    node.H = (abs(end.x - node.x) + abs(end.y - node.y)) * 10
                    if node not in openSet:
                        openSet.add(node)
                        heapq.heappush(openHeap, (node.H, node))
                    node.parent = current
        return []

app = wx.App(False)
frame = MyFrame(None, 'QLPathfinding')
app.MainLoop()
