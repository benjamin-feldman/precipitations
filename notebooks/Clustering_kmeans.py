
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import io
import time
import os
import ast


path = 'C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/features_01012018.csv'
chemin_dossier_zip = "./precipitations/features_01_2018.zip"
#data_complète = pd.read_csv(path)
#data = data_complète.iloc[:,8:]

def chargement_données_zippées(chemin_dossier_zip):
    # Ouvrir le dossier zippé en mode lecture
    dico_données = {}       # Ce dictionnaire contiendra toutes les données de précipitations extraites.
    with zipfile.ZipFile(chemin_dossier_zip, 'r') as zip_ref:
        # Liste des noms de fichiers dans le dossier zippé
        fichiers_dans_zip = zip_ref.namelist()
        
        # Parcourir les fichiers dans le dossier zippé
        a = 0   # Nombre de fichiers contenus dans l'archive. 
        for nom_fichier in fichiers_dans_zip:
            a = a+1
            print(nom_fichier)
            # Extraire les données du fichier sans les sauvegarder dans un nouveau dossier
            with zip_ref.open(nom_fichier) as fichier:
                fichier_csv = io.TextIOWrapper(fichier, encoding='utf-8')
                dataframe = pd.read_csv(fichier_csv)
                #nom_variable = f"données_{a}"
                nom_variable = "données_" + str(a)
                dico_données[nom_variable] = dataframe
                print(dataframe)
        return(dico_données)



def clustering_KMeans(data_complète, k):
    data = data_complète.iloc[:,8:]
    kmeans = KMeans(n_clusters=k)       # Initialisation du modèle KMeans
    kmeans.fit(data)        # Entraînement du modèle
    labels = kmeans.labels_     # Obtention des labels de cluster pour chaque point de données
    print("Centers of the clusters:")       # Affichage des centres des clusters
    print(kmeans.cluster_centers_)      # Affichage des labels des clusters pour chaque point de données
    print("Labels of the clusters for each data point:")
    print(labels)
    return (labels, kmeans.cluster_centers_)
    
def occurences_clusters(data_complète, labels, k):
    coord_i_s = data_complète.iloc[:,4]
    coord_j_s = data_complète.iloc[:,5]
    coord_i_s = coord_i_s.tolist()
    coord_j_s = coord_j_s.tolist()
    tableau_proportions = [[] for _ in range(300)]      # tableau_proportions stockera, pour chaque pixel, le nombre de fois où il appartient à chaque cluster.
    for ligne in tableau_proportions:
        for _ in range(300):
            ligne.append([0]*k)
    print("L'ordinateur va devoir traiter", len(labels), "événements. Cela pourrait prendre plusieurs minutes. Merci de patienter.")
    t0 = time.time()
    for l in range(len(labels)):
        pourcentage_avancement = int(100*l/len(labels))
        #print("Le programme traite actuellement l'événement numéro", l, "sur", len(labels), end='\r')
        t = time.time()
        temps_passé = t-t0
        temps_restant = temps_passé*(len(labels)-l-1)/(l+1)
        temps_restant_min = int(temps_restant/60)
        temps_restant_sec = int(temps_restant - temps_restant_min*60)
        print("L'ordinateur a traité", pourcentage_avancement, "%","des données.", "Merci de patienter encore", temps_restant_min, "min et", temps_restant_sec, "s.", end='\r')
        coord_i = coord_i_s[l]
        coord_j = coord_j_s[l]
        cluster = labels[l]
        tableau_proportions[coord_i][coord_j][cluster-1] = tableau_proportions[coord_i][coord_j][cluster-1] + 1
    print("Construction du tableau d'occurence des clusters terminée. La machine exécute désormais l'affichage.")
    return (tableau_proportions)


dico_données = chargement_données_zippées(chemin_dossier_zip)
tableau_proportions = clustering_KMeans(dico_données["données_1"],3)
#tableau_proportions_df = pd.DataFrame(tableau_proportions)
#tableau_proportions_df.to_csv("Répartition_2_clusters_janv_2018.csv", sep=',', index=True)

    
