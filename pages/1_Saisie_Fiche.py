import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime

def obtenir_connexion():
    conn = psycopg2.connect(st.secrets["PG_URL"])
    conn.set_client_encoding('UTF8')
    return conn

def determiner_categorie_format(l, h):
    if l <= 115 and h <= 185: return "115 x 185 (In 12)"
    elif l <= 130 and h <= 200: return "130 x 200 (In 8° écu)"
    elif l <= 160 and h <= 245: return "160 x 245 (In 8° raisin)"
    elif l <= 175 and h <= 270: return "175 x 270 (In 8° jésus)"
    elif l <= 245 and h <= 320: return "245 x 320 (In 4° raisin)"
    elif l <= 270 and h <= 350: return "270 x 350 (In 4° jésus)"
    elif l <= 280 and h <= 440: return "280 x 440 (Folio carré)"
    elif l <= 320 and h <= 490: return "320 x 490 (Folio raisin)"
    elif l <= 350 and h <= 540: return "350 x 540 (Folio jésus)"
    elif l <= 440 and h <= 600: return "440 x 600 (Grand folio)"
    elif l <= 700: return "Plano A"
    else: return "Plano B"

def lister_tous_les_clients():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM clients ORDER BY nom ASC")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients

def lister_les_trains_du_client(client):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT numero_train FROM fiches_livres WHERE nom_client = %s ORDER BY numero_train DESC", (client,))
    trains = [row[0] for row in cursor.fetchall()]
    conn.close()
    return trains

def generer_automatiquement_numero_train(client):
    annee_courante = datetime.now().year
    prefixe_recherche = f"T{annee_courante}%"
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT numero_train FROM fiches_livres WHERE nom_client = %s AND numero_train LIKE %s ORDER BY numero_train DESC LIMIT 1", (client, prefixe_recherche))
    dernier_train = cursor.fetchone()
    conn.close()
    if d_train := dernier_train:
        str_num = d_train[0][5:]
        try: prochain_ordre = int(str_num) + 1
        except ValueError: prochain_ordre = 1
    else: prochain_ordre = 1
    return f"T{annee_courante}{prochain_ordre:03d}"

def determiner_prochain_numero_livre(client, train):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero_livre) FROM fiches_livres WHERE nom_client = %s AND numero_train = %s", (client, train))
    max_num = cursor.fetchone()[0]
    conn.close()
    return (max_num + 1) if max_num is not None else 1

def recuperer_livre_specifique(client, train, num_livre):
    conn = obtenir_connexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM fiches_livres WHERE nom_client = %s AND numero_train = %s AND numero_livre = %s", (client, train, num_livre))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def recuperer_livres_du_train(client, train):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT numero_livre, nature_doc, text_doc, largeur, hauteur, type_reliure, couleur, CASE WHEN cocher_piece_titre THEN 'Oui (' || couleur_pieces_toile || ')' ELSE 'Non' END as piece_titre FROM fiches_livres WHERE nom_client = %s AND numero_train = %s ORDER BY numero_livre ASC", (client, train))
    donnees = cursor.fetchall()
    conn.close()
    return donnees

def enregistrer_ou_mettre_a_jour_livre(donnees):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    champs = ", ".join(donnees.keys())
    placeholders = ", ".join(["%s"] * len(donnees))
    updates = ", ".join([f"{k} = EXCLUDED.{k}" for k in donnees.keys() if k not in ["nom_client", "numero_train", "numero_livre"]])
    valeurs = tuple(donnees.values())
    requete = f"INSERT INTO fiches_livres ({champs}) VALUES ({placeholders}) ON CONFLICT (nom_client, numero_train, numero_livre) DO UPDATE SET {updates}"
    cursor.execute(requete, valeurs)
    conn.commit()
    conn.close()

st.set_page_config(page_title="Saisie & Suivi des Livres", layout="wide")
st.title("📚 Saisie de Fiche — Devis + Traitements")

liste_clients_existants = lister_tous_les_clients()
liste_couleurs = ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]

if not liste_clients_existants:
    st.warning("⚠️ Créez d'abord un client dans le module 'Fiches Clients'.")
