import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "base_reliure_v2.db"

def lister_tous_les_clients():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM clients ORDER BY nom ASC")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients

def lister_les_trains_du_client(client):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT numero_train FROM fiches_livres WHERE nom_client = ? ORDER BY numero_train DESC", (client,))
    trains = [row[0] for row in cursor.fetchall()]
    conn.close()
    return trains

st.set_page_config(page_title="Titrage Système 3", layout="wide")
st.title("📟 Module de Composition Spécifique — Titrage Système 3")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.warning("⚠️ Créez d'abord un client pour utiliser le module de titrage.")
else:
    col_form_saisie, col_gabarit_visualisation = st.columns([1.1, 0.9])
    
    with col_form_saisie:
        st.subheader("Informations Saisie")
        c_meta1, c_meta2 = st.columns(2)
        with c_meta1:
            t3_client = st.selectbox("Client référent", options=liste_clients_existants)
            t3_trains = lister_les_trains_du_client(t3_client)
            t3_train_sel = st.selectbox("N° de train", options=["-- Choisir --"] + t3_trains)
        with c_meta2:
            t3_date = st.date_input("Date d'atelier", value=datetime.now())
            t3_livre_num = st.number_input("N° du livre en cours", min_value=1, value=1, step=1)
            
        st.write("---")
        c_dim1, c_dim2 = st.columns(2)
        with c_dim1: t3_larg_brute = st.number_input("Largeur d'atelier (mm)", min_value=0, value=160, step=1)
        with c_dim2: t3_haut_brute = st.number_input("Hauteur d'atelier (mm)", min_value=0, value=220, step=1)
        
        st.write("---")
        if "df_lignes_system3" not in st.session_state:
            st.session_state.df_lignes_system3 = pd.DataFrame([
                {"Hauteur (1-34)": 22, "Titrage": "Livre"},
                {"Hauteur (1-34)": 21, "Titrage": "qui"},
                {"Hauteur (1-34)": 20, "Titrage": "ce"},
                {"Hauteur (1-34)": 19, "Titrage": "construit"},
                {"Hauteur (1-34)": 4, "Titrage": "cote"},
                {"Hauteur (1-34)": 3, "Titrage": "griffe"}
            ])
            
        df_edite_lignes = st.data_editor(
            st.session_state.df_lignes_system3,
            column_config={
                "Hauteur (1-34)": st.column_config.NumberColumn("Hauteur", min_value=1, max_value=34, step=1, required=True),
                "Titrage": st.column_config.TextColumn("Texte de la ligne", required=True)
            },
            num_rows="dynamic",
            use_container_width=True
        )

    with col_gabarit_visualisation:
        st.subheader("📐 Gabarit de Prévisualisation (HTML)")
        
        # Rendu du gabarit et de la règle graduée via du HTML propre (pas de dépendance externe)
        html_gabarit = f"""
        <div style="display: flex; font-family: monospace; background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            <div style="display: flex; flex-direction: column-reverse; justify-content: space-between; height: 500px; padding-right: 10px; border-right: 2px solid #ccc; text-align: right; width: 40px;">
        """
        for i in range(1, 35):
            html_gabarit += f'<div style="height: 14.7px; font-size: 11px; color: #555;">{i} —</div>'
            
        html_gabarit += f"""
            </div>
            <div style="position: relative; width: 150px; height: 500px; background-color: #fdf6e2; border: 2px solid #111; margin-left: 20px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);">
                <div style="position: absolute; width: 100%; top: 0; text-align: center; font-size: 10px; font-style: italic; background: #ddd; padding: 2px 0;">H Maquette: {t3_haut_brute + 5}mm</div>
        """
        
        for _, row_data in df_edite_lignes.iterrows():
            h_pos = row_data["Hauteur (1-34)"]
            txt = row_data["Titrage"]
            if pd.notna(h_pos) and txt:
                # Calcul de la position depuis le bas du dos cartonné
                bottom_offset = (int(h_pos) - 1) * 14.5 + 10
                html_gabarit += f'<div style="position: absolute; bottom: {bottom_offset}px; width: 100%; text-align: center; font-weight: bold; font-size: 14px; color: #111; text-transform: uppercase;">{txt}</div>'
                
        html_gabarit += f"""
                <div style="position: absolute; width: 100%; bottom: 0; text-align: center; font-size: 10px; font-style: italic; background: #ddd; padding: 2px 0;">L Maquette: {t3_larg_brute + 5}mm</div>
            </div>
        </div>
        """
        st.components.v1.html(html_gabarit, height=540)