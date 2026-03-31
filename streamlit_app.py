import streamlit as st
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Titre
st.title("Visualitation Catalog Stelliant")

# téléchargement et mise en place du catalog
uploaded_file = st.file_uploader("Pour accéder aux visualisations, chargez le catalog en format csv.", type=["csv"])

if uploaded_file is not None:
    catalog = pd.read_csv(uploaded_file)
    catalog = catalog.drop(columns=['Sélection des filtres', "Fiche d'Informations", "Rang Occupé?"])

    def get_region(x):
        if x == "National":
            return "Auvergne-Rhône-Alpes, Bourgogne-Franche-Comté, Bretagne, Centre-Val de Loire, Corse, Grand Est, Hauts-de-France, Île-de-France, Normandie, Nouvelle-Aquitaine, Occitanie, Pays de la Loire, Provence-Alpes-Côte d'Azur"
        elif x == "Occitanie":
            return "Occitanie"
        elif x == "Ouest de la France":
            return "Bretagne, Pays de la Loire"
        elif x == "Île-de-France":
            return "Île-de-France"
        elif x == "Martinique":
            return "Martinique"
        else:
            return "none"

    catalog['Region'] = catalog["Secteur d'intervention /livraison"].apply(get_region)
    st.dataframe(catalog)