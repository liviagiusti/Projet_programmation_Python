# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:41:48 2020

@author: Livia Giusti et Ines Kara
"""
#--------------------------------------------------------------------------------------------------
#Importation des librairies
#--------------------------------------------------------------------------------------------------

import praw
import urllib
import xmltodict
import pickle
import datetime as dt

from Document import Document
from Document import RedditDocument
from Document import ArvicDocument
from Auteur import Auteur
from Collection import Corpus

#--------------------------------------------------------------------------------------------------
#Création du dictionnaire
#--------------------------------------------------------------------------------------------------

#Dictionnaire collection contenant les instances des documents
collection={}

#Dictionnaire id2doc contenant les clés id des documents et leur titre
id2doc={}

#Dictionnaire id2aut contenant les clés id auteurs et leur nom
id2aut={}

#Dictionnaire auteur contenant les instances des auteurs
authors={}

#Dictionnaire corpus contant les instances des corpus
corpus={}
        
#--------------------------------------------------------------------------------------------------
#Importation des données REDIT
#--------------------------------------------------------------------------------------------------

#Récupération des document REDIT
reddit = praw.Reddit(client_id='bWI_QQArBel7Mg', client_secret='yWNWfkj8X0oY419W446qFoqwS30', user_agent='Reddit WebScrapping')
host_post = reddit.subreddit('covid').hot(limit=5)

#Intégration des informations des documents aux différents dictionnaires
for post in host_post:
    titre = post.title
    texte = post.selftext
    texte = texte.replace("\n", " ")
    auteur = post.author
    url = post.url
    date = dt.datetime.fromtimestamp(post.created)
    commentaire = post.num_comments
    
    #Intégration du document au corpus
    i=len(collection)
    collection[i] = RedditDocument(titre, texte, date, auteur.name, url, commentaire)
    
    #Intégration des auteurs au dictionnaire authors
    auteurConnu = False
    for x in range(0,len(authors)):
        if auteur == authors[x].name:
            auteurConnu = True
            authors[x].addDocument(i)
    if auteurConnu == False :
        x=len(authors)
        authors[x]=Auteur(auteur.name)
        authors[x].addDocument(i)
        
        #Intégration du nouvel auteur au dictionnaire id2aut
        id2aut[x] = auteur.name
    #Intégration du nouveau document au dictionnaire id2doc
    id2doc[i] = titre

#--------------------------------------------------------------------------------------------------
#Importation des données ARVIC
#--------------------------------------------------------------------------------------------------

#Récupération des documents ARVIC
url = 'http://export.arxiv.org/api/query?search_query=all:covid&start=0&max_results=5'
data = urllib.request.urlopen(url).read().decode()

#text_arvic est une liste de dictionnaires ordonnés
text_arvic = xmltodict.parse(data)['feed']['entry']

#Intégration des informations des documents aux différents dictionnaires
for post_arvic in text_arvic :
    titre = post_arvic["title"]
    texte = post_arvic["summary"]
    texte = texte.replace("\n", " ")
    auteur = post_arvic["author"]
    date = dt.datetime.strptime(post_arvic['published'], '%Y-%m-%dT%H:%M:%SZ')
    url = post_arvic["id"]
    
    #Test si le type de la variable auteur est une liste
    nb_auteurs = 1
    if isinstance(auteur, list):
        nb_auteurs = len(auteur)
        auteur = auteur[0]
    auteur1 = auteur['name']
    
    #Intégration du document au corpus
    i = len(collection)
    collection[i] = ArvicDocument(titre, texte, date, auteur1, nb_auteurs, url)
          
    #Intégration des auteurs au dictionnaire authors
    liste_auteur = post_arvic["author"]
    for numaut in range(0,nb_auteurs):
        auteur = liste_auteur[numaut]
    
        auteurConnu = False
        for x in range(0,len(authors)):
            if auteur == authors[x].name:
                auteurConnu = True
                authors[x].addDocument(i)
        if auteurConnu == False :
            x=len(authors)
            authors[x]=Auteur(auteur["name"])
            authors[x].addDocument(i)
            
            #Intégration du nouvel auteur au dictionnaire id2aut
            id2aut[x] = auteur["name"]
    
    #Intégration du nouveau document au dictionnaire id2doc
    id2doc[i] = titre

#--------------------------------------------------------------------------------------------------
#Enregistrement des données dans le corpus
#--------------------------------------------------------------------------------------------------

corpus=Corpus(authors, id2aut, collection, id2doc)

#--------------------------------------------------------------------------------------------------
#Enregistrement et récupération du corpus sur le disque
#--------------------------------------------------------------------------------------------------

#Enregistrement du corpus sur le disque
corpus.enregistrer("corpus.csv")

#Récupération du corpus sur le disque
#Ouverture (en lecture) du fichier de configuration
infile = open("corpus.csv", 'rb')   
#Chargement des donnees contenues dans le fichier
corpus_recupere = pickle.load(infile)
#Fermeture du fichier
infile.close()

#--------------------------------------------------------------------------------------------------
#Analyse du contenu textuel
#--------------------------------------------------------------------------------------------------

#Affiche le corpus (titre et texte)
corpus.get_collection()

print("Nombre de fois où le mois covid apparait dans le corpus :", len(corpus.search("covid")))

#Tableau indiquant les 10 caractères avant et après les occurences de "covid"
corpus.concorde("covid", 10)
#Certaines occurences des mots ne sont pas dans le tableau : lorsque les deux occurences sont trop proches,
#et que certains caractères après une occurence font également partir des caractères avant l'occurence suivante,
#l'occurence suivante ne fait pas partir du tableau.
#Idem pour les premiers et derniers mots de la chaine unique.
#Car la fonction considère qu'il n'existe pas les 10 caractères recherchés nécessaires pour remplir le tableau.

#--------------------------------------------------------------------------------------------------
#Création, enregistrement et récupération du tableau de fréquences des mots contenus dans les titres du corpus
#--------------------------------------------------------------------------------------------------

#Fichier nodes
frequence_mot_sans_stopword = corpus.frequence_mot(stopword=False)

#Récupération de nodes sur le disque
#Ouverture (en lecture) du fichier de configuration
infile = open("nodes_sans_stopword.csv", 'rb')
#Chargement des donnees contenues dans le fichier
nodes_sans_stopword = pickle.load(infile)
#Fermeture du fichier
infile.close()

#--------------------------------------------------------------------------------------------------
#Création, enregistrement et récupération du tableau de co-occurences des mots contenus dans les titres du corpus
#--------------------------------------------------------------------------------------------------

#Fichier edges
frequence_lien_mot_sans_stopword = corpus.frequence_lien_mot(stopword=False)

#Récupération edges sur le disque
#Ouverture (en lecture) du fichier de configuration
infile = open("edges_sans_stopword.csv", 'rb')
#Chargement des donnees contenues dans le fichier
edges_sans_stopword = pickle.load(infile)
#Fermeture du fichier
infile.close()  

#--------------------------------------------------------------------------------------------------
#Méthodes de la classe Corpus
#--------------------------------------------------------------------------------------------------

#Affichage du nom du corpus
corpus.get_nom()

#Affichage du premier auteur
corpus.get_auteur(0)

#Affichage des auteurs du corpus 
corpus.get_authors()

#Affichage du dictionnaire id2aut
corpus.get_id2aut()

#Affichage du premier document
corpus.get_doc(0)

#Affichage du corpus
corpus.get_collection()

#Affichage du dictionnaire id2doc
corpus.get_id2doc()

#Affichage du nombre de documents dans le corpus
corpus.get_ndoc()

#Affichage du nombre d'auteurs du corpus
corpus.get_naut()

#Affichage de __str__
print(corpus)

#Affichage de __repr__ (titre et texte de tous les documents du corpus)
corpus

#Affichage du corpus trié selon la date
corpus.affichageTrierDate()

#Affichage du corpus trié selon le titre
corpus.affichageTrierTitre()

#Affichage de toutes les occurences du mot coronavirus 
corpus.search("coronavirus")

#Affichage des 5 caractères avant et après toutes les occurences du mot coronavirus
corpus.concorde("coronavirus", 5)

#Enregistrement du corpus sur le disque
corpus.enregistrer("corpus.csv")

#Affichage de la liste des mots du titre du premier document qui ne sont pas des stop_word
corpus.retirer_stopword(corpus.get_doc(0).get_titre())

#Affichage de la fréquence (nombre de docs et nombre d'utilisations) de tous les mots contenus dans les titres du corpus
corpus.frequence_mot(stopword=True)

#Affichage de la fréquence (nombre de docs en commun et nombre de liens) de chaque co-occurence des mots contenus dans les titres du corpus
corpus.frequence_lien_mot(stopword=True)

#--------------------------------------------------------------------------------------------------
#Méthodes de la classe Document
#--------------------------------------------------------------------------------------------------

#Affichage du titre du premier document
corpus.get_doc(0).get_titre()

#Affichage du texte du premier document
corpus.get_doc(0).get_texte()

#Affichage de l'auteur principal du premier document
corpus.get_doc(0).get_auteur()

#Affichage de la date du premier document
corpus.get_doc(0).get_date()

#Affichage de l'URL du premier document
corpus.get_doc(0).get_url()

#Affichage de toutes les informations du premier document
corpus.get_doc(0).afficher()

#Affiche de la représentation __repr__ du premier document
corpus.get_doc(0)

#Affichage de __str__ des classes filles
print(corpus.get_doc(0))
print(corpus.get_doc(5))

#Affichage du type d'un document REDIT et d'un document ARVIC
corpus.get_doc(0).get_type()
corpus.get_doc(5).get_type()

#Affichage d'une phrase après nettoyage (ne conserve que les lettres - tout est mis en minuscule)
phrase_a_nettoyer = "Voici la phrase à nettoyer : le numéro 1 est inférieur (dont le signe s'écrit <) au numéro 3."
Document.nettoyer_texte(Document,phrase_a_nettoyer)

#Affichage du nombre de commentaires d'un document REDIT
corpus.get_doc(0).get_commentaire()

#Affichage du nombre d'auteurs d'un document ARVIC
corpus.get_doc(5).get_nb_auteurs()

#--------------------------------------------------------------------------------------------------
#Méthodes de la classe Auteur
#--------------------------------------------------------------------------------------------------

#Affichage du nom du premier auteur
corpus.get_auteur(0).get_name()

#Affiche du nombre de documents écrits par le premier auteur
corpus.get_auteur(0).get_ndoc()

#Affichage du dictionnaire contenant les identifiants des textes écrits par le premier auteur
corpus.get_auteur(0).get_production()

#Affichage de toutes les informations du premier auteur
corpus.get_auteur(0).afficher()

#Affichage de __str__ du permier auteur
print(corpus.get_auteur(0))

#Affichage de la représentation __repr__ du premier auteur
corpus.get_auteur(0)
