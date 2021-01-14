# Projet_programmation_Python

Ce projet est composé de deux parties : 
- La première est principalement constituée des différentes classes et méthodes codées lors des TD d'Algorithmique et programmation avancée.
- La deuxième est l'application dash (notre projet).

Pour installer les librairies nécessaires à l'exécution de nos programmes, un fichier de requirements est disponible.

Tout d'abord il faut exécuter Programme_principal.py qui utlise les fichiers Auteur.py, Collection.py et Document.py.
Cette exécution va créer 5 fichiers csv codés en binaire : corpus.csv, edges.csv, edges_sans_stopword.csv, nodes.csv et nodes_sans_stopword.csv.

Puis il faut exécuter Application_dash.py qui a besoin des fichiers edges_sans_stopword.csv et nodes_sans_stopword.csv créés par Programme_principal.py. 
Pour ouvrir l'application il faut se rendre sur la page http://127.0.0.1:8050/.
