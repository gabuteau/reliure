import streamlit as st
import sqlite3
import pandas as pd

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_FILE = "base_reliure.db"

def initialiser_bdd():
    """Crée la table des livres si elle n'existe pas encore."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_livres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_client TEXT NOT NULL,
            numero_train TEXT NOT NULL,
            nombre_livres_total INTEGER NOT NULL,
            numero_livre INTEGER NOT NULL,
            hauteur INTEGER,
            largeur INTEGER,
            epaisseur INTEGER,
            toile TEXT,
            couleur TEXT,
            UNIQUE(numero_train, numero_livre) ON CONFLICT REPLACE
        )
    """)
    conn.commit()
    conn.close()

def enregistrer_ou_mettre_a_jour_livre(client, train, nb_total, num_livre, hauteur, largeur, epaisseur, toile, couleur):
    """Enregistre ou met à jour les données d'un livre spécifique dans un train."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fiches_livres (
            nom_client, numero_train, nombre_livres_total, numero_livre, 
            hauteur, largeur, epaisseur, toile, couleur
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (client, train, int(nb_total), num_livre, hauteur, largeur, epaisseur, toile, couleur))
    conn.commit()
    conn.close()

def recuperer_livres_du_train(train):
    """Récupère tous les livres déjà saisis pour un train donné."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT numero_livre, hauteur, largeur, epaisseur, toile, couleur 
        FROM fiches_livres 
        WHERE numero_train = ? 
        ORDER BY numero_livre ASC
    """, (train,))
    donnees = cursor.fetchall()
    conn.close()
    return donnees

def recuperer_toutes_les_saisies():
    """Récupère l'intégralité de la base de données."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nom_client, numero_train, nombre_livres_total, numero_livre, hauteur, largeur, epaisseur, toile, couleur 
        FROM fiches_livres 
        ORDER BY numero_train ASC, numero_livre ASC
    """)
    donnees = cursor.fetchall()
    conn.close()
    return donnees

# Initialisation de la BDD
initialiser_bdd()

# --- INTERFACE DE SAISIE ---
st.set_page_config(page_title="Saisie par Numéro de Livre", layout="wide")

st.title("📚 Système de Saisie de Reliure — Par Numéro de Livre")

# Structure en deux colonnes : Saisie à gauche, Visualisation à droite
col_saisie, col_visualisation = st.columns([1, 1])

with col_saisie:
    st.header("📋 Saisie des Données")
    
    # 1. Informations Générales du Train
    st.subheader("1. Informations du Train")
    nom_client = st.text_input("Nom du client", placeholder="Ex: Bibliothèque Municipale")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        numero_train = st.text_input("N° du train", placeholder="Ex: T2026-07")
    with col_t2:
        # Reste vide par défaut, mais saisie obligatoire
        nombre_livres_total_saisie = st.text_input("Nombre total de livres dans le train", placeholder="Saisie obligatoire", value="")

    st.write("---")

    # 2. Informations Spécifiques du Livre en cours
    st.subheader("2. Caractéristiques par Livre")
    
    # Détermination de la borne maximale de livres si saisie
    max_livres = 150
    if nombre_livres_total_saisie.strip().isdigit():
        max_livres = int(nombre_livres_total_saisie.strip())
        
    numero_livre_selectionne = st.number_input(
        "N° du livre à renseigner", 
        min_value=1, 
        max_value=max_livres, 
        value=1, 
        step=1,
        help="Sélectionnez le numéro du livre que vous souhaitez remplir ou modifier."
    )
    
    # Champs techniques pour le livre sélectionné
    col_dim1, col_dim2, col_dim3 = st.columns(3)
    with col_dim1:
        hauteur = st.number_input("Hauteur (mm)", min_value=0, value=220, step=1)
    with col_dim2:
        largeur = st.number_input("Largeur (mm)", min_value=0, value=160, step=1)
    with col_dim3:
        epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=20, step=1)
        
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        toile = st.selectbox("Type de Toile", ["Buckram", "Fantaisie", "Autre"])
    with col_opt2:
        couleur = st.text_input("Couleur", placeholder="Ex: Bleu Marine")

    # Bouton d'enregistrement pour ce numéro précis
    bouton_enregistrer = st.button(f"💾 Enregistrer le livre N° {numero_livre_selectionne}")

    if bouton_enregistrer:
        # Validations obligatoires
        if nom_client.strip() == "" or numero_train.strip() == "":
            st.error("Le nom du client et le numéro de train sont obligatoires.")
        elif nombre_livres_total_saisie.strip() == "":
            st.error("Le nombre total de livres est obligatoire.")
        elif not nombre_livres_total_saisie.strip().isdigit():
            st.error("Le nombre total de livres doit être un nombre entier.")
        else:
            # Sauvegarde en BDD (écrase et remplace si le couple [train, numéro de livre] existe déjà)
            enregistrer_ou_mettre_a_jour_livre(
                nom_client.strip(), 
                numero_train.strip(), 
                nombre_livres_total_saisie.strip(), 
                numero_livre_selectionne, 
                hauteur, 
                largeur, 
                epaisseur, 
                toile, 
                couleur
            )
            st.success(f"Livre N° {numero_livre_selectionne} enregistré avec succès pour le train {numero_train.strip()} !")

with col_visualisation:
    st.header("📊 Suivi du Train en Cours")
    
    if numero_train.strip() != "":
        st.subheader(f"Livres saisis pour le train : {numero_train.strip()}")
        livres_train = recuperer_livres_du_train(numero_train.strip())
        
        if livres_train:
            df_train = pd.DataFrame(livres_train, columns=["N° Livre", "Hauteur (mm)", "Largeur (mm)", "Épaisseur (mm)", "Toile", "Couleur"])
            st.dataframe(df_train, use_container_width=True, hide_index=True)
            
            # Indicateur visuel d'avancement
            total_saisis = len(livres_train)
            if nombre_livres_total_saisie.strip().isdigit():
                total_attendu = int(nombre_livres_total_saisie.strip())
                st.progress(total_saisis / total_attendu)
                st.info(f"Avancement : {total_saisis} / {total_attendu} livres saisis pour ce train.")
        else:
            st.info("Aucun livre n'a encore été saisi pour ce train.")
    else:
        st.info("Saisissez un numéro de train à gauche pour visualiser son avancement.")

# --- HISTORIQUE GLOBAL ---
st.write("---")
st.subheader("🗃️ Base de données globale (Tous les trains)")
historique_complet = recuperer_toutes_les_saisies()

if historique_complet:
    df_global = pd.DataFrame(
        historique_complet, 
        columns=["Client", "N° Train", "Total Livres", "N° Livre", "Hauteur", "Largeur", "Épaisseur", "Toile", "Couleur"]
    )
    st.dataframe(df_global, use_container_width=True, hide_index=True)
else:
    st.info("La base de données est actuellement vide.")