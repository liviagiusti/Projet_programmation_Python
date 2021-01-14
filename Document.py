# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:41:48 2020

@author: Livia Giusti et Ines Kara
"""
#--------------------------------------------------------------------------------------------------
#Importation des librairies
#--------------------------------------------------------------------------------------------------

import re
import datetime as dt

#--------------------------------------------------------------------------------------------------
#Création de la classe Document
#--------------------------------------------------------------------------------------------------

class Document:
    #Constructeur
    #Dans les paramètres, il faut toujours mettre les paramètres obligatoires d'habord
    #Puis les paramètres nommés (facultatifs)
    def __init__(self, titre, texte, date, auteur="inconnu", url="inconnu"):
        self.titre = self.nettoyer_texte(titre)
        self.texte = self.nettoyer_texte(texte)
        self.auteur = auteur
        self.date = date
        self.url = url
    
    #Méthodes permettant de connaitre la valeur de chaque clé - getters
    def get_titre(self):
        return self.titre
    
    def get_texte(self):
        return self.texte
    
    def get_auteur(self):
        return self.auteur
    
    def get_date(self):
        return self.date
    
    def get_url(self):
        return self.url
    
    #Méthode qui affiche tout
    def afficher(self):
        print("Le titre du document est ",self.get_titre())
        print("L'auteur du document est ",self.get_auteur())
        print("La date du document est ",self.get_date())
        print("L'URL du document est ",self.get_url())
        print("Le texte du document est ",self.get_texte())
        
    def __repr__(self):
        return self.get_titre()+" "+self.get_texte()
    
    def __str__(self):
        return "Le document \"" + str(self.get_titre()) + "\" est un document " + str(self.get_type())
    
    def get_type(self):
        pass
    
    #Methode qui nettoie les textes 
    #Méthode exécutée sur les textes avant de les enregistrer
    def nettoyer_texte(self, texte_a_nettoyer):
        texte_nettoye = texte_a_nettoyer.lower()
        #Enleve les passages à la ligne
        expReg = re.compile("\n")
        texte_nettoye = re.sub(expReg," ", texte_nettoye)
        #Enleve les chiffres
        expReg = re.compile("\d")
        texte_nettoye = re.sub(expReg," ", texte_nettoye)
        #Enleve tout ce qui n'est pas une lettre
        expReg = re.compile("\W")
        texte_nettoye = re.sub(expReg," ", texte_nettoye)
        #Enleve les multi-espaces
        expReg = re.compile("\s+")
        texte_nettoye = re.sub(expReg," ", texte_nettoye)
        return texte_nettoye
    
#--------------------------------------------------------------------------------------------------
#Création de la classe RedditDocument qui est une classe fille de la classe Document
#--------------------------------------------------------------------------------------------------
   
class RedditDocument(Document):
    def __init__(self, titre, texte, date, auteur="inconnu", url="inconnu", commentaire=0):
        super().__init__(titre, texte, date, auteur, url)
        self.commentaire = commentaire
        self.type = "reddit"
    
    #Méthodes permettant de connaitre la valeur de chaque clé - getters
    def get_commentaire(self):
        return self.commentaire
    
    def get_type(self):
        return self.type
    
    def __str__(self):
        return Document.__str__(self) + " et il a " + str(self.get_commentaire()) + " commentaires."

#--------------------------------------------------------------------------------------------------
#Création de la classe ArvicDocument qui est une classe fille de la classe Document
#--------------------------------------------------------------------------------------------------
     
class ArvicDocument(Document):
    def __init__(self, titre, texte, date, auteur="inconnu", nb_auteurs=0, url="inconnu"):
        super().__init__(titre, texte, date, auteur, url)
        self.nb_auteurs = nb_auteurs
        self.type = "arvic"
        
    def get_nb_auteurs(self):
        return self.nb_auteurs
        
    def get_type(self):
        return self.type
    
    def __str__(self):
        s = Document.__str__(self)
        if self.get_nb_auteurs() > 0:
            return s + " et il a été écrit par " + str(self.get_nb_auteurs()) + " auteurs."
        else : 
            return s