class TroncSort(object):
    def __init__(self, nom, vitesse, longueur, destination):
        self.nom = nom
        self.vitesse = vitesse
        self.longueur = longueur
        self.destination = destination
        self.cout = longueur / vitesse
