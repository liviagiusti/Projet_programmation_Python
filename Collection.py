# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:41:48 2020

@author: Livia Giusti et Ines Kara
"""
#--------------------------------------------------------------------------------------------------
#Importation des librairies
#--------------------------------------------------------------------------------------------------

import re
import pandas
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize   

#--------------------------------------------------------------------------------------------------
#Création de la classe Corpus
#--------------------------------------------------------------------------------------------------

class Corpus :
    #Constructeur
    def __init__(self, authors, id2aut, collection, id2doc, nom='corpus'):
        self.nom = nom
        self.authors = authors
        self.id2aut = id2aut
        self.collection = collection
        self.id2doc = id2doc
        self.ndoc = len(collection)
        self.naut = len(authors)
    
    #Méthodes permettant de connaitre la valeur de chaque clé - getters
    def get_nom(self):
        return self.nom
    
    def get_auteur(self, i):
        return self.authors[i]
    
    def get_authors(self):
        return self.authors
    
    def get_id2aut(self):
        return self.id2aut
    
    def get_doc(self, i):
        return self.collection[i]
    
    def get_collection(self):
        return self.collection
    
    def get_id2doc(self):
        return self.id2doc
    
    def get_ndoc(self):
        return self.ndoc
    
    def get_naut(self):
        return self.naut
        
    #Méthode qui se déclanche lors que l'on utilise la fonction print   
    def __str__(self):
        return 'Le corpus '+str(self.nom)+' contient '+str(self.ndoc)+' documents et '+str(self.naut)+' auteurs.'
    
    def __repr__(self):
        return str(self.collection)
        
    #Méthode qui affiche les éléments du corpus triés selon le titre    
    def affichageTrierTitre(self,nreturn=None):
        if nreturn is None:
            nreturn = self.ndoc
        return [self.collection[k] for k, v in sorted(self.collection.items(), key=lambda item: item[1].get_titre())][:(nreturn)]
    
    #Méthode qui affiche les éléments du corpus triés selon la date
    def affichageTrierDate(self,nreturn=None):
        if nreturn is None:
            nreturn = self.ndoc
        return [self.collection[k] for k, v in sorted(self.collection.items(), key=lambda item: item[1].get_date(), reverse=True)][:(nreturn)]
    
    #Méthode qui permet de chercher dans tous les documents le mot cible
    def search(self, mot_cible):
        if not hasattr(self, 'chaine_unique'):
            #Création d'une chaine unique contenant tous les documents
            self.chaine_unique = "".join(str(self.get_collection()))
        cherche = re.findall(mot_cible, self.chaine_unique)
        return cherche
    
    #Méthode qui permet de chercher dans tous les documents le mot cible et d'afficher les caractères avant et après
    def concorde(self, mot_cible, taille=5):
        if not hasattr(self, 'chaine_unique'):
            #Création d'une chaine unique contenant tous les documents
            self.chaine_unique = "".join(str(self.get_collection())) 
        #print(self.chaine_unique)
        chaine = ".{"+str(taille)+"}"+str(mot_cible)+".{"+str(taille)+"}"
        expReg = re.compile(chaine)
        cherche = re.findall(expReg, self.chaine_unique)
        tableau_resultat = pandas.DataFrame(columns=['contexte gauche', 'motif trouvé', 'contexte droit'])
        for i in cherche :
            gauche = ""
            for j in range(0,taille):
                gauche = gauche + i[j]
            droite = ""
            for j in range(len(i)-taille, len(i)):
                droite = droite + i[j]
            indice = len(tableau_resultat.index)
            tableau_resultat.loc[indice] = [gauche, mot_cible, droite]
        return tableau_resultat
    
    #Méthode d'enregistrement de fichier sur le disque dur
    def enregistrer(self,nomfichier,fichier=None):
        #Enregistrement du corpus
        if fichier is None:
            pickle.dump(self, open(nomfichier, "wb" ))
            print("Enregistrement du corpus sur le disque dur")
        #Enregistrement d'un autre fichier lié au corpus
        else:
            pickle.dump(fichier, open(nomfichier, "wb" ))
            print("Enregistrement du fichier", nomfichier, "sur le disque dur")
    
    #Méthode qui enlève les stop words
    def retirer_stopword(self,texte):
       #Retire tous les stop words anglais      
       text_tokens = word_tokenize(texte)
       texte_sans_stopword = [word for word in text_tokens if not word in stopwords.words()]
       return texte_sans_stopword
   
    #Méthode qui crée et enregistre la fréquence des mots du corpus
    def frequence_mot(self, stopword=True):
        #Télechargement des stopword anglais
        if (stopword==False) :
            nltk.download('punkt')
            nltk.download('stopwords')
        
        #Initialisation du Dataframe qui va contenir les fréquences de tous les mots du corpus
        frequence_mot = pandas.DataFrame(columns=['mot', 'nombre_doc', 'nombre_utilisation'])
        
        #Pour chaque document
        for i in range (0,self.ndoc) :
            if (stopword==True) :
                #Data frame contenant tous les mots du document
                titre_texte = self.get_doc(i).get_titre().split(" ")
            else : 
                titre_texte = self.retirer_stopword(self.get_doc(i).get_titre())
            
            if len(titre_texte)>0 :  
                #Suppression de l'ensemble vide présent à la fin de certains titres et de certains documents
                for v in range(0,titre_texte.count("")) :
                    titre_texte.remove("")
                
                #Dataframe contenant tous les mots du document
                frequence_mot_doc = pandas.DataFrame(titre_texte)
                frequence_mot_doc.columns = ['mot']
                #print("Nombre de mots du texte :",len(frequence_mot_doc))
                
                #Liste contenant tous les mots différents du document (sans les doublons)
                liste_mot = set(titre_texte)
                #print("Nombre de mots uniques :",len(liste_mot))
                 
                #nb_mot = 0
                #Pour chaque mot
                for m in liste_mot :
                    #print("Mot traité :",m)
                    #print("Nombre de fois où le mot est présent dans ce texte :",len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m,:]))
                    #nb_mot = nb_mot + len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m,:])
                    
                    #Si ce mot existe déjà dans frequence_mot, incrémentation de ses fréquences
                    if (len(frequence_mot.loc[frequence_mot["mot"]==m,:])!=0) : 
                        #print("le mot existe déjà")
                        frequence_mot.loc[frequence_mot["mot"]==m,"nombre_utilisation"] += len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m,:])
                        frequence_mot.loc[frequence_mot["mot"]==m,"nombre_doc"] += 1
                    #Sinon création du mot et incrémentation de ses fréquences
                    else : 
                        #print("nouveau mot")
                        frequence_mot.loc[len(frequence_mot)] = [m, 1, len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m,:])]
            #print("Nombre de mots traités :",nb_mot)
            
        #Enregistrement de frequence_mot
        if (stopword==True) :
            self.enregistrer("nodes.csv",frequence_mot)
        else :
            self.enregistrer("nodes_sans_stopword.csv",frequence_mot)
        
        return frequence_mot
    
    #Méthode qui crée et enregistre les co-occurences des mots du corpus 
    def frequence_lien_mot(self, stopword=True):
        #Télechargement des stopword anglais
        if (stopword==False) :
            nltk.download('punkt')
            
        frequence_lien_mot = pandas.DataFrame(columns=['mot1', 'mot2', 'nombre_doc_commun', 'nombre_lien'])

        #num_doc=0
        
        #Pour chaque document
        for i in range (0,self.ndoc) :
            if (stopword==True) :
                #Data frame contenant tous les mots du document
                titre_texte = self.get_doc(i).get_titre().split(" ")
            else : 
                titre_texte = self.retirer_stopword(self.get_doc(i).get_titre())
            
            if len(titre_texte)>0 :      
                #Suppression de l'ensemble vide présent à la fin de certains titres et de certains documents
                for v in range(0,titre_texte.count("")) :
                    titre_texte.remove("")
                    
                #print("document ",num_doc)
                #num_doc += 1
                
                frequence_mot_doc = pandas.DataFrame(titre_texte)
                frequence_mot_doc.columns = ['mot']
                #print("Nombre de mots du texte :",len(frequence_mot_doc))
                
                #Liste contenant tous les mots différents du document (sans les doublons)
                liste_mot = set(titre_texte)
                #print("Nombre de mots uniques :",len(liste_mot))
                 
                #Initialisation de la liste des mots 2
                liste_mot_lien = liste_mot.copy()
                    
                #Pour chaque mot
                for m in liste_mot :
                    #print("Mot traité :",m)
                    
                    #Mise à jour de la liste contenant les mots 2 du mot traité
                    liste_mot_lien.remove(m)
                    
                    #Si il existe au moins un mot 2
                    if (len(liste_mot_lien)!=0) :
                        #pour chaque mot 2 (mot en lien avec le premier mot)
                        for m2 in liste_mot_lien:
                            #Recherche si ce lien existe déjà pour l'incrémenter
                            if (len(frequence_lien_mot.loc[(frequence_lien_mot["mot1"]==m) & (frequence_lien_mot["mot2"]==m2),:])!=0) : 
                                #print('Configuration 1 --- ','mot :',m,'/ mot 2 :',m2)
                                frequence_lien_mot.loc[(frequence_lien_mot["mot1"]==m) & (frequence_lien_mot["mot2"]==m2),"nombre_doc_commun"] += 1
                                frequence_lien_mot.loc[(frequence_lien_mot["mot1"]==m) & (frequence_lien_mot["mot2"]==m2),"nombre_lien"] += (len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m,:]) * len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m2,:]))
                            elif (len(frequence_lien_mot.loc[(frequence_lien_mot["mot1"]==m2) & (frequence_lien_mot["mot2"]==m),:])!=0) : 
                                #print('Configuration 2 --- ','mot :',m2,'/ mot 2 :',m)
                                frequence_lien_mot.loc[(frequence_lien_mot["mot1"]==m2) & (frequence_lien_mot["mot2"]==m),"nombre_doc_commun"] += 1
                                frequence_lien_mot.loc[(frequence_lien_mot["mot1"]==m2) & (frequence_lien_mot["mot2"]==m),"nombre_lien"] += (len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m,:]) * len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m2,:]))
                            else :
                                #print("Nouveau lien")
                                frequence_lien_mot.loc[len(frequence_lien_mot)] = [m, m2, 1, len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m,:]) * len(frequence_mot_doc.loc[frequence_mot_doc["mot"]==m2,:])]
        
        #Enregistrement de frequence_mot
        if (stopword==True) :
            self.enregistrer("edges.csv",frequence_lien_mot)
        else :
            self.enregistrer("edges_sans_stopword.csv",frequence_lien_mot)
        
        return frequence_lien_mot  