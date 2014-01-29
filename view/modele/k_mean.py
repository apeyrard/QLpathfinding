# -*- coding: utf-8 -*-
import math, random


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


#Cluster de points
class Cluster:
    def __init__(self, points):
        self.points = points

        self.centroid = self.calculateCentroid()

    def update(self, points):
        old_centroid = self.centroid
        self.points = points
        self.centroid = self.calculateCentroid()
        return getDistance(old_centroid, self.centroid)

    def calculateCentroid(self):
        x = 0
        y = 0
        #le centroid est un point barycentre des points du cluster
        for p in self.points:
            x += p.x
            y += p.y
        x = x/len(self.points)
        y = y/len(self.points)
        return Point(x, y)

def kmeans(points, k, epsilon):
    #on génère k points aléatoires qui serviront de centroides initiaux
    initial = random.sample(points, k)
    #on génère les clusters correspondant
    clusters = [Cluster([p]) for p in initial]

    flag = True
    while flag:

        lists = [ [] for c in clusters]
        for p in points:
            #pour chaque point on trouve le centroide le plus proche
            smallest_distance = getDistance(p,clusters[0].centroid)
            index = 0
            for i in range(len(clusters[1:])):
                distance = getDistance(p, clusters[i+1].centroid)
                if distance < smallest_distance:
                    smallest_distance = distance
                    index = i+1
            #on ajoute le point a la liste du centroide le plus proche
            lists[index].append(p)

        #si les centroides se déplacent de moins de epsilon, on s'arrete
        biggest_shift = 0.0
        for i in range(len(clusters)):
            shift = clusters[i].update(lists[i])
            biggest_shift = max(biggest_shift, shift)
        if biggest_shift < epsilon:
            flag = False
    return clusters

def getDistance(a, b):
    dist = math.sqrt(pow(a.x-b.x, 2) + pow(a.y-b.y,2))
    return dist
