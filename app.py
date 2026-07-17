import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_FILE = "base_reliure_finale.db"

def initialiser_bdd():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Table des livres
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_livres (
            nom_client TEXT NOT NULL,
            numero_train TEXT NOT NULL,
            numero_livre INTEGER NOT NULL,
            nature_doc TEXT,
            text_doc TEXT,
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
            sans_titrage BOOLEAN,
            titrage_sens TEXT,
            lignes_sup INTEGER,
            titrage_couleur TEXT,
            police TEXT,
            type_toile TEXT,
            couleur TEXT,
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
    # Nouvelle Table Fiche Client
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            nom TEXT PRIMARY KEY,
            adresse TEXT,
            telephone TEXT,
            email TEXT,
            contact_nom TEXT,
            notes TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS couleurs_toile (nom_couleur TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

# --- FONCTIONS CLIENTS ---
def lister_tous_les_clients():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM clients ORDER BY nom ASC")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients

def recuperer_fiche_client(nom_client):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE nom = ?", (nom_client,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def enregistrer_client(nom, adresse, telephone, email, contact, notes):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (nom, adresse, telephone, email, contact_nom, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(nom) DO UPDATE SET
            adresse=excluded.adresse,
            telephone=excluded.telephone,
            email=excluded.email,
            contact_nom=excluded.contact_nom,
            notes=excluded.notes
    """, (nom, adresse, telephone, email, contact, notes))
    conn.commit()
    conn.close()

def supprimer_client_bdd(nom_client):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE nom = ?", (nom_client,))
    cursor.execute("DELETE FROM fiches_livres WHERE nom_client = ?", (nom_client,))
    conn.commit()
    conn.close()

# --- FONCTIONS TRAINS ET LIVRES ---
def lister_les_trains_du_client(client):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT numero_train FROM fiches_livres WHERE nom_client = ? ORDER BY numero_train DESC", (client,))
    trains = [row[0] for row in cursor.fetchall()]
    conn.close()
    return trains

def generer_automatiquement_numero_train(client):
    """Génère un numéro de train type T2026001 basé sur le max existant pour l'année en cours."""
    annee_courante = datetime.now().year
    prefixe_recherche = f"T{annee_courante}%"
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT numero_train FROM fiches_livres 
        WHERE nom_client = ? AND numero_train LIKE ?
        ORDER BY numero_train DESC LIMIT 1
    """, (client, prefixe_recherche))
    dernier_train = cursor.fetchone()
    conn.close()
    
    if dernier_train:
        str_num = dernier_train[0][5:]  # Extrait les 3 derniers digits
        try:
            prochain_ordre = int(str_num) + 1
        except ValueError:
            prochain_ordre = 1
    else:
        prochain_ordre = 1
        
    return f"T{annee_courante}{prochain_ordre:03d}"

def determiner_prochain_numero_livre(client, train):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero_livre) FROM fiches_livres WHERE nom_client = ? AND numero_train = ?", (client, train))
    max_num = cursor.fetchone()[0]
    conn.close()
    return (max_num + 1) if max_num is not None else 1

def enregistrer_ou_mettre_a_jour_livre(donnees):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    champs = ", ".join(donnees.keys())
    placeholders = ", ".join(["?"] * len(donnees))
    valeurs = tuple(donnees.values())
    cursor.execute(f"INSERT INTO fiches_livres ({champs}) VALUES ({placeholders})", valeurs)
    conn.commit()
    conn.close()

def recuperer_livre_specifique(client, train, num_livre):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fiches_livres WHERE nom_client = ? AND numero_train = ? AND numero_livre = ?", (client, train, num_livre))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def recuperer_livres_du_train(client, train):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT numero_livre, nature_doc, text_doc, hauteur, type_reliure, couleur,
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

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Gestion Atelier Reliure", layout="wide")

tabs = st.tabs(["📚 Saisie & Suivi des Livres", "🏢 Fiches Clients"])
liste_couleurs = charger_couleurs()
liste_clients_existants = lister_tous_les_clients()

# ==========================================
# TAB 2 : GESTION DES FICHES CLIENTS
# ==========================================
with tabs[1]:
    st.header("🏢 Gestion de l'Annuaire des Clients")
    
    action_client = st.radio("Action :", ["Sélectionner / Modifier un client", "➕ Créer un nouveau client"], horizontal=True)
    st.write("---")
    
    if action_client == "➕ Créer un nouveau client":
        with st.form("form_creer_client"):
            nc_nom = st.text_input("Nom de l'établissement / Client *").strip()
            nc_contact = st.text_input("Nom du contact référent")
            nc_adresse = st.text_area("Adresse complète")
            c_tel, c_mel = st.columns(2)
            with c_tel: nc_tel = st.text_input("Téléphone")
            with c_mel: nc_mail = st.text_input("Adresse E-mail")
            nc_notes = st.text_area("Notes d'atelier spécifiques (Ex: habillage habituel...)")
            
            bouton_creer = st.form_submit_button("💾 Enregistrer le nouveau client")
            if bouton_creer:
                if not nc_nom:
                    st.error("Le nom du client est obligatoire.")
                else:
                    enregistrer_client(nc_nom, nc_adresse, nc_tel, nc_mail, nc_contact, nc_notes)
                    st.success(f"Client '{nc_nom}' ajouté avec succès.")
                    st.rerun()
                    
    else:
        if not liste_clients_existants:
            st.info("Aucun client enregistré pour le moment.")
        else:
            client_sel = st.selectbox("Choisir le client à gérer :", options=liste_clients_existants)
            fiche = recuperer_fiche_client(client_sel)
            
            if fiche:
                with st.form("form_modif_client"):
                    st.markdown(f"### Édition de la fiche : **{fiche['nom']}**")
                    mod_contact = st.text_input("Nom du contact référent", value=fiche["contact_nom"])
                    mod_adresse = st.text_area("Adresse complète", value=fiche["adresse"])
                    c_tel2, c_mel2 = st.columns(2)
                    with c_tel2: mod_tel = st.text_input("Téléphone", value=fiche["telephone"])
                    with c_mel2: mod_mail = st.text_input("Adresse E-mail", value=fiche["email"])
                    mod_notes = st.text_area("Notes d'atelier spécifiques", value=fiche["notes"])
                    
                    bouton_modif = st.form_submit_button("💾 Sauvegarder les modifications")
                    if bouton_modif:
                        enregistrer_client(fiche["nom"], mod_adresse, mod_tel, mod_mail, mod_contact, mod_notes)
                        st.success("Fiche client mise à jour.")
                        st.rerun()
                        
                st.write("---")
                with st.expander("🚨 Zone de danger — Supprimer le client"):
                    st.warning(f"La suppression de **{fiche['nom']}** détruira définitivement sa fiche ainsi que tous ses livres et trains associés.")
                    confirme_suppr = st.checkbox(f"Je confirme vouloir supprimer définitivement {fiche['nom']}")
                    if st.button("❌ Supprimer définitivement"):
                        if confirme_suppr:
                            supprimer_client_bdd(fiche["nom"])
                            st.success("Client effacé.")
                            st.rerun()
                        else:
                            st.error("Veuillez cocher la case de confirmation.")

# ==========================================
# TAB 1 : SAISIE & SUIVI DES LIVRES
# ==========================================
with tabs[0]:
    st.title("📚 Saisie de Fiche — Devis + Traitements")
    
    if not liste_clients_existants:
        st.warning("⚠️ Veuillez d'abord créer un client dans l'onglet 'Fiches Clients' pour commencer la saisie.")
    else:
        col_saisie, col_visualisation = st.columns([1.2, 0.8])
        
        with col_saisie:
            st.header("📋 Saisie de la fiche")
            st.subheader("1. Clés d'enregistrement")
            
            # Sélection Client simplifiée
            nom_client_valide = st.selectbox("Client", options=liste_clients_existants, key="livre_client_selectbox")
            liste_trains_existants = lister_les_trains_du_client(nom_client_valide)
            
            # Choix ou génération du Train
            c_tr1, c_tr2 = st.columns([1.2, 0.8])
            with c_tr1:
                options_train = ["-- Nouveau train automatique --"] + liste_trains_existants
                train_selectionne = st.selectbox("Sélectionner le train", options=options_train)
            
            if train_selectionne == "-- Nouveau train automatique --":
                numero_train = generer_automatiquement_numero_train(nom_client_valide)
                with c_tr2:
                    st.info(f"⚙️ Prochain numéro : **{numero_train}**")
            else:
                numero_train = train_selectionne
                with c_tr2:
                    st.success(f"📂 Train actif : **{numero_train}**")

            # Gestion du numéro de livre
            num_livre_en_cours = 1
            donnees_edition = None

            if "livre_selectionne" in st.session_state and nom_client_valide and numero_train:
                num_livre_en_cours = st.session_state.livre_selectionne
                donnees_edition = recuperer_livre_specifique(nom_client_valide, numero_train, num_livre_en_cours)
                st.warning(f"🔄 Mode Modification : Vous éditez actuellement le Livre N° {num_livre_en_cours}")
                if st.button("❌ Annuler la modification (Revenir au livre suivant)"):
                    del st.session_state.livre_selectionne
                    st.rerun()
            elif nom_client_valide and numero_train:
                num_livre_en_cours = determiner_prochain_numero_livre(nom_client_valide, numero_train)
                st.info(f"✨ Nouveau Livre : Numéro attribué automatiquement : **{num_livre_en_cours}**")

            # --- FORMULAIRE ---
            st.write("---")
            st.subheader("2. Nature et Finition du document")
            
            idx_nature = 0 if donnees_edition and donnees_edition["nature_doc"] == "Monographie (Mono)" else (1 if donnees_edition and donnees_edition["nature_doc"] == "Périodique (Pério)" else 0)
            nature_doc = st.radio("**Sélectionnez la nature du document :**", ["Monographie (Mono)", "Périodique (Pério)"], horizontal=True, index=idx_nature)
            
            idx_etat = 0 if donnees_edition and donnees_edition["text_doc"] == "Neuf" else (1 if donnees_edition and donnees_edition["text_doc"] == "Usagé" else 0)
            text_doc = st.radio("**Sélectionnez l'état :**", ["Neuf", "Usagé"], horizontal=True, index=idx_etat)

            val_autre = True if donnees_edition and donnees_edition["option_autre"] != "N/A" else False
            cocher_autre = st.checkbox("Autre (Matières spécifiques)", value=val_autre)
            option_autre = "N/A"
            if cocher_autre:
                idx_opt = ["Cuir", "1/2 cuir", "1/2 toile"].index(donnees_edition["option_autre"]) if donnees_edition and donnees_edition["option_autre"] in ["Cuir", "1/2 cuir", "1/2 toile"] else 0
                option_autre = st.radio("Finition spécifique :", ["Cuir", "1/2 cuir", "1/2 toile"], horizontal=True, index=idx_opt)

            st.markdown("**Reprographie :**")
            val_scanne = bool(donnees_edition["repro_scanne"]) if donnees_edition else False
            val_report = bool(donnees_edition["repro_report"]) if donnees_edition else False
            col_scanne, col_report, _ = st.columns([1, 1, 3])
            with col_scanne: repro_scanne = st.checkbox("Scannée", value=val_scanne)
            with col_report: repro_report = st.checkbox("Report", value=val_report)

            # --- SECTION 3 : DIMENSIONS ---
            st.write("---")
            st.subheader("3. Désignation format")
            c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)
            with c_dim1: hauteur = st.number_input("Hauteur (mm)", min_value=0, value=int(donnees_edition["hauteur"]) if donnees_edition else 220, step=1)
            with c_dim2: largeur = st.number_input("Largeur (mm)", min_value=0, value=int(donnees_edition["largeur"]) if donnees_edition else 160, step=1)
            with c_dim3: epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=int(donnees_edition["epaisseur"]) if donnees_edition else 20, step=1)
            with c_dim4: ne_pas_rogner = st.checkbox("Ne pas rogner", value=bool(donnees_edition["ne_pas_rogner"]) if donnees_edition else False)

            # --- SECTION 4 : TRAITEMENTS & RELIURE ---
            st.subheader("4. Traitements & Reliure")
            c_trt1, c_trt2, c_trt3 = st.columns(3)
            
            list_trt = ["T1", "T2", "T3", "T4", "T5", "T6"]
            idx_trt = list_trt.index(donnees_edition["traitement"]) if donnees_edition and donnees_edition["traitement"] in list_trt else 0
            with c_trt1: traitement = st.selectbox("Traitement de structure", list_trt, index=idx_trt)
            
            list_rel = ["Bradel", "Emboîtage", "Passure en carton"]
            idx_rel = list_rel.index(donnees_edition["type_reliure"]) if donnees_edition and donnees_edition["type_reliure"] in list_rel else 0
            with c_trt2: type_reliure = st.selectbox("Type de reliure", list_rel, index=idx_rel)
            
            list_cou = ["Cahiers machine", "Surjeté", "Cahier manuel"]
            idx_cou = list_cou.index(donnees_edition["type_couture"]) if donnees_edition and donnees_edition["type_couture"] in list_cou else 0
            with c_trt3: type_couture = st.selectbox("Type de couture", list_cou, index=idx_cou)

            agraphes = False
            nombre_cahiers = 0
            if type_couture == "Cahier manuel":
                st.markdown("**Options spécifiques au Couture manuelle :**")
                c_cah1, c_cah2 = st.columns(2)
                with c_cah1: agraphes = st.checkbox("Présence d'agraphes", value=bool(donnees_edition["agraphes"]) if donnees_edition else False)
                with c_cah2: nombre_cahiers = st.number_input("Nombre de cahiers", min_value=0, value=int(donnees_edition["nombre_cahiers"]) if donnees_edition else 0, step=1)

            # --- SECTION 5 : TITRAGE ---
            st.write("---")
            st.subheader("5. Spécifications du titrage")
            val_sans_titrage = bool(donnees_edition["sans_titrage"]) if donnees_edition else False
            sans_titrage = st.checkbox("**Pas de titrage (Masquer la saisie)**", value=val_sans_titrage)

            titrage_sens = "N/A"; lignes_sup = 0; titrage_couleur = "N/A"; police = "N/A"

            if not sans_titrage:
                c_tit1, c_tit2, c_tit3, c_tit4 = st.columns(4)
                idx_sens = 0 if donnees_edition and donnees_edition["titrage_sens"] == "Long" else (1 if donnees_edition and donnees_edition["titrage_sens"] == "Travers" else 0)
                with c_tit1: titrage_sens = st.radio("Sens du titrage", ["Long", "Travers"], horizontal=True, index=idx_sens)
                with c_tit2: lignes_sup = st.number_input("Lignes supplémentaires (Nbre)", min_value=0, value=int(donnees_edition["lignes_sup"]) if donnees_edition else 0, step=1)
                
                list_marq = ["OR", "ARGENT", "BLANC", "NOIR"]
                idx_marq = list_marq.index(donnees_edition["titrage_couleur"]) if donnees_edition and donnees_edition["titrage_couleur"] in list_marq else 0
                with c_tit3: titrage_couleur = st.selectbox("Couleur du marquage (Caractères)", list_marq, index=idx_marq)
                
                idx_pol = 0 if donnees_edition and donnees_edition["police"] == "Elzévir" else (1 if donnees_edition and donnees_edition["police"] == "Baskerville" else 0)
                with c_tit4: police = st.radio("Police de caractère", ["Elzévir", "Baskerville"], horizontal=True, index=idx_pol)

            # --- SECTION 6 : HABILLAGE ---
            st.write("---")
            st.subheader("6. Habillage")
            c_toi1, c_toi2 = st.columns(2)
            
            list_toile = ["Buckram", "Fantaisie", "Autre"]
            idx_toile = list_toile.index(donnees_edition["type_toile"]) if donnees_edition and donnees_edition["type_toile"] in list_toile else 0
            with c_toi1: type_toile = st.selectbox("Type de toile", list_toile, index=idx_toile)
            
            idx_c_toile = liste_couleurs.index(donnees_edition["couleur"]) if donnees_edition and donnees_edition["couleur"] in liste_couleurs else 0
            with c_toi2: couleur = st.selectbox("Couleur de la toile", options=liste_couleurs, index=idx_c_toile)

            with st.expander("➕ Ajouter une nouvelle couleur au catalogue commun"):
                nouvelle_couleur_saisie = st.text_input("Nom de la couleur").strip()
                if st.button("Enregistrer la couleur"):
                    if nouvelle_couleur_saisie:
                        ajouter_couleur_bdd(nouvelle_couleur_saisie.capitalize())
                        st.success("Couleur ajoutée au catalogue !")
                        st.rerun()

            # --- SECTION 7 : OPTION PIÈCE DE TITRE & SUPPLÉMENTS ---
            st.write("---")
            st.subheader("7. Pièce de titre & Suppléments")
            
            val_c_piece = bool(donnees_edition["cocher_piece_titre"]) if donnees_edition else False
            cocher_piece_titre = st.checkbox("**Activer une pièce de titre**", value=val_c_piece)

            couleur_pieces_toile = "N/A"; marquage_pieces = "N/A"
            supplement_1 = ""; supplement_2 = ""; supplement_3 = ""; supplement_4 = ""
            valeur_maquette_defaut = int(donnees_edition["hauteur_maquette"]) if donnees_edition else (hauteur + 5)

            if cocher_piece_titre:
                c_p1, c_p2, c_p3 = st.columns(3)
                idx_c_piece = liste_couleurs.index(donnees_edition["couleur_pieces_toile"]) if donnees_edition and donnees_edition["couleur_pieces_toile"] in liste_couleurs else 0
                with c_p1: couleur_pieces_toile = st.selectbox("Couleur de la pièce de titre", options=liste_couleurs, index=idx_c_piece)
                
                list_mp = ["OR", "ARGENT", "BLANC", "NOIR"]
                idx_mp = list_mp.index(donnees_edition["marquage_pieces"]) if donnees_edition and donnees_edition["marquage_pieces"] in list_mp else 0
                with c_p2: marquage_pieces = st.selectbox("Couleur du marquage de la pièce", list_mp, index=idx_mp)
                    
                with c_p3: hauteur_maquette = st.number_input("Hauteur maquette (mm)", min_value=0, value=valeur_maquette_defaut, step=1)
                    
                st.markdown("**Zones de saisie libre (Suppléments) :**")
                cs1, cs2 = st.columns(2)
                with cs1:
                    supplement_1 = st.text_input("Supplément 1", value=donnees_edition["supplement_1"] if donnees_edition else "")
                    supplement_2 = st.text_input("Supplément 2", value=donnees_edition["supplement_2"] if donnees_edition else "")
                with cs2:
                    supplement_3 = st.text_input("Supplément 3", value=donnees_edition["supplement_3"] if donnees_edition else "")
                    supplement_4 = st.text_input("Supplément 4", value=donnees_edition["supplement_4"] if donnees_edition else "")
            else:
                hauteur_maquette = valeur_maquette_defaut

            # Bouton de validation
            st.write("---")
            label_bouton = f"💾 Enregistrer les modifications du Livre N° {num_livre_en_cours}" if donnees_edition else f"💾 Valider l'enregistrement [Livre N° {num_livre_en_cours}]"
            bouton_valider = st.button(label_bouton)

            if bouton_valider:
                donnees_fiche = {
                    "nom_client": nom_client_valide, "numero_train": numero_train, "numero_livre": num_livre_en_cours,
                    "nature_doc": nature_doc, "text_doc": text_doc, "option_autre": option_autre,
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
                st.success("Données enregistrées avec succès !")
                if "livre_selectionne" in st.session_state:
                    del st.session_state.livre_selectionne
                st.rerun()

        # --- COLONNE DE DROITE (VISUALISATION & SELECTION) ---
        with col_visualisation:
            st.header("📊 Suivi en direct du Train")
            
            if nom_client_valide and numero_train:
                st.subheader(f"Client : {nom_client_valide} | Train : {numero_train}")
                livres_train = recuperer_livres_du_train(nom_client_valide, numero_train)
                
                if livres_train:
                    st.markdown("💡 *Cliquez sur une ligne du tableau pour charger et modifier le livre correspondant.*")
                    df_train = pd.DataFrame(
                        livres_train, 
                        columns=["N° Livre", "Nature", "État", "Hauteur", "Reliure", "Couleur Toile", "Pièce Titre active"]
                    )
                    
                    reponse_selection = st.dataframe(
                        df_train, 
                        use_container_width=True, 
                        hide_index=True,
                        selection_mode="single-row",
                        on_select="rerun"
                    )
                    
                    if reponse_selection and "rows" in reponse_selection.get("selection", {}):
                        lignes_selectionnees = reponse_selection["selection"]["rows"]
                        if lignes_selectionnees:
                            index_ligne = lignes_selectionnees[0]
                            numero_livre_selectionne = int(df_train.iloc[index_ligne]["N° Livre"])
                            st.session_state.livre_selectionne = numero_livre_selectionne
                            st.rerun()
                else:
                    st.info("Aucun livre créé pour le moment pour ce Train.")