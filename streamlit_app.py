import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import pandas as pd
import requests
from collections import defaultdict

# Titre
st.title("Visualitation Catalog Stelliant")

# téléchargement et mise en place du catalog
uploaded_file = st.file_uploader("Pour accéder aux visualisations, chargez le catalog en format csv.", type=["csv"])

# tant qu'il n'y a pas de fichier ça n'active pas
if uploaded_file is not None:
    # lire le fichier CSV et enlever les colonnes inutiles
    catalog = pd.read_csv(uploaded_file, sep=';', quotechar='"', encoding='utf-8-sig')
    catalog.columns = catalog.columns.str.strip()  # removes leading/trailing spaces from all column names
    catalog = catalog.drop(columns=['Sélection des filtres', "Fiche d'Informations", "Rang Occupé?"])

    # fonction pour ajouter les regions pour la carte à partir des secteurs d'interventions
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

    # utiliser la fonction sur le tableau entier
    catalog['Region'] = catalog["Secteur d'intervention /livraison"].apply(get_region)
    #montrer le tableau
    st.dataframe(catalog)

    # SECTION VISUEL DE CARTE!

    geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson"
    geo_data = requests.get(geojson_url).json()

    def build_map(categorie_filter="Toutes"):
        # (this function is unchanged)
        # Filtrer catalog
        if categorie_filter == "Toutes":
            filtered = catalog.copy()
        else:
            filtered = catalog[catalog["Catégorie"] == categorie_filter]

        # Expand regions
        rows = []
        for _, row in filtered.iterrows():
            if row["Region"] == "none":
                continue
            regions = [r.strip() for r in row["Region"].split(",")]
            for region in regions:
                rows.append({
                    "region": region,
                    "entreprise": row["Entreprise"],
                    "categorie": row["Catégorie"],
                    "etat": row["Etat"],
                })

        expanded = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["region", "entreprise", "categorie", "etat"])

        count_per_region = expanded.groupby("region").size().reset_index(name="nb_solutions") if not expanded.empty else pd.DataFrame(columns=["region", "nb_solutions"])

        popup_dict = defaultdict(list)
        for _, row in expanded.iterrows():
            popup_dict[row["region"]].append(f"<b>{row['entreprise']}</b> — {row['categorie']} ({row['etat']})")

        # construire map
        m = folium.Map(
            location=[46.5, 2.5],
            zoom_start=6,
            tiles="cartodb positron",
            max_bounds=True,
            min_zoom=5
        )
        m.fit_bounds([[41.0, -5.5], [51.5, 10.0]])

        if not count_per_region.empty:
            folium.Choropleth(
                geo_data=geo_data,
                data=count_per_region,
                columns=["region", "nb_solutions"],
                key_on="feature.properties.nom",
                fill_color="YlOrRd",
                fill_opacity=0.7,
                line_opacity=0.5,
                legend_name="Nombre de solutions",
                nan_fill_color="lightgrey"
            ).add_to(m)

        for feature in geo_data["features"]:
            nom = feature["properties"]["nom"]
            row = count_per_region[count_per_region["region"] == nom]
            nb = row["nb_solutions"].values[0] if not row.empty else 0
            details = "<br>".join(popup_dict[nom]) if nom in popup_dict else "Aucune solution"
            popup_html = f"<b>{nom}</b><br>🟢 {nb} solution(s)<br><br>{details}"

            folium.GeoJson(
                feature,
                style_function=lambda x: {"fillOpacity": 0, "color": "transparent"},
                tooltip=folium.Tooltip(nom),
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

        return m

    # inside your `if uploaded_file is not None:` block:
    categories = ["Toutes"] + sorted(catalog["Catégorie"].dropna().unique().tolist())

    categorie_filter = st.selectbox("Catégorie", options=categories)

    m = build_map(categorie_filter)
    st_folium(m, width=900, height=600)