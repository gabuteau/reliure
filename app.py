import streamlit as st
import sqlite3
import pandas as pd

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_FILE = "base_reliure.db"

def initialiser_bdd():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_livres (
            nom_client TEXT NOT NULL,
            numero_train TEXT NOT NULL,
            numero_livre INTEGER NOT NULL,
            -- Nature du document
            nature_doc TEXT, -- Mono ou Perio
            etat_doc TEXT,   -- Neuf ou Usage
            option_autre TEXT, -- Cuir, 1/2 cuir, 1/2 toile ou N/A
            -- Options de reprographie
            repro_scanne BOOLEAN,
            repro_report BOOLEAN,
            -- Dimensions
            hauteur INTEGER,
            largeur INTEGER,
            epaisseur INTEGER,
            ne_pas_rogner BOOLEAN,
            -- Traitements et Reliure
            traitement TEXT,
            type_reliure TEXT,
            type_couture TEXT,
            agraphes BOOLEAN,
            nombre_cahiers INTEGER,
            -- Titrage
            titrage_sens TEXT,
            lignes_sup INTEGER,
            titrage_couleur TEXT,
            police TEXT,
            -- Toile & Couleur
            type_toile TEXT,
            couleur TEXT,
            pieces_titre TEXT,
            couleur_pieces TEXT,
            hauteur_maquette INTEGER,
            PRIMARY KEY (nom_client, numero_train, numero_livre) ON CONFLICT REPLACE
        )
    """)
    conn.commit()
    conn.close()

def enregistrer_ou_mettre_a_jour_livre(donnees):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    champs = ", ".join(donnees.keys())
    placeholders = ", ".join(["?"] * len(donnees))
    valeurs = tuple(donnees.values())
    cursor.execute(f"INSERT INTO fiches_livres ({champs}) VALUES ({placeholders})", valeurs)
    conn.commit()
    conn.close()

def compter_livres_du_train(client, train):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fiches_livres WHERE nom_client = ? AND numero_train = ?", (client, train))
    total = cursor.fetchone()[0]
    conn.close()
    return total

def recuperer_livres_du_train(client, train):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT numero_livre, nature_doc, etat_doc, option_autre, hauteur, type_reliure, couleur 
        FROM fiches_livres 
        WHERE nom_client = ? AND numero_train = ? 
        ORDER BY numero_livre ASC
    """, (client, train))
    donnees = cursor.fetchall()
    conn.close()
    return donnees

initialiser_bdd()

# --- INTERFACE DE SAISIE ---
st.set_page_config(page_title="Saisie Devis + Traitements", layout="wide")
st.title("📚 Saisie de Fiche — Devis + Traitements")

col_saisie, col_visualisation = st.columns([1.2, 0.8])

