import streamlit as st
import sqlite3
import pandas as pd

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_FILE = "base_reliure.db"

def initialiser_bdd():
    """Crée la table avec tous les champs de la fiche 'Devis + Traitements'."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_livres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_client TEXT NOT NULL,
            numero_train TEXT NOT NULL,
            nombre_livres_total INTEGER NOT NULL,
            numero_livre INTEGER NOT NULL,
            -- État & Type de document
            etat_doc TEXT, -- Perio, Mono, Neuf, Usagé
            matiere_autre TEXT, -- Cuir, Demi-cuir, Demi-Toile
            -- Options de reprographie
            repro TEXT, -- Scannée, Report
            -- Dimensions
            hauteur INTEGER,
            largeur INTEGER,
            epaisseur INTEGER,
            ne_pas_rogner BOOLEAN,
            -- Traitements et Reliure
            traitement TEXT, -- T1 à T6
            type_reliure TEXT, -- Bradel, Emboîtage, Passure en carton
            type_couture TEXT, -- Surjeté, Cahiers machine, Cahier manuel
            agraphes BOOLEAN,
            nombre_cahiers INTEGER,
            -- Titrage
            titrage_sens TEXT, -- Long, Travers
            lignes_sup INTEGER,
            titrage_couleur TEXT, -- Or, Noir, Blanc, Autre
            police TEXT, -- Elzévir, Baskerville
            -- Toile & Couleur
            type_toile TEXT, -- Buck, Fantas, Autre
            couleur TEXT,
            -- Pièces de titre
            pieces_titre TEXT,
            couleur_pieces TEXT,
            hauteur_maquette INTEGER,
            UNIQUE(numero_train, numero_livre) ON CONFLICT REPLACE
        )
    """)
    conn.commit()
    conn.close()

