
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import io
import time


path = 'C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/features_01012018.csv'
chemin_dossier_zip = "./features_01_2018.zip"
#data_complète = pd.read_csv(path)
#data = data_complète.iloc[:,8:]

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
            # Lire le fichier CSV avec le module csv
            dataframe = pd.read_csv(fichier_csv)
            #nom_variable = f"données_{a}"
            nom_variable = "données_" + str(a)
            dico_données[nom_variable] = dataframe
            print(dataframe)

# Définition du nombre de clusters
k = 2
    


def clustering_KMeans(data_complète, k):
    data = data_complète.iloc[:,8:]
    kmeans = KMeans(n_clusters=k)       # Initialisation du modèle KMeans
    kmeans.fit(data)        # Entraînement du modèle
    labels = kmeans.labels_     # Obtention des labels de cluster pour chaque point de données
    print("Centers of the clusters:")       # Affichage des centres des clusters
    print(kmeans.cluster_centers_)      # Affichage des labels des clusters pour chaque point de données
    print("Labels of the clusters for each data point:")
    print(labels)
    tableau_proportions = [[] for _ in range(300)]      # tableau_proportions stockera, pour chaque pixel, le nombre de fois où il appartient à chaque cluster.
    for ligne in tableau_proportions:
        for _ in range(300):
            ligne.append([0]*k)
    print("L'ordinateur va devoir traiter", len(labels), "événements. Cela pourrait prendre plusieurs minutes. Merci de patienter")
    t0 = time.time()
    for l in range(len(labels)):
        pourcentage_avancement = int(100*l/len(labels))
        #print("Le programme traite actuellement l'événement numéro", l, "sur", len(labels), end='\r')
        t = time.time()
        temps_passé = t-t0
        temps_restant = temps_passé*(len(labels)-l-1)/(l+1)
        temps_restant_min = int(temps_restant/60)
        temps_restant_sec = int(temps_restant - temps_restant_min*60)
        print("L'ordinateur a traité", pourcentage_avancement, "%","des données. \n", "Merci de patienter encore", temps_restant_min, "min et", temps_restant_sec, "s.", end='\r')
        coord_i = data_complète.iloc[l,4]
        coord_j = data_complète.iloc[l,5]
        cluster = labels[l]
        tableau_proportions[coord_i][coord_j][cluster-1] = tableau_proportions[coord_i][coord_j][cluster-1] + 1
    print("Construction du tableau d'occurence des clusters terminée. La machine exécute désormais l'affichage.")
    return (tableau_proportions)


def affichage_répartition_clusters(tableau_proportions, color = 'gray'):
    k = len(tableau_proportions[0][0])
    #carte_répartition = np.zeros((300, 300))
    carte_répartition = [[] for _ in range(300)]
    for ligne in carte_répartition:
        for _ in range(300):
            ligne.append([])
    if (k == 2):
        for i in range (300):
            print("Le programme d'affichage traite actuellement la ligne", i+1 , "sur 300 de la carte.", end='\r')
            for j in range (300):
                carte_répartition[i][j] = 256*tableau_proportions[i][j][1]/(tableau_proportions[i][j][0] + tableau_proportions[i][j][1])
        print(carte_répartition)
        plt.imshow(carte_répartition, cmap=color)
    elif (k == 3):
        for i in range (300):
            for j in range (300):
                lst_RVB = []
                S = sum(tableau_proportions[i][j])
                for l in range (3):
                    lst_RVB.append(tableau_proportions[i][j][l]/S*256)
                carte_répartition[i][j] = lst_RVB
        print(carte_répartition)
        plt.imshow(carte_répartition)
    titre = "Carte géographique de la répartition des différents clusters pour un nombre de clusters égal à " + str(k)
    plt.title(titre)
    plt.colorbar()
    plt.show()
    

tableau_proportions = clustering_KMeans(dico_données["données_1"],2)
affichage_répartition_clusters(tableau_proportions)
    
    
