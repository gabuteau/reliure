import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def lister_tous_les_clients():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("clients").select("nom").order("nom").execute()
        return [row["nom"] for row in reponse.data]
    except Exception:
        return []

def lister_les_trains_du_client(client):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("numero_train").eq("nom_client", client).execute()
    return sorted(list(set([row["numero_train"] for row in reponse.data])), reverse=True)

def lister_les_livres_du_train(client, train):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("numero_livre").eq("nom_client", client).eq("numero_train", train).order("numero_livre").execute()
    return [row["numero_livre"] for row in reponse.data]

def recuperer_dimensions_livre(client, train, num_livre):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("largeur, hauteur").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
    if reponse.data:
        return reponse.data[0]["largeur"], reponse.data[0]["hauteur"]
    return 160, 220 # Valeurs par défaut si non trouvé

st.set_page_config(page_title="Titrage Système 3", layout="wide")
st.title("📟 Module de Composition Spécifique — Titrage Système 3")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.warning("⚠️ Créez d'abord un client pour utiliser le module de titrage.")
else:
    col_form_saisie, col_gabarit_visualisation = st.columns([1.1, 0.9])
    
    with col_form_saisie:
        st.subheader("Clé de sélection du Livre")
        c_meta1, c_meta2 = st.columns(2)
        with c_meta1:
            t3_client = st.selectbox("1. Client référent", options=liste_clients_existants)
            t3_trains = lister_les_trains_du_client(t3_client)
            t3_train_sel = st.selectbox("2. N° de train", options=["-- Choisir --"] + t3_trains)
        
        # Initialisation des variables par défaut
        t3_larg_brute = 160
        t3_haut_brute = 220
        liste_livres = []
        
        with c_meta2:
            t3_date = st.date_input("Date d'atelier", value=datetime.now())
            if t3_train_sel != "-- Choisir --":
                liste_livres = lister_les_livres_du_train(t3_client, t3_train_sel)
                t3_livre_num = st.selectbox("3. N° du livre", options=liste_livres)
                
                # Récupération automatique des vraies dimensions depuis la fiche de saisie
                if t3_livre_num:
                    t3_larg_brute, t3_haut_brute = recuperer_dimensions_livre(t3_client, t3_train_sel, t3_livre_num)
            else:
                st.info("Sélectionnez un train pour charger les livres associés.")
                t3_livre_num = None

        st.write("---")
        st.subheader("📐 Dimensions du livre (Lecture seule)")
        c_dim1, c_dim2 = st.columns(2)
        # Utilisation de disabled=True pour bloquer la modification
        with c_dim1: st.number_input("Largeur récupérée (mm)", value=int(t3_larg_brute), disabled=True)
        with c_dim2: st.number_input("Hauteur récupérée (mm)", value=int(t3_haut_brute), disabled=True)
        
        st.write("---")
        st.subheader("✍️ Composition des lignes")
        if "df_lignes_system3" not in st.session_state:
            st.session_state.df_lignes_system3 = pd.DataFrame([
                {"Hauteur (1-34)": 22, "Titrage": "TITRE EXEMPLE"},
                {"Hauteur (1-34)": 4, "Titrage": "COTE"}
            ])
            
        df_edite_lignes = st.data_editor(
            st.session_state.df_lignes_system3,
            column_config={
                "Hauteur (1-34)": st.column_config.NumberColumn("Ligne (Position)", min_value=1, max_value=34, step=1, required=True),
                "Titrage": st.column_config.TextColumn("Texte de la ligne", required=True)
            },
            num_rows="dynamic",
            use_container_width=True
        )

    with col_gabarit_visualisation:
        st.subheader("📐 Gabarit de Prévisualisation dynamique")
        
        # Calcul de la hauteur visuelle dynamique en pixels proportionnellement à la hauteur réelle
        # On définit une échelle (ex: 2.2 pixels par mm) pour que le rendu à l'écran soit fidèle
        facteur_echelle = 2.2
        hauteur_visuelle_px = int(t3_haut_brute * facteur_echelle)
        largeur_visuelle_px = int(t3_larg_brute * facteur_echelle)
        
        # Sécurité pour éviter un affichage trop immense ou trop minuscule à l'écran
        hauteur_visuelle_px = max(min(hauteur_visuelle_px, 650), 300)
        largeur_visuelle_px = max(min(largeur_visuelle_px, 300), 100)
        
        # Calcul de la hauteur de chaque ligne de repère (les 34 divisions) dans cet espace dynamique
        hauteur_par_ligne_repere = (hauteur_visuelle_px - 20) / 34

        html_gabarit = f"""
        <div style="display: flex; font-family: monospace; background-color: #f8f9fa; padding: 15px; border-radius: 5px; min-height: {hauteur_visuelle_px + 50}px;">
            <div style="display: flex; flex-direction: column-reverse; justify-content: space-between; height: {hauteur_visuelle_px}px; padding-right: 10px; border-right: 2px solid #ccc; text-align: right; width: 45px;">
        """
        for i in range(1, 35):
            html_gabarit += f'<div style="height: {hauteur_par_ligne_repere}px; font-size: 11px; color: #555; line-height: {hauteur_par_ligne_repere}px;">{i} —</div>'
            
        html_gabarit += f"""
            </div>
            <div style="position: relative; width: {largeur_visuelle_px}px; height: {hauteur_visuelle_px}px; background-color: #fdf6e2; border: 2px solid #111; margin-left: 20px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); transition: all 0.3s ease;">
                <div style="position: absolute; width: 100%; top: 0; text-align: center; font-size: 10px; font-style: italic; background: #ddd; padding: 2px 0;">H Maquette: {t3_haut_brute + 5}mm</div>
        """
        
        # Placement dynamique des lignes composées
        for _, row_data in df_edite_lignes.iterrows():
            h_pos = row_data["Hauteur (1-34)"]
            txt = row_data["Titrage"]
            if pd.notna(h_pos) and txt:
                # Calcul précis du décalage depuis le bas en fonction de la hauteur dynamique
                bottom_offset = (int(h_pos) - 1) * hauteur_par_ligne_repere + 10
                html_gabarit += f'<div style="position: absolute; bottom: {bottom_offset}px; width: 100%; text-align: center; font-weight: bold; font-size: 14px; color: #111; text-transform: uppercase;">{txt}</div>'
                
        html_gabarit += f"""
                <div style="position: absolute; width: 100%; bottom: 0; text-align: center; font-size: 10px; font-style: italic; background: #ddd; padding: 2px 0;">L Maquette: {t3_larg_brute + 5}mm</div>
            </div>
        </div>
        """
        st.components.v1.html(html_gabarit, height=hauteur_visuelle_px + 70)