with col_saisie:
    st.header("📋 Saisie de la fiche")
    
    # --- SECTION 1 : ENTÊTE (Clés de l'enregistrement) ---
    st.subheader("1. Clés d'enregistrement")
    nom_client = st.text_input("Client", placeholder="Ex: Bibliothèque de Périgueux")
    
    c1, c2 = st.columns(2)
    with c1:
        numero_train = st.text_input("N° du train", placeholder="Ex: T2026-07")
    with c2:
        numero_livre = st.number_input("N° du livre", min_value=1, value=1, step=1)

    if nom_client.strip() and numero_train.strip():
        nombre_total_actuel = compter_livres_du_train(nom_client.strip(), numero_train.strip())
        st.metric(label="Nombre de livres actuellement enregistrés dans ce train", value=nombre_total_actuel)

    # --- SECTION 2 : LOGIQUE EN CASCADE (NATURE ET ÉTAT) ---
    st.write("---")
    st.subheader("2. Nature et Finition du document")
    
    # Choix 1 : Mono ou Perio
    nature_doc = st.radio("**Sélectionnez la nature du document :**", ["Monographie (Mono)", "Périodique (Pério)"], horizontal=True)
    
    # Choix 2 : Neuf ou Usagé
    etat_doc = st.radio("**Sélectionnez l'état :**", ["Neuf", "Usagé"], horizontal=True)

    # Choix Optionnel : Autre
    st.markdown("**Option supplémentaire :**")
    cocher_autre = st.checkbox("Autre", value=False, help="Cochez pour ouvrir les options de matières spécifiques (Cuir, 1/2 cuir, 1/2 toile)")
    
    option_autre = "N/A"
    if cocher_autre:
        option_autre = st.radio("Finition spécifique (Autre) :", ["Cuir", "1/2 cuir", "1/2 toile"], horizontal=True)

    # Reprographie
    st.markdown("**Reprographie :**")
    col_scanne, col_report, _ = st.columns([1, 1, 3])
    with col_scanne: repro_scanne = st.checkbox("Scannée", value=False)
    with col_report: repro_report = st.checkbox("Report", value=False)

    # --- SECTION 3 : DIMENSIONS ---
    st.write("---")
    st.subheader("3. Désignation format")
    c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)
    with c_dim1: hauteur = st.number_input("Hauteur (mm)", min_value=0, value=220, step=1)
    with c_dim2: largeur = st.number_input("Largeur (mm)", min_value=0, value=160, step=1)
    with c_dim3: epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=20, step=1)
    with c_dim4: ne_pas_rogner = st.checkbox("Ne pas rogner", value=False)

    # --- SECTION 4 : TRAITEMENTS & RELIURE ---
    st.subheader("4. Traitements & Reliure")
    c_trt1, c_trt2, c_trt3 = st.columns(3)
    with c_trt1: traitement = st.selectbox("Traitement de structure", ["T1", "T2", "T3", "T4", "T5", "T6"])
    with c_trt2: type_reliure = st.selectbox("Type de reliure", ["Bradel", "Emboîtage", "Passure en carton"])
    with c_trt3: type_couture = st.selectbox("Type de couture", ["Cahiers machine", "Surjeté", "Cahier manuel"])

    c_cah1, c_cah2 = st.columns(2)
    with c_cah1: agraphes = st.checkbox("Présence d'agraphes", value=False)
    with c_cah2: nombre_cahiers = st.number_input("Nombre de cahiers", min_value=0, value=0, step=1)

    # --- SECTION 5 : TITRAGE & TOILE ---
    st.subheader("5. Spécifications du titrage & Toile")
    c_tit1, c_tit2, c_tit3, c_tit4 = st.columns(4)
    with c_tit1: titrage_sens = st.radio("Sens du titrage", ["Long", "Travers"], horizontal=True)
    with c_tit2: lignes_sup = st.number_input("Lignes supplémentaires (Nbre)", min_value=0, value=0, step=1)
    with c_tit3: titrage_couleur = st.selectbox("Couleur du titrage", ["OR", "Noir", "Blanc", "Autre"])
    with c_tit4: police = st.radio("Police de caractère", ["Elzévir", "Baskerville"], horizontal=True)

    c_toi1, c_toi2, c_toi3, c_toi4 = st.columns(4)
    with c_toi1: type_toile = st.selectbox("Type de toile", ["Buckram", "Fantaisie", "Autre"])
    with c_toi2: couleur = st.text_input("Couleur de la toile")
    with c_toi3: pieces_titre = st.text_input("Pièces de titre")
    with c_toi4: couleur_pieces = st.text_input("Couleur pièce de titre")

    hauteur_maquette = hauteur + 5

    # Bouton de validation
    bouton_valider = st.button(f"💾 Valider l'enregistrement [Livre N° {numero_livre}]")

    if bouton_valider:
        if nom_client.strip() == "" or numero_train.strip() == "":
            st.error("Le nom du client et le numéro de train sont obligatoires pour créer l'enregistrement.")
        else:
            donnees_fiche = {
                "nom_client": nom_client.strip(),
                "numero_train": numero_train.strip(),
                "numero_livre": numero_livre,
                "nature_doc": nature_doc,
                "etat_doc": etat_doc,
                "option_autre": option_autre,
                "repro_scanne": repro_scanne, "repro_report": repro_report,
                "hauteur": hauteur, "largeur": largeur, "epaisseur": epaisseur, "ne_pas_rogner": ne_pas_rogner,
                "traitement": traitement, "type_reliure": type_reliure, "type_couture": type_couture,
                "agraphes": agraphes, "nombre_cahiers": nombre_cahiers,
                "titrage_sens": titrage_sens, "lignes_sup": lignes_sup, "titrage_couleur": titrage_couleur, "police": police,
                "type_toile": type_toile, "couleur": couleur, "pieces_titre": pieces_titre, "couleur_pieces": couleur_pieces,
                "hauteur_maquette": hauteur_maquette
            }
            
            enregistrer_ou_mettre_a_jour_livre(donnees_fiche)
            st.success(f"Enregistrement créé/mis à jour avec succès : Livre N°{numero_livre}")
            st.rerun()

with col_visualisation:
    st.header("📊 Suivi en direct du Train")
    
    if nom_client.strip() and numero_train.strip():
        st.subheader(f"Client : {nom_client.strip()} | Train : {numero_train.strip()}")
        livres_train = recuperer_livres_du_train(nom_client.strip(), numero_train.strip())
        
        if livres_train:
            df_train = pd.DataFrame(
                livres_train, 
                columns=["N° Livre", "Nature", "État", "Option Autre", "Hauteur", "Reliure", "Couleur"]
            )
            st.dataframe(df_train, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun livre créé pour le moment pour ce couple Client/Train.")
    else:
        st.info("Renseignez un client et un numéro de train pour afficher son tableau.")