def enregistrer_ou_mettre_a_jour_livre(donnees):
    """Enregistre ou met à jour un livre avec toutes ses spécifications."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    champs = ", ".join(donnees.keys())
    placeholders = ", ".join(["?"] * len(donnees))
    valeurs = tuple(donnees.values())
    
    cursor.execute(f"""
        INSERT INTO fiches_livres ({champs})
        VALUES ({placeholders})
    """, valeurs)
    conn.commit()
    conn.close()

def recuperer_livres_du_train(train):
    """Récupère la liste simplifiée des livres saisis pour un train."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT numero_livre, hauteur, largeur, epaisseur, type_reliure, type_toile, couleur 
        FROM fiches_livres 
        WHERE numero_train = ? 
        ORDER BY numero_livre ASC
    """, (train,))
    donnees = cursor.fetchall()
    conn.close()
    return donnees

# Initialisation de la base de données
initialiser_bdd()

# --- INTERFACE DE SAISIE ---
st.set_page_config(page_title="Saisie Devis + Traitements", layout="wide")

st.title("📚 Saisie de Fiche — Devis + Traitements")

# Deux colonnes principales
col_saisie, col_visualisation = st.columns([1.2, 0.8])

with col_saisie:
    st.header("📋 Saisie de la fiche")
    
    # --- SECTION 1 : ENTÊTE ---
    st.subheader("1. Entête")
    nom_client = st.text_input("Client", placeholder="Ex: Bibliothèque de Périgueux")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        numero_train = st.text_input("N° du train", placeholder="Ex: T2026-07")
    with c2:
        nombre_total_saisie = st.text_input("Nombre de livres dans le train", placeholder="Saisie obligatoire")
    with c3:
        # Détermination de la borne maximale de livres
        max_livres = 150
        if nombre_total_saisie.strip().isdigit():
            max_livres = int(nombre_total_saisie.strip())
        numero_livre = st.number_input("N° du livre", min_value=1, max_value=max_livres, value=1, step=1)

    # --- SECTION 2 : ÉTAT & MATIÈRE ---
    st.subheader("2. État du document & Matières")
    c_etat1, c_etat2 = st.columns(2)
    with c_etat1:
        etat_doc = st.radio("Type", ["Perio", "Mono", "Neuf", "Usagé", "Autre"], index=2, horizontal=True)
    with c_etat2:
        repro = st.radio("Reprographie", ["Aucun", "Scannée", "Report"], index=0, horizontal=True)
        
    matiere_autre = "N/A"
    if etat_doc == "Autre":
        matiere_autre = st.radio("Finition cuir / toile", ["Cuir", "Demi-cuir", "Demi-Toile"], horizontal=True)

    # --- SECTION 3 : DIMENSIONS ---
    st.subheader("3. Désignation format")
    c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)
    with c_dim1:
        hauteur = st.number_input("Hauteur (mm)", min_value=0, value=220, step=1)
    with c_dim2:
        largeur = st.number_input("Largeur (mm)", min_value=0, value=160, step=1)
    with c_dim3:
        epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=20, step=1)
    with c_dim4:
        ne_pas_rogner = st.checkbox("Ne pas rogner", value=False)

    # --- SECTION 4 : TRAITEMENTS, RELIURE & COUTURE ---
    st.subheader("4. Traitements & Reliure")
    c_trt1, c_trt2, c_trt3 = st.columns(3)
    with c_trt1:
        traitement = st.selectbox("Traitement de structure", ["T1", "T2", "T3", "T4", "T5", "T6"])
    with c_trt2:
        type_reliure = st.selectbox("Type de reliure", ["Bradel", "Emboîtage", "Passure en carton"])
    with c_trt3:
        type_couture = st.selectbox("Type de couture", ["Cahiers machine", "Surjeté", "Cahier manuel"])

    c_cah1, c_cah2 = st.columns(2)
    with c_cah1:
        agraphes = st.checkbox("Présence d'agraphes", value=False)
    with c_cah2:
        nombre_cahiers = st.number_input("Nombre de cahiers", min_value=0, value=0, step=1)

    # --- SECTION 5 : TITRAGE & TOILE ---
    st.subheader("5. Spécifications du titrage & Toile")
    c_tit1, c_tit2, c_tit3, c_tit4 = st.columns(4)
    with c_tit1:
        titrage_sens = st.radio("Sens du titrage", ["Long", "Travers"], horizontal=True)
    with c_tit2:
        lignes_sup = st.number_input("Lignes supplémentaires (Nbre)", min_value=0, value=0, step=1)
    with c_tit3:
        titrage_couleur = st.selectbox("Couleur du titrage", ["OR", "Noir", "Blanc", "Autre"])
    with c_tit4:
        police = st.radio("Police de caractère", ["Elzévir", "Baskerville"], horizontal=True)

    c_toi1, c_toi2, c_toi3, c_toi4 = st.columns(4)
    with c_toi1:
        type_toile = st.selectbox("Type de toile", ["Buckram", "Fantaisie", "Autre"])
    with c_toi2:
        couleur = st.text_input("Couleur de la toile", placeholder="Ex: Vert d'eau")
    with c_toi3:
        pieces_titre = st.text_input("Pièces de titre", placeholder="Ex: Dos cuir")
    with c_toi4:
        couleur_pieces = st.text_input("Couleur pièce de titre", placeholder="Ex: Rouge")

    # Calcul automatique de la hauteur de la maquette (H + 5 mm)
    hauteur_maquette = hauteur + 5
    st.info(f"📏 **Hauteur de maquette calculée** : {hauteur_maquette} mm (Hauteur réelle {hauteur} mm + 5 mm)")

    # Bouton de validation
    bouton_valider = st.button(f"💾 Enregistrer le livre N° {numero_livre}")

    if bouton_valider:
        # Contrôles de validation
        if nom_client.strip() == "" or numero_train.strip() == "":
            st.error("Le nom du client et le numéro de train sont obligatoires.")
        elif nombre_total_saisie.strip() == "":
            st.error("Le nombre total de livres est obligatoire.")
        elif not nombre_total_saisie.strip().isdigit():
            st.error("Le nombre total de livres doit être un nombre entier.")
        else:
            # Construction du dictionnaire de données pour l'enregistrement
            donnees_fiche = {
                "nom_client": nom_client.strip(),
                "numero_train": numero_train.strip(),
                "nombre_livres_total": int(nombre_total_saisie.strip()),
                "numero_livre": numero_livre,
                "etat_doc": etat_doc,
                "matiere_autre": matiere_autre,
                "repro": repro,
                "hauteur": hauteur,
                "largeur": largeur,
                "epaisseur": epaisseur,
                "ne_pas_rogner": ne_pas_rogner,
                "traitement": traitement,
                "type_reliure": type_reliure,
                "type_couture": type_couture,
                "agraphes": agraphes,
                "nombre_cahiers": nombre_cahiers,
                "titrage_sens": titrage_sens,
                "lignes_sup": lignes_sup,
                "titrage_couleur": titrage_couleur,
                "police": police,
                "type_toile": type_toile,
                "couleur": couleur,
                "pieces_titre": pieces_titre,
                "couleur_pieces": couleur_pieces,
                "hauteur_maquette": hauteur_maquette
            }
            
            enregistrer_ou_mettre_a_jour_livre(donnees_fiche)
            st.success(f"Livre N° {numero_livre} enregistré avec succès pour le train {numero_train.strip()} !")

with col_visualisation:
    st.header("📊 Suivi du train")
    
    if numero_train.strip() != "":
        st.subheader(f"Train en cours : {numero_train.strip()}")
        livres_train = recuperer_livres_du_train(numero_train.strip())
        
        if livres_train:
            df_train = pd.DataFrame(
                livres_train, 
                columns=["N° Livre", "Hauteur", "Largeur", "Épaisseur", "Reliure", "Toile", "Couleur"]
            )
            st.dataframe(df_train, use_container_width=True, hide_index=True)
            
            # Indicateur d'avancement
            total_saisis = len(livres_train)
            if nombre_total_saisie.strip().isdigit():
                total_attendu = int(nombre_total_saisie.strip())
                avancement = total_saisis / total_attendu
                st.progress(avancement)
                st.info(f"Avancement : {total_saisis} / {total_attendu} livres saisis.")
        else:
            st.info("Aucun livre n'a encore été saisi pour ce train.")
    else:
        st.info("Saisissez un numéro de train à gauche pour visualiser les volumes associés.")