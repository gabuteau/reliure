import streamlit as st
import sqlite3
import os

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_FILE = "base_reliure.db"

def initialiser_bdd():
    """Crée la table dans la base de données si elle n'existe pas encore."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_fabrication (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_client TEXT NOT NULL,
            numero_train TEXT NOT NULL,
            nombre_livres INTEGER NOT NULL,
            numero_livre INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def enregistrer_fiche(client, train, nb_livres, num_livre):
    """Insère une nouvelle fiche de fabrication dans la base de données."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fiches_fabrication (nom_client, numero_train, nombre_livres, numero_livre)
        VALUES (?, ?, ?, ?)
    """, (client, train, nb_livres, num_livre))
    conn.commit()
    conn.close()

def recuperer_historique():
    """Récupère toutes les fiches enregistrées."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nom_client, numero_train, nombre_livres, numero_livre FROM fiches_fabrication ORDER BY id DESC")
    donnees = cursor.fetchall()
    conn.close()
    return donnees

# Lancement automatique de la BDD au démarrage
initialiser_bdd()

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Saisie Devis & Traitements", layout="centered")

st.title("📚 Programme de Saisie — Reliure")
st.subheader("Informations Générales")

# Formulaire de saisie
with st.form("formulaire_saisie", clear_on_submit=True):
    nom_client = st.text_input("Nom du client", placeholder="Ex: Bibliothèque Municipale")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        numero_train = st.text_input("N° du train", placeholder="Ex: T2026-07")
    with col2:
        nombre_livre = st.number_input("Nombre de livres dans le train", min_value=1, value=150, step=1)
    with col3:
        numero_livre = st.number_input("N° du livre dans le train", min_value=1, value=1, step=1)
        
    bouton_valider = st.form_submit_button("💾 Enregistrer dans la base de données")

# Action lors du clic sur le bouton
if bouton_valider:
    if nom_client.strip() == "" or numero_train.strip() == "":
        st.error("Veuillez remplir le nom du client et le numéro de train.")
    else:
        enregistrer_fiche(nom_client, numero_train, nombre_livre, numero_livre)
        st.success(f"Fiche enregistrée avec succès pour le client '{nom_client}' !")

# --- SECTION HISTORIQUE / AFFICHAGE DE LA BASE DE DONNÉES ---
st.write("---")
st.subheader("📋 Historique des saisies (Base de données)")

historique = recuperer_historique()

if historique:
    # Transformation en tableau propre
    import pandas as pd
    df = pd.DataFrame(historique, columns=["Client", "N° Train", "Total Livres", "N° Livre"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Aucune fiche enregistrée pour le moment.")