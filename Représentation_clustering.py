
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import io
import time
import os
import ast


# Petite fonction préliminaire qui convertit une chaîne de caractère représentant une liste en liste.
def str_to_list(s):
    return ast.literal_eval(s)

def affichage_répartition_clusters(tableau_proportions, color = 'gray'):
    tableau_prop = tableau_proportions.iloc[:,1:]   # On enlève la première colonne, composée des indices de localisation.
    tableau_prop_lst = tableau_prop.applymap(str_to_list)   # On transforme les chaînes de caractères en listes.
    list_of_lists = tableau_prop_lst.values.tolist()    # On convertit le dataframe en liste de listes.
    # On vérifie si toutes les listes ont la même longueur.
    if len(set(map(len, list_of_lists))) != 1:
        print("Les listes n'ont pas toutes la même longueur.")
    else:
        tableau_prop_lst = np.array(list_of_lists)  # Si tout va bien, on convertit la liste de listes en tableau numpy.
    print(tableau_prop_lst)
    shape = tableau_prop_lst.shape
    print(shape)
    k = tableau_prop_lst.shape[2]   # k représente le nombre de clusters.
    plt.figure(figsize = (10,8))
    if (k == 2):
        sums = tableau_prop_lst.sum(axis=2)
        carte_répartition = tableau_prop_lst[:,:,1] / sums      
        print(carte_répartition)
        plt.imshow(carte_répartition, cmap=color)
    elif (k == 3):
        somme = np.sum(tableau_prop_lst, axis=2, keepdims=True)
        carte_répartition = (256 * tableau_prop_lst / somme).astype(np.uint8)
        print(carte_répartition)
        plt.imshow(carte_répartition)
        plt.colorbar()
    titre = "Carte géographique de la répartition des différents clusters pour un nombre de clusters égal à " + str(k)
    plt.title(titre)
    plt.colorbar(label="Proportion d'événements dans le cluster 1")
    plt.show()
    

chemin_proportions = ".\Répartition_2_clusters_janv_2018.csv"
tableau_proportions_df = pd.read_csv(chemin_proportions)
#print(tableau_proportions_df)
affichage_répartition_clusters(tableau_proportions_df)
    
    
