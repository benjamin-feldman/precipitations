from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.models import Slider, ColumnDataSource, CheckboxGroup, Select, Div, ColorBar
from bokeh.embed import file_html
from bokeh.resources import INLINE
from bokeh.transform import linear_cmap
import numpy as np
import pandas as pd
import ast


# Petite fonction préliminaire

def str_to_list(s):
    return ast.literal_eval(s)


# Fonction pour mettre à jour le graphique en fonction des paramètres choisis.

def generation_plot(nombre_clusters, normalisation, rm_outliers):
    chemin_proportions = ".\Prop_clusters\Répartition_" + str(nombre_clusters) + "_clusters_06-09_" + "2018_norm=" + normalisation + "_rm_outliers=" + rm_outliers + ".csv"
    tableau_proportions_df = pd.read_csv(chemin_proportions)
    tableau_prop = tableau_proportions_df.iloc[:, 1:]
    tableau_prop_lst = tableau_prop.applymap(str_to_list)
    list_of_lists = tableau_prop_lst.values.tolist()
    if len(set(map(len, list_of_lists))) != 1:
        print("Les listes n'ont pas toutes la même longueur.")
    else:
        tableau_prop_lst = np.array(list_of_lists)
    k = tableau_prop_lst.shape[2]
    plots = []

    for l in range(k):
        carte_répartition = tableau_prop_lst[:, :, l] / tableau_prop_lst.sum(axis=2)
        p = figure(title='Répartition du cluster {}'.format(l), x_range=(0, tableau_prop_lst.shape[0]),
                   y_range=(0, tableau_prop_lst.shape[1]), width=400, height=400)
        p.image(image=[carte_répartition], x=0, y=0, dw=tableau_prop_lst.shape[0], dh=tableau_prop_lst.shape[1],
                palette="Greys256")
        p.xaxis.axis_label = 'latitude'
        p.yaxis.axis_label = 'longitude'
        plots.append(p)

    plots_row = row(*plots)  # Convertir la liste de figures en une rangée de figures
    return (plots_row)

# Création d'une fonction pour mettre à jour la figure en fonction des paramètres choisis.

def update_plot(attr, old, new):
    rm_outliers = select_rm_outliers.value
    normalisation = select_normalisation.value
    nombre_clusters = nombre_clusters_slider.value
    new_plot = generation_plot(nombre_clusters, normalisation, rm_outliers)
    layout.children[3] = new_plot
    #div.text = file_html(new_plot, INLINE, "Plot")


# Création des widgets interactifs

select_rm_outliers = Select(title="Remove outliers", options=["yes", "no"], value="yes")
select_rm_outliers.on_change('value', update_plot)
select_normalisation = Select(title="Normalisation", options=["Divmax", "Standard"], value="Divmax")
select_normalisation.on_change('value', update_plot)
nombre_clusters_slider = Slider(title="Nombre de clusters", value=5, start=2, end=7, step=1)
nombre_clusters_slider.on_change('value', update_plot)

# Créer une figure initiale avec le premier paramètre
rm_outliers_ini = select_rm_outliers.value
normalisation_ini = select_normalisation.value
nombre_clusters_ini = nombre_clusters_slider.value
initial_plot = generation_plot(nombre_clusters_ini, normalisation_ini, rm_outliers_ini)

# Convertir la figure initiale en HTML
#initial_plot_html = file_html(initial_plot, INLINE, "Plot")

# Création d'un élément div pour afficher la figure
#div = Div(text=initial_plot_html, width=400, height=300)

# Créer la mise en page
mapper = linear_cmap(field_name='values', palette='Viridis256', low=0, high=1)
color_bar = ColorBar(color_mapper=mapper['transform'], width=8, location=(0,0))
layout = column(select_rm_outliers, select_normalisation, nombre_clusters_slider, initial_plot)
#final_layout = column(
#    row(layout, color_bar),
#    sizing_mode='stretch_both'  # Ajuste la taille du layout
#)

# Ajouter la mise en page à l'application Bokeh
curdoc().add_root(layout)

