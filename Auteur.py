# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:41:48 2020

@author: Livia Giusti et Ines Kara
"""
#--------------------------------------------------------------------------------------------------
#Création de la classe Auteur
#--------------------------------------------------------------------------------------------------

class Auteur : 
    #Constructeur
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}
        
    #Méthodes permettant de connaitre la valeur de chaque clé - getters
    def get_name(self):
        return self.name
    
    def get_ndoc(self):
        return self.ndoc
    
    def get_production(self):
        return self.production
        
    #Alimentation du dictionnaire production qui contient les identifiants des documents écrits par l'auteur
    def addDocument(self, numDoc):
        self.ndoc = self.ndoc + 1
        self.production[self.ndoc] = "document "+str(numDoc)
    
    #Méthode qui affiche les informations de l'auteur
    def afficher(self):
        print("L'auteur ",self.name," a écrit ",self.ndoc," document(s) qui est(sont) ",self.production)

    #Méthode qui se déclanche lors que l'on utilise la fonction print
    def __str__(self):
        return 'L\'auteur '+str(self.name)+' a ecrit '+str(self.ndoc)+' document(s).'
    
    def __repr__(self):
        return self.get_name()