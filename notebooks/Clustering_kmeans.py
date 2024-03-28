
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import io
import time
import os
import ast
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


path = 'C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/features_01012018.csv'
chemin_dossier_zip = "./precipitations/features_01_2018.zip"
#data_complète = pd.read_csv(path)
#data = data_complète.iloc[:,8:]


def chargement_données_zippées(chemin_dossier_zip):
    pd.set_option('display.float_format', lambda x: '%.5f' % x)
    df = pd.read_pickle(chemin_dossier_zip)
    df['end_time_absolute'] = df['start_time_absolute'] + df['duration'] # should be removed in the future (newly generated .pkl files will already have this column)
    return(df)

def clustering_KMeans(data_complète, k):
    FEATURES = ['duration', 'max_intensity', 'mean_intensity', 'variance', 'percentage_null']
    pipeline = Pipeline([
    ('scaling', StandardScaler()),
    ('clustering', KMeans(n_clusters=k, random_state=42))  # Adjust n_clusters as needed
    ])
    data_complète['cluster'] = pipeline.fit_predict(data_complète[FEATURES])
    cluster_centers = pipeline.named_steps['clustering'].cluster_centers_
    print("Les centres des clusters sont :\n", cluster_centers)
    print (data_complète)
    return data_complète
    

def occurences_clusters(data_clusters, k):
    tableau_proportions = [[[0]*k for _ in range(300)] for _ in range(300)]
    
    # Précalculer les masques de coordonnées
    coord_i = [[i] * 300 for i in range(300)]
    coord_j = [list(range(300)) for _ in range(300)]
    
    t0 = time.time()
    for i in range(300):
        t = time.time()
        temps_restant = (t-t0)*(300-i)/(i+1)
        temps_restant_min = int(temps_restant/60)
        temps_restant_sec = int(temps_restant - temps_restant_min*60)
        print("Le programme occurences_clusters traite la ligne", i, ". Merci de patienter encore", temps_restant_min, "min", temps_restant_sec, "s.", end="\r")
        
        # Filtrer le dataframe pour les coordonnées i
        clusters_i = data_clusters[data_clusters['i'] == coord_i[i][0]]
        
        # Group by sur les colonnes 'j' et 'cluster' et compter les occurrences
        counts = clusters_i.groupby(['j', 'cluster']).size().unstack(fill_value=0)
        
        # Remplir le tableau_proportions
        for j in range(300):
            if j in counts.index:
                tableau_proportions[i][j] = counts.loc[j].tolist()
    
    print("Construction du tableau d'occurrence des clusters terminée. La machine exécute désormais l'affichage.")
    return tableau_proportions
        


#mois = "09"
#année = "2018"
#k = 2
#chemin_dossier_zip = "C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/" + année + "_" + mois + ".zip"
#data = chargement_données_zippées(chemin_dossier_zip)
#data_clusters = clustering_KMeans(data, k)
#tableau_proportions = occurences_clusters(data_clusters, k)
#tableau_proportions_df = pd.DataFrame(tableau_proportions)
#nom_fichier = "Répartition_" + str(k) + "_clusters_" + mois + "_" + année + ".csv"
#tableau_proportions_df.to_csv(nom_fichier, sep=',', index=True)
#print ("Terminé !")

année = "2018"
k = 4
chemin_dossier_zip_1 = "C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/" + année + "_06.zip"
data_1 = chargement_données_zippées(chemin_dossier_zip_1)
chemin_dossier_zip_2 = "C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/" + année + "_07.zip"
data_2 = chargement_données_zippées(chemin_dossier_zip_2)
chemin_dossier_zip_3 = "C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/" + année + "_08.zip"
data_3 = chargement_données_zippées(chemin_dossier_zip_3)
chemin_dossier_zip_4 = "C:/Users/Trist/Documents/Cours 2A - CS/Semestre 8/Projet S8/" + année + "_09.zip"
data_4 = chargement_données_zippées(chemin_dossier_zip_4)
data = pd.concat([data_1, data_2, data_3, data_4])
data_clusters = clustering_KMeans(data, k)
tableau_proportions = occurences_clusters(data_clusters, k)
tableau_proportions_df = pd.DataFrame(tableau_proportions)
nom_fichier = "Répartition_" + str(k) + "_clusters_06-09_" + année + ".csv"
tableau_proportions_df.to_csv(nom_fichier, sep=',', index=True)
print ("Terminé !")


    