else:
    col_saisie, col_visualisation = st.columns([1.2, 0.8])
    with col_saisie:
        st.header("📋 Saisie de la fiche")
        nom_client_valide = st.selectbox("Client", options=liste_clients_existants)
        liste_trains_existants = lister_les_trains_du_client(nom_client_valide)
        
        c_tr1, c_tr2 = st.columns([1.2, 0.8])
        with c_tr1:
            options_train = ["-- Nouveau train automatique --"] + liste_trains_existants
            train_selectionne = st.selectbox("Sélectionner le train", options=options_train)
        numero_train = generer_automatiquement_numero_train(nom_client_valide) if train_selectionne == "-- Nouveau train automatique --" else train_selectionne
        with c_tr2: st.info(f"📂 Train : **{numero_train}**")

        num_livre_en_cours = 1
        donnees_edition = None
        if "livre_selectionne" in st.session_state:
            num_livre_en_cours = st.session_state.livre_selectionne
            donnees_edition = recuperer_livre_specifique(nom_client_valide, numero_train, num_livre_en_cours)
            st.warning(f"🔄 Modification du Livre N° {num_livre_en_cours}")
            if st.button("❌ Annuler la modification"):
                del st.session_state.livre_selectionne
                st.rerun()
        else:
            num_livre_en_cours = determiner_prochain_numero_livre(nom_client_valide, numero_train)
            st.info(f"✨ Livre suivant automatique : **{num_livre_en_cours}**")

        st.write("---")
        nature_doc = st.radio("Nature :", ["Monographie (Mono)", "Périodique (Pério)"], horizontal=True, index=0 if donnees_edition and donnees_edition["nature_doc"] == "Monographie (Mono)" else (1 if donnees_edition and donnees_edition["nature_doc"] == "Périodique (Pério)" else 0))
        text_doc = st.radio("État :", ["Neuf", "Usagé"], horizontal=True, index=0 if donnees_edition and donnees_edition["text_doc"] == "Neuf" else (1 if donnees_edition and donnees_edition["text_doc"] == "Usagé" else 0))

        cocher_autre = st.checkbox("Autre (Matières spécifiques)", value=True if donnees_edition and donnees_edition["option_autre"] != "N/A" else False)
        option_autre = "N/A"
        if cocher_autre:
            idx_opt = ["Cuir", "1/2 cuir", "1/2 toile"].index(donnees_edition["option_autre"]) if donnees_edition and donnees_edition["option_autre"] in ["Cuir", "1/2 cuir", "1/2 toile"] else 0
            option_autre = st.radio("Finition :", ["Cuir", "1/2 cuir", "1/2 toile"], horizontal=True, index=idx_opt)

        st.markdown("**Reprographie :**")
        col_scanne, col_report, _ = st.columns([1, 1, 3])
        with col_scanne: repro_scanne = st.checkbox("Scannée", value=bool(donnees_edition["repro_scanne"]) if donnees_edition else False)
        with col_report: repro_report = st.checkbox("Report", value=bool(donnees_edition["repro_report"]) if donnees_edition else False)

        st.write("---")
        st.subheader("3. Désignation format")
        c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)
        with c_dim1: largeur = st.number_input("Largeur (mm)", min_value=0, value=int(donnees_edition["largeur"]) if donnees_edition else 160, step=1)
        with c_dim2: hauteur = st.number_input("Hauteur (mm)", min_value=0, value=int(donnees_edition["hauteur"]) if donnees_edition else 220, step=1)
        with c_dim3: epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=int(donnees_edition["epaisseur"]) if donnees_edition else 20, step=1)
        with c_dim4: ne_pas_rogner = st.checkbox("Ne pas rogner", value=bool(donnees_edition["ne_pas_rogner"]) if donnees_edition else False)

        format_detecte = determiner_categorie_format(largeur, hauteur)
        st.success(f"📐 **Format détecté** : {format_detecte}")

        st.subheader("4. Traitements & Reliure")
        c_trt1, c_trt2, c_trt3 = st.columns(3)
        list_trt = ["T1", "T2", "T3", "T4", "T5", "T6"]
        with c_trt1: traitement = st.selectbox("Traitement", list_trt, index=list_trt.index(donnees_edition["traitement"]) if donnees_edition and donnees_edition["traitement"] in list_trt else 0)
        list_rel = ["Bradel", "Emboîtage", "Passure en carton"]
        with c_trt2: type_reliure = st.selectbox("Type de reliure", list_rel, index=list_rel.index(donnees_edition["type_reliure"]) if donnees_edition and donnees_edition["type_reliure"] in list_rel else 0)
        list_cou = ["Cahiers machine", "Surjeté", "Cahier manuel"]
        with c_trt3: type_couture = st.selectbox("Type de couture", list_cou, index=list_cou.index(donnees_edition["type_couture"]) if donnees_edition and donnees_edition["type_couture"] in list_cou else 0)

        agraphes = False; nombre_cahiers = 0
        if type_couture == "Cahier manuel":
            c_cah1, c_cah2 = st.columns(2)
            with c_cah1: agraphes = st.checkbox("Présence d'agraphes", value=bool(donnees_edition["agraphes"]) if donnees_edition else False)
            with c_cah2: nombre_cahiers = st.number_input("Nombre de cahiers", min_value=0, value=int(donnees_edition["nombre_cahiers"]) if donnees_edition else 0, step=1)

        st.write("---")
        st.subheader("5. Spécifications du titrage")
        sans_titrage = st.checkbox("**Pas de titrage**", value=bool(donnees_edition["sans_titrage"]) if donnees_edition else False)
        titrage_sens = "N/A"; lignes_sup = 0; titrage_couleur = "N/A"; police = "N/A"
        if not sans_titrage:
            c_tit1, c_tit2, c_tit3, c_tit4 = st.columns(4)
            with c_tit1: titrage_sens = st.radio("Sens", ["Long", "Travers"], horizontal=True, index=0 if donnees_edition and donnees_edition["titrage_sens"] == "Long" else (1 if donnees_edition and donnees_edition["titrage_sens"] == "Travers" else 0))
            with c_tit2: lignes_sup = st.number_input("Lignes sup", min_value=0, value=int(donnees_edition["lignes_sup"]) if donnees_edition else 0, step=1)
            list_marq = ["OR", "ARGENT", "BLANC", "NOIR"]
            with c_tit3: titrage_couleur = st.selectbox("Marquage", list_marq, index=list_marq.index(donnees_edition["titrage_couleur"]) if donnees_edition and donnees_edition["titrage_couleur"] in list_marq else 0)
            with c_tit4: police = st.radio("Police", ["Elzévir", "Baskerville"], horizontal=True, index=0 if donnees_edition and donnees_edition["police"] == "Elzévir" else (1 if donnees_edition and donnees_edition["police"] == "Baskerville" else 0))

        st.write("---")
        st.subheader("6. Habillage")
        c_toi1, c_toi2 = st.columns(2)
        list_toile = ["Buckram", "Fantaisie", "Autre"]
        with c_toi1: type_toile = st.selectbox("Type de toile", list_toile, index=list_toile.index(donnees_edition["type_toile"]) if donnees_edition and donnees_edition["type_toile"] in list_toile else 0)
        with c_toi2: couleur = st.selectbox("Couleur de la toile", options=liste_couleurs, index=liste_couleurs.index(donnees_edition["couleur"]) if donnees_edition and donnees_edition["couleur"] in liste_couleurs else 0)

        st.write("---")
        st.subheader("7. Pièce de titre & Suppléments")
        cocher_piece_titre = st.checkbox("**Activer une pièce de titre**", value=bool(donnees_edition["cocher_piece_titre"]) if donnees_edition else False)
        couleur_pieces_toile = "N/A"; marquage_pieces = "N/A"
        valeur_maquette_defaut = int(donnees_edition["hauteur_maquette"]) if donnees_edition else (hauteur + 5)
        if cocher_piece_titre:
            c_p1, c_p2, c_p3 = st.columns(3)
            with c_p1: couleur_pieces_toile = st.selectbox("Couleur de la pièce", options=liste_couleurs, index=liste_couleurs.index(donnees_edition["couleur_pieces_toile"]) if donnees_edition and donnees_edition["couleur_pieces_toile"] in liste_couleurs else 0)
            list_mp = ["OR", "ARGENT", "BLANC", "NOIR"]
            with c_p2: marquage_pieces = st.selectbox("Marquage de la pièce", list_mp, index=list_mp.index(donnees_edition["marquage_pieces"]) if donnees_edition and donnees_edition["marquage_pieces"] in list_mp else 0)
            with c_p3: hauteur_maquette = st.number_input("Hauteur maquette (mm)", min_value=0, value=valeur_maquette_defaut, step=1)
        else: hauteur_maquette = valeur_maquette_defaut

        st.write("---")
        if st.button("💾 Valider l'enregistrement"):
            donnees_fiche = {
                "nom_client": nom_client_valide, "numero_train": numero_train, "numero_livre": num_livre_en_cours,
                "nature_doc": nature_doc, "text_doc": text_doc, "option_autre": option_autre, "repro_scanne": repro_scanne, "repro_report": repro_report,
                "hauteur": hauteur, "largeur": largeur, "epaisseur": epaisseur, "ne_pas_rogner": ne_pas_rogner, "traitement": traitement, "type_reliure": type_reliure, "type_couture": type_couture,
                "agraphes": agraphes, "nombre_cahiers": nombre_cahiers, "sans_titrage": sans_titrage, "titrage_sens": titrage_sens, "lignes_sup": lignes_sup, "titrage_couleur": titrage_couleur, "police": police, "type_toile": type_toile, "couleur": couleur,
                "cocher_piece_titre": cocher_piece_titre, "couleur_pieces_toile": couleur_pieces_toile, "marquage_pieces": marquage_pieces, "hauteur_maquette": hauteur_maquette,
                "supplement_1": "", "supplement_2": "", "supplement_3": "", "supplement_4": ""
            }
            enregistrer_ou_mettre_a_jour_livre(donnees_fiche)
            st.success("Données enregistrées avec succès sur Supabase !")
            if "livre_selectionne" in st.session_state: del st.session_state.livre_selectionne
            st.rerun()

    with col_visualisation:
        st.header("📊 Suivi en direct du Train")
        if nom_client_valide and numero_train:
            st.subheader(f"Train : {numero_train}")
            livres_train = recuperer_livres_du_train(nom_client_valide, numero_train)
            if livres_train:
                df_train = pd.DataFrame(livres_train, columns=["N° Livre", "Nature", "État", "Largeur", "Hauteur", "Reliure", "Couleur Toile", "Pièce Titre active"])
                reponse_selection = st.dataframe(df_train, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun")
                if reponse_selection and "rows" in reponse_selection.get("selection", {}):
                    lignes_selectionnees = reponse_selection["selection"]["rows"]
                    if lignes_selectionnees:
                        st.session_state.livre_selectionne = int(df_train.iloc[lignes_selectionnees[0]]["N° Livre"])
                        st.rerun()
            else: st.info("Aucun livre dans ce Train.")
