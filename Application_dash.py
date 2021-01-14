# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:41:48 2020

@author: Livia Giusti et Ines Kara

modification du fichier créé par Jiahui Wang
document récupéré sur le site : https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7
"""
#--------------------------------------------------------------------------------------------------
#Importation des librairies
#--------------------------------------------------------------------------------------------------

import dash
import dash_core_components as dcc
import dash_html_components as html

import networkx as nx
import plotly.graph_objs as go
import pickle
import pandas
from colour import Color
from networkx.algorithms import community as com

#--------------------------------------------------------------------------------------------------
#Initialisation de l'application DASH
#--------------------------------------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Transaction Network"

#--------------------------------------------------------------------------------------------------
#Importation des données du graphe
#--------------------------------------------------------------------------------------------------

EDGE0 = pickle.load(open("edges_sans_stopword.csv", 'rb'))
NODE0 = pickle.load(open("nodes_sans_stopword.csv", 'rb'))
     
#--------------------------------------------------------------------------------------------------
#Initialisation des variables globales
#--------------------------------------------------------------------------------------------------
        
NOMBRE= [min(EDGE0.loc[:,"nombre_lien"]), max(EDGE0.loc[:,"nombre_lien"])]
NOMBRE2 = [min(EDGE0.loc[:,"nombre_doc_commun"]), max(EDGE0.loc[:,"nombre_doc_commun"])]
NOMBRE3 = [min(NODE0.loc[:,"nombre_utilisation"]), max(NODE0.loc[:,"nombre_utilisation"])]
NOMBRE4 = [min(NODE0.loc[:,"nombre_doc"]), max(NODE0.loc[:,"nombre_doc"])]

ACCOUNT=""

G_PRECEDENT = ""
TRACERECODE_PRECEDENT = []
NOMBRES_PRECEDENT = ""
NOMBRE2_PRECEDENT = ""
NOMBRE3_PRECEDENT = ""
NOMBRE4_PRECEDENT = ""
SOMMETS_CENTRAUX = []
COMMUNAUTE = []

#--------------------------------------------------------------------------------------------------
#Création du graphe en fonction des filtres et de la recherche
#--------------------------------------------------------------------------------------------------

def network_graph(nombres, AccountToSearch,nombre2, nombre3, nombre4) :
    
    global G_PRECEDENT, TRACERECODE_PRECEDENT, NOMBRES_PRECEDENT, NOMBRE2_PRECEDENT, NOMBRE3_PRECEDENT, NOMBRE4_PRECEDENT, SOMMETS_CENTRAUX, COMMUNAUTE
    
    #--------------------------------------------------------------------------------------------------
    #Création du nouveau graphe en fonction des filtres uniquement si les valeurs ont changé
    #--------------------------------------------------------------------------------------------------

    if (nombres!=NOMBRES_PRECEDENT) or (nombre2!=NOMBRE2_PRECEDENT) or (nombre3!=NOMBRE3_PRECEDENT) or (nombre4!=NOMBRE4_PRECEDENT) :
    
        #--------------------------------------------------------------------------------------------------
        #Création du graphe NETWORKX (G)
        #--------------------------------------------------------------------------------------------------
    
        #Initialisation des arêtes du graphe
        edge1 = EDGE0.copy()
        edge1["weight"] = edge1.nombre_doc_commun.copy()
        
        #Initialisation des noeuds du graphe
        node1 = NODE0.copy()
        
        #Filtrage des arêtes du graphe en fonction du nombre de liens de co-occurences des mots
        liste_edge_sup = edge1.loc[(edge1["nombre_lien"]<nombres[0]) | (edge1["nombre_lien"]>nombres[1]),:].index
        if (len(liste_edge_sup)>0):
            for index in liste_edge_sup:
                edge1.drop(axis=0, index = index, inplace =True)
        
        #Filtrage des arêtes du graphes en fonction du nombre de documents des lequels les co-occurences des mots apparaissent
        liste_edge_sup = edge1.loc[(edge1["nombre_doc_commun"]<nombre2[0]) | (edge1["nombre_doc_commun"]>nombre2[1]),:].index
        if (len(liste_edge_sup)>0):
            for index in liste_edge_sup:
                edge1.drop(axis=0, index = index, inplace =True)
    
        #Filtrage des noeuds et des arêtes du graphe en fonction du nombre d'utilisation des mots dans l'ensemble du corpus
        liste_node_sup = node1.loc[(node1['nombre_utilisation']<nombre3[0]) | (node1['nombre_utilisation']>nombre3[1]),:].index
        for index in liste_node_sup :
            liste_edge_sup = edge1.loc[(edge1['mot1'] == node1['mot'][index]) | (edge1['mot2'] == node1['mot'][index]),:].index
            for index2 in liste_edge_sup : 
                edge1.drop(axis =0, index = index2, inplace = True)
            node1.drop(axis =0, index = index, inplace = True)
        
        #Filtrage des noeuds et des arêtes du grpahe en fonction du nombre de documents dans lesquel les mots apparaissent
        liste_node_sup = node1.loc[(node1['nombre_doc']<nombre4[0]) | (node1['nombre_doc']>nombre4[1]),:].index
        for index in liste_node_sup :
            liste_edge_sup = edge1.loc[(edge1['mot1'] == node1['mot'][index]) | (edge1['mot2'] == node1['mot'][index]),:].index
            for index2 in liste_edge_sup : 
                edge1.drop(axis =0, index = index2, inplace = True)
            node1.drop(axis =0, index = index, inplace = True)
    
        #Création du graphe ne contenant que les arêtes respectant tous les filtres
        G = nx.from_pandas_edgelist(edge1, 'mot1', 'mot2', ['mot1', 'mot2', 'nombre_doc_commun', 'nombre_lien','weight'])
        nx.set_node_attributes(G, node1.set_index('mot')['nombre_utilisation'].to_dict(), 'nombre_utilisation')
        nx.set_node_attributes(G, node1.set_index('mot')['nombre_doc'].to_dict(), 'nombre_doc')
        
        #Calcul des mots centraux avec le centralité de degrée et création des communautés
        taille = len(G.nodes)
        sommets_centralite_max = []
        communaute_mot = []
        
        #Initialisation de traceRecode qui va contenir tous les éléments du graphique à afficher dans l'application
        traceRecode = []
        
        if len(edge1)>0 :
            #Calcul des mots centraux avec le centralité de degrée
            centralite = nx.degree_centrality(G)
            centralite_ind = list(centralite.keys())
            centralite_val = list(centralite.values())
            maximum = max(centralite_val)
            
            for i in range(taille):
                if centralite_val[i]== maximum:
                    sommets_centralite_max.append(centralite_ind[i]) 
        
            #Création des communautés de mots
            partition = com.greedy_modularity_communities(G)
            for i in range(len(partition)):
                  communaute_mot.append(list(partition[i]))
                  
            #--------------------------------------------------------------------------------------------------
            #Création du graphique PLOTLY (traceRecode) en se basant sur le graphe NETWORKX (G)
            #--------------------------------------------------------------------------------------------------
            
            #Initialisation de la position des noeuds des éléments du graphique à partir de la position des noeueds du graphe G
            pos = nx.drawing.layout.spring_layout(G)
            
            #Ajout de l'attribut contenant les positions au point du graphe G pour pouvoir les utiliser ultérieurement
            for node in G.nodes:
                G.nodes[node]['pos'] = list(pos[node])
        
           
            #Initialisation de la liste des couleurs des arêtes : plus le nombre de doc en commun est important plus l'arête sera rouge foncé
            colors = list(Color('lightcoral').range_to(Color('darkred'), max(edge1['nombre_doc_commun'])))
            colors = ['rgb' + str(x.rgb) for x in colors]
           
            #Initialisation de la variable contenant les fenêtres d'informations 
            middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                            marker={'size': 20, 'color': 'LightSkyBlue'},
                                            opacity=0)
            
            #Création des arêtes et des étiquettes des arêtes
            for edge in G.edges:
                #Création des arêtes
                x0, y0 = G.nodes[edge[0]]['pos']
                x1, y1 = G.nodes[edge[1]]['pos']
                weight = float(G.edges[edge]['nombre_doc_commun']) * 2 
                trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                                   mode='lines',
                                   line={'width': weight},
                                   marker={'color': colors[G.edges[edge]['nombre_doc_commun']-1]},
                                   line_shape='spline',
                                   opacity=1)
                traceRecode.append(trace)
                
                #Ajout des informations concernant les arêtes
                #La fenêtre apparait seulement lorsque la souris est placée au milieu de l'arête
                hovertext = "Co-occurence entre " + str(G.edges[edge]['mot1']) + " et " + str(
                    G.edges[edge]['mot2']) + "<br>" + "Nombre de documents en commun : " + str(
                    G.edges[edge]['nombre_doc_commun']) + "<br>" + "Nombre de liens : " + str(G.edges[edge]['nombre_lien'])
                middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
                middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
                middle_hover_trace['hovertext'] += tuple([hovertext])
            
            #Ajout des arêtes au graphique
            traceRecode.append(middle_hover_trace)
            
        #Sauvegarde du graphique et du graphe pour les réutiliser tant que les filtres sont inchangés, ainsi que la liste des sommets centraux et les communautés
        TRACERECODE_PRECEDENT = traceRecode.copy()
        G_PRECEDENT = G
        SOMMETS_CENTRAUX = sommets_centralite_max
        COMMUNAUTE = communaute_mot
            
        NOMBRES_PRECEDENT = nombres
        NOMBRE2_PRECEDENT = nombre2
        NOMBRE3_PRECEDENT = nombre3
        NOMBRE4_PRECEDENT = nombre4
    else : 
        #Réuitlisation du graphique et du graphe puisque les filtres n'ont pas été modifié, ainsi que la liste des sommets centraux et les communautés
        traceRecode = TRACERECODE_PRECEDENT
        G = G_PRECEDENT
        sommets_centralite_max = SOMMETS_CENTRAUX
        communaute_mot = COMMUNAUTE
        
    #--------------------------------------------------------------------------------------------------
    #Coloration des noeuds du graphe en fonction des noeuds centraux et du mot recherché
    #--------------------------------------------------------------------------------------------------

    for node in G.nodes():
        #Ajout des informations concernant les noeuds
        x, y = G.nodes[node]['pos']
        hovertext = "Mot: " + str(node) + "<br>" + "Nombre de documents : " + str(G.nodes[node]['nombre_doc']) + "<br>" + "Nombre d'utilisations : " + str(G.nodes[node]['nombre_utilisation'])
        
        #Coloration du noeud recherché en rouge
        if node == AccountToSearch :
            node_trace = go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hovertext]), text=tuple([str(node)]), 
                                    mode='markers+text', 
                                    textposition="bottom center",
                                    hoverinfo="text", 
                                    marker={'size': 20, 'color': 'red'})
        else:
            if node in sommets_centralite_max :
                hovertext = "Mot: " + str(node) + "<br>" +"Mot central de la centralité des degrés"+"<br>"+ "Nombre de documents : " + str(G.nodes[node]['nombre_doc']) + "<br>" + "Nombre d'utilisations : " + str(G.nodes[node]['nombre_utilisation'])
                node_trace = go.Scatter(x=tuple([x]), y=tuple([y]), hovertext= tuple([hovertext]), text=tuple([str(node)]), 
                                        mode='markers+text', 
                                        textposition="bottom center",
                                        hoverinfo="text", 
                                        marker={'size': 20, 'color': 'Blue'})
            else :
                node_trace = go.Scatter(x=tuple([x]), y=tuple([y]), hovertext=tuple([hovertext]), text=tuple([str(node)]), 
                                        mode='markers+text', 
                                        textposition="bottom center",
                                        hoverinfo="text", 
                                        marker={'size': 20, 'color': 'LightSkyBlue'})
        traceRecode.append(node_trace)
    
    #--------------------------------------------------------------------------------------------------
    #Création de la figure a affiché à partir de toutes les données contenues dans traceRecode
    #--------------------------------------------------------------------------------------------------
    
    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Visualisation des co-occurence de mots du corpus', showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select'
                            )}
    return figure

#--------------------------------------------------------------------------------------------------
#Création du style CSS des composants de droite
#--------------------------------------------------------------------------------------------------
   
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#--------------------------------------------------------------------------------------------------
#Création de la page http://127.0.0.1:8050/
#--------------------------------------------------------------------------------------------------

app.layout = html.Div([
    
    #Titre
    html.Div([html.H1("Graphe des co-occurences des mots de notre corpus sur le thème du covid")],
             className="row",
             style={'textAlign': "center"}),
    
    #Création de la page
    html.Div(
        className="row",
        children=[
            
            #Création des composants affichés à gauche
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown("""
                            #### Filtres et recherche
                            """),
                    #Création du curseur filtrant les arêtes selon le nombre de liens de la co-occurence
                    dcc.Markdown("""
                            ** Co-occurences des mots  **\n
                            Nombre de liens entre deux mots
                            """),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider',
                                min=min(EDGE0.loc[:,"nombre_lien"]),
                                max=max(EDGE0.loc[:,"nombre_lien"]),
                                step=None,
                                value=[min(EDGE0.loc[:,"nombre_lien"]), max(EDGE0.loc[:,"nombre_lien"])],
                                marks={i : {'label': str(i)} for i in EDGE0['nombre_lien'].unique()}
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider')
                        ],
                        style={'height': '70px'}
                    ),
                    
                    #Création du curseur filtrant les arêtes selon le nombre de documents en commun de la co-occurence
                    dcc.Markdown("""
                            Nombre de documents en commun \n
                            (plus l'arête est rouge foncé, plus le nombre de documents en commun est important)
                            """),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider2',
                                min=min(EDGE0.loc[:,"nombre_doc_commun"]),
                                max=max(EDGE0.loc[:,"nombre_doc_commun"]),
                                step=None,
                                value=[min(EDGE0.loc[:,"nombre_doc_commun"]), max(EDGE0.loc[:,"nombre_doc_commun"])],
                                marks={i : {'label': str(i)} for i in EDGE0['nombre_doc_commun'].unique()}
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider2')
                        ],
                        style={'height': '70px'}
                    ),
                    
                    #Création du curseur filtrant les noeuds selon le nombre d'occurences du mot
                    dcc.Markdown("""
                            ** Mots du corpus  **\n
                            Nombre d'occurences du mot
                            """),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider3',
                                min=min(NODE0.loc[:,"nombre_utilisation"]),
                                max=max(NODE0.loc[:,"nombre_utilisation"]),
                                step=None,
                                value=[min(NODE0.loc[:,"nombre_utilisation"]), max(NODE0.loc[:,"nombre_utilisation"])],
                                marks={i : {'label': str(i)} for i in NODE0['nombre_utilisation'].unique()}
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider3')
                        ],
                        style={'height': '70px'}
                    ),
                    
                    #Création du curseur filtrant les noeuds selon le nombre de documents dans lesquels le mot apparait
                    dcc.Markdown("""
                            Nombre de documents dans lesquels le mot apparait
                            """),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider4',
                                min=min(NODE0.loc[:,"nombre_doc"]),
                                max= max(NODE0.loc[:,"nombre_doc"]),
                                step=None,
                                value=[min(NODE0.loc[:,"nombre_doc"]), max(NODE0.loc[:,"nombre_doc"])],
                                marks = {i : {'label': str(i)} for i in NODE0['nombre_doc'].unique()}
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider4')
                        ],
                        style={'height': '70px'}
                    ),
                    
                    #Création de la zone de recherche d'un mot
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown("""
                            Recherche d'un mot \n
                            (si le mot existe, son noeud devient rouge)
                            """),
                            dcc.Input(id="input1", type="text", placeholder="mots"),
                            html.Div(id="output")
                        ],
                        style={'height': '70px'}
                    )
                ]
            ),

            #Création du composant affichant le graphique
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=network_graph(NOMBRE, ACCOUNT, NOMBRE2, NOMBRE3, NOMBRE4))],
            ),
            
            #Création des composants affichés à droite
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown("""
                            #### Centralité et communautés
                            """),
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown("""
                            ** Les mots centraux  avec la centralité des dégrés (noeuds bleus foncés) : **
                            """),
                            html.Div(id = 'output_mot_centraux')
                            
                        ],
                        style={'height': '150px'}),

                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown("""
                            **Les communautés de mots : **
                            """),
                            html.Div(id = 'output_communaute_mots')
                        ],
                        style={'height': '400px'})
                ]
            )
        ]
    )
])

#--------------------------------------------------------------------------------------------------
#Création callback
#--------------------------------------------------------------------------------------------------

#Fonction callback exécutée à chaque modification des composants situés à gauche (filtres et recherche)
@app.callback(
    [dash.dependencies.Output('my-graph', 'figure'),dash.dependencies.Output('output_mot_centraux', 'children'),dash.dependencies.Output('output_communaute_mots', 'children')],
    [dash.dependencies.Input('my-range-slider', 'value'), dash.dependencies.Input('input1', 'value'), dash.dependencies.Input('my-range-slider2', 'value'),
     dash.dependencies.Input('my-range-slider3','value'), dash.dependencies.Input('my-range-slider4','value')])
def update_output(value,input1,value2,value3, value4):
    return network_graph(value, input1, value2, value3, value4),html.P(str(SOMMETS_CENTRAUX)),html.Div([html.P("Communauté "+str(i+1) + " : " + str(COMMUNAUTE[i]) + "\n") for i in range(len(COMMUNAUTE))])

#--------------------------------------------------------------------------------------------------
#Afficher les erreurs d'execution dans le navigateur
#--------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)