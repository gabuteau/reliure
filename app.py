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
            nature_doc TEXT,
            etat_doc TEXT,
            option_autre TEXT,
            repro_scanne BOOLEAN,
            repro_report BOOLEAN,
            hauteur INTEGER,
            largeur INTEGER,
            epaisseur INTEGER,
            ne_pas_rogner BOOLEAN,
            traitement TEXT,
            type_reliure TEXT,
            type_couture TEXT,
            agraphes BOOLEAN,
            nombre_cahiers INTEGER,
            -- Titrage principal
            sans_titrage BOOLEAN,
            titrage_sens TEXT,
            lignes_sup INTEGER,
            titrage_couleur TEXT,
            police TEXT,
            -- Habillage
            type_toile TEXT,
            couleur TEXT,
            -- Option Pièce de titre (Après Habillage)
            cocher_piece_titre BOOLEAN,
            couleur_pieces_toile TEXT,
            marquage_pieces TEXT,
            hauteur_maquette INTEGER,
            supplement_1 TEXT,
            supplement_2 TEXT,
            supplement_3 TEXT,
            supplement_4 TEXT,
            PRIMARY KEY (nom_client, numero_train, numero_livre) ON CONFLICT REPLACE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS couleurs_toile (
            nom_couleur TEXT PRIMARY KEY
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
        SELECT numero_livre, nature_doc, etat_doc, hauteur, type_reliure, couleur,
               CASE WHEN cocher_piece_titre THEN 'Oui (' || couleur_pieces_toile || ')' ELSE 'Non' END as piece_titre
        FROM fiches_livres 
        WHERE nom_client = ? AND numero_train = ? 
        ORDER BY numero_livre ASC
    """, (client, train))
    donnees = cursor.fetchall()
    conn.close()
    return donnees

def ajouter_couleur_bdd(nouvelle_couleur):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO couleurs_toile (nom_couleur) VALUES (?)", (nouvelle_couleur,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def charger_couleurs():
    couleurs_base = ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nom_couleur FROM couleurs_toile ORDER BY nom_couleur ASC")
    couleurs_perso = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sorted(list(set(couleurs_base + couleurs_perso)))

initialiser_bdd()

# --- INTERFACE DE SAISIE ---
st.set_page_config(page_title="Saisie Devis + Traitements", layout="wide")
st.title("📚 Saisie de Fiche — Devis + Traitements")

col_saisie, col_visualisation = st.columns([1.2, 0.8])
liste_couleurs = charger_couleurs()

with col_saisie:
    st.header("📋 Saisie de la fiche")
    
    # --- SECTION 1 : ENTÊTE ---
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

    # --- SECTION 2 : NATURE ET ÉTAT ---
    st.write("---")
    st.subheader("2. Nature et Finition du document")
    nature_doc = st.radio("**Sélectionnez la nature du document :**", ["Monographie (Mono)", "Périodique (Pério)"], horizontal=True)
    etat_doc = st.radio("**Sélectionnez l'état :**", ["Neuf", "Usagé"], horizontal=True)

    cocher_autre = st.checkbox("Autre (Matières spécifiques)")
    option_autre = "N/A"
    if cocher_autre:
        option_autre = st.radio("Finition spécifique :", ["Cuir", "1/2 cuir", "1/2 toile"], horizontal=True)

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

    # --- SECTION 5 : TITRAGE ---
    st.write("---")
    st.subheader("5. Spécifications du titrage")
    sans_titrage = st.checkbox("**Pas de titrage (Masquer la saisie)**", value=False)

    titrage_sens = "N/A"
    lignes_sup = 0
    titrage_couleur = "N/A"
    police = "N/A"

    if not sans_titrage:
        c_tit1, c_tit2, c_tit3, c_tit4 = st.columns(4)
        with c_tit1: titrage_sens = st.radio("Sens du titrage", ["Long", "Travers"], horizontal=True)
        with c_tit2: lignes_sup = st.number_input("Lignes supplémentaires (Nbre)", min_value=0, value=0, step=1)
        with c_tit3: titrage_couleur = st.selectbox("Couleur du marquage (Caractères)", ["OR", "Noir", "Blanc", "Autre"])
        with c_tit4: police = st.radio("Police de caractère", ["Elzévir", "Baskerville"], horizontal=True)

    # --- SECTION 6 : HABILLAGE ---
    st.write("---")
    st.subheader("6. Habillage")
    c_toi1, c_toi2 = st.columns(2)
    with c_toi1: 
        type_toile = st.selectbox("Type de toile", ["Buckram", "Fantaisie", "Autre"])
    with c_toi2: 
        couleur = st.selectbox("Couleur de la toile", options=liste_couleurs)

    with st.expander("➕ Ajouter une nouvelle couleur au catalogue commun"):
        nouvelle_couleur_saisie = st.text_input("Nom de la couleur").strip()
        if st.button("Enregistrer la couleur"):
            if nouvelle_couleur_saisie:
                ajouter_couleur_bdd(nouvelle_couleur_saisie.capitalize())
                st.success(f"Couleur ajoutée !")
                st.rerun()

    # --- SECTION 7 : OPTION PIÈCE DE TITRE EN CASCADE ---
    st.write("---")
    st.subheader("7. Pièce de titre & Suppléments")
    cocher_piece_titre = st.checkbox("**Activer une pièce de titre**", value=False)

    # Valeurs par défaut si décoché
    couleur_pieces_toile = "N/A"
    marquage_pieces = "N/A"
    supplement_1 = ""
    supplement_2 = ""
    supplement_3 = ""
    supplement_4 = ""
    hauteur_maquette = hauteur + 5  # Calculé de base

    # Si coché, on débloque toute la suite demandée
    if cocher_piece_titre:
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            couleur_pieces_toile = st.selectbox("Couleur de la pièce de titre (Table des toiles)", options=liste_couleurs)
        with c_p2:
            marquage_pieces = st.selectbox("Couleur du marquage de la pièce", ["OR", "Noir", "Blanc", "Autre"])
            
        st.info(f"📏 **Hauteur de maquette** : {hauteur_maquette} mm (H + 5 mm)")
        
        st.markdown("**Zones de saisie libre (Suppléments) :**")
        cs1, cs2 = st.columns(2)
        with cs1:
            supplement_1 = st.text_input("Supplément 1")
            supplement_2 = st.text_input("Supplément 2")
        with cs2:
            supplement_3 = st.text_input("Supplément 3")
            supplement_4 = st.text_input("Supplément 4")

    # Bouton de validation
    st.write("---")
    bouton_valider = st.button(f"💾 Valider l'enregistrement [Livre N° {numero_livre}]")

    if bouton_valider:
        if nom_client.strip() == "" or numero_train.strip() == "":
            st.error("Le nom du client et le numéro de train sont obligatoires.")
        else:
            donnees_fiche = {
                "nom_client": nom_client.strip(), "numero_train": numero_train.strip(), "numero_livre": numero_livre,
                "nature_doc": nature_doc, "etat_doc": etat_doc, "option_autre": option_autre,
                "repro_scanne": repro_scanne, "repro_report": repro_report,
                "hauteur": hauteur, "largeur": largeur, "epaisseur": epaisseur, "ne_pas_rogner": ne_pas_rogner,
                "traitement": traitement, "type_reliure": type_reliure, "type_couture": type_couture,
                "agraphes": agraphes, "nombre_cahiers": nombre_cahiers,
                "sans_titrage": sans_titrage, "titrage_sens": titrage_sens, "lignes_sup": lignes_sup, 
                "titrage_couleur": titrage_couleur, "police": police,
                "type_toile": type_toile, "couleur": couleur,
                "cocher_piece_titre": cocher_piece_titre, "couleur_pieces_toile": couleur_pieces_toile, 
                "marquage_pieces": marquage_pieces, "hauteur_maquette": hauteur_maquette,
                "supplement_1": supplement_1, "supplement_2": supplement_2, 
                "supplement_3": supplement_3, "supplement_4": supplement_4
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
                columns=["N° Livre", "Nature", "État", "Hauteur", "Reliure", "Couleur Toile", "Pièce Titre active"]
            )
            st.dataframe(df_train, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun livre créé pour le moment pour ce couple Client/Train.")
    else:
        st.info("Renseignez un client et un numéro de train pour afficher son tableau.")