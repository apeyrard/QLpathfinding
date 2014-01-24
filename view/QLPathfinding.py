#!/usr/bin/env python2

import wx
from modele.XMLParser import XMLParser


# Create a new frame class, derived from the wxPython Frame.
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.visitedSet = set()
        self.toDrawSet = set()

        self.statusbar = self.CreateStatusBar()
        self.panel = wx.Panel(self, size=(800, 800))

        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", " Choose XML File to open")
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
        self.Fit()
        self.Show(True)

    def OnPaint(self, event):
        dc = wx.PaintDC(self.panel)

        for element in self.toDrawSet:
            if element not in self.visitedSet:
                dc.SetPen(wx.Pen('blue', 4))
                dc.DrawCircle(element.x, element.y, 4)
            else:
                dc.SetPen(wx.Pen('green', 4))
                dc.DrawCircle(element.x, element.y, 4)
        #dc.DrawLine(50, 20, 300, 20)
        #dc.SetPen(wx.Pen('red', 1))

        #rect = wx.Rect(50, 50, 100, 100)
        #dc.DrawRoundedRectangleRect(rect, 8)

        #dc.SetBrush(wx.Brush('yellow'))
        #x = 250
        #y = 100
        #r = 50
        #dc.DrawCircle(x, y, r)

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

app = wx.App(False)
frame = MyFrame(None, 'QLPathfinding')
app.MainLoop()
