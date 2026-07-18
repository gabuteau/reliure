import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

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

def generer_automatiquement_numero_train(client):
    annee_courante = datetime.now().year
    prefixe = f"T{annee_courante}"
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("numero_train").eq("nom_client", client).like("numero_train", f"{prefixe}%").execute()
    trains = list(set([row["numero_train"] for row in reponse.data]))
    if trains:
        trains.sort(reverse=True)
        str_num = trains[0][5:]
        try: prochain_ordre = int(str_num) + 1
        except ValueError: prochain_ordre = 1
    else:
        prochain_ordre = 1
    return f"{prefixe}{prochain_ordre:03d}"

def determiner_prochain_numero_livre(client, train):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("numero_livre").eq("nom_client", client).eq("numero_train", train).execute()
    nums = [row["numero_livre"] for row in reponse.data]
    return (max(nums) + 1) if nums else 1

def recuperer_livre_specifique(client, train, num_livre):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("*").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
    return reponse.data[0] if reponse.data else None

def recuperer_livres_du_train(client, train):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("numero_livre, nature_doc, text_doc, largeur, hauteur, type_reliure, couleur, cocher_piece_titre, couleur_pieces_toile").eq("nom_client", client).eq("numero_train", train).order("numero_livre").execute()
    
    donnees_formatees = []
    for r in reponse.data:
        pt_active = f"Oui ({r['couleur_pieces_toile']})" if r['cocher_piece_titre'] else "Non"
        donnees_formatees.append([
            r['numero_livre'], r['nature_doc'], r['text_doc'], r['largeur'], r['hauteur'], r['type_reliure'], r['couleur'], pt_active
        ])
    return donnees_formatees

def enregistrer_ou_mettre_a_jour_livre(donnees):
    supabase = obtenir_client_supabase()
    supabase.table("fiches_livres").upsert(donnees).execute()

st.set_page_config(page_title="Saisie & Suivi des Livres", layout="wide")
st.title("📚 Saisie de Fiche — Devis + Traitements")

liste_clients_existants = lister_tous_les_clients()
liste_couleurs = ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]

OPTIONS_SUPPLEMENTS = [
    "Plats conservés", "Onglets", "Doublage japon", "Charnières toile", 
    "Conservation de gardes", "Couture sur nerfs", "Couvrure sur nerf", 
    "Filets fleurons", "Plaçure", "Sup ouvrage déjà relié", 
    "Plaçure intercalaires", "Doublage couverture", "Montage de couverture", 
    "Fonds de cahiers", "Pose antivol", "Désacidification", 
    "Désinfection", "Charnière cuir", "Enlever agrafes", 
    "Couture manuelle sur rubans"
]

# Grille tarifaire indicative de l'atelier
PRIX_SUPPLEMENTS = {
    "Plats conservés": 15.00, "Onglets": 8.50, "Doublage japon": 22.00, "Charnières toile": 14.00,
    "Conservation de gardes": 12.00, "Couture sur nerfs": 35.00, "Couvrure sur nerf": 40.00,
    "Filets fleurons": 25.00, "Plaçure": 18.00, "Sup ouvrage déjà relié": 30.00,
    "Plaçure intercalaires": 15.00, "Doublage couverture": 20.00, "Montage de couverture": 17.50,
    "Fonds de cahiers": 12.50, "Pose antivol": 3.00, "Désacidification": 45.00,
    "Désinfection": 50.00, "Charnière cuir": 28.00, "Enlever agrafes": 9.00,
    "Couture manuelle sur rubans": 32.00
}

if not liste_clients_existants:
    st.warning("⚠️ Créez d'abord un client dans le module 'Fiches Clients'.")
else:
    col_saisie, col_visualisation = st.columns([1.2, 0.8])
    
    with col_saisie:
        st.subheader("Clé d'identification du Train")
        c_tr1, c_tr2 = st.columns(2)
        with c_tr1:
            nom_client_valide = st.selectbox("1. Sélectionner le client", options=["-- Choisir un client --"] + liste_clients_existants)
        
        if nom_client_valide == "-- Choisir un client --":
            st.info("💡 Sélectionnez un client pour afficher ou créer un train de livres.")
            train_charge_valide = False
        else:
            liste_trains_existants = lister_les_trains_du_client(nom_client_valide)
            options_train = ["-- Choisir un train --", "[+] Créer un nouveau train automatiquement"] + liste_trains_existants
            
            with c_tr2:
                train_selectionne = st.selectbox("2. Sélectionner le n° de train", options=options_train)
            
            if train_selectionne == "-- Choisir un train --":
                st.info("💡 Sélectionnez un numéro de train existant ou demandez une création automatique.")
                train_charge_valide = False
            else:
                train_charge_valide = True
                if train_selectionne == "[+] Créer un nouveau train automatiquement":
                    numero_train = generer_automatiquement_numero_train(nom_client_valide)
                else:
                    numero_train = train_selectionne

    if train_charge_valide:
        with col_saisie:
            st.write("---")
            st.header(f"📋 Saisie de la fiche — Train : {numero_train}")
            
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
                st.info(f"✨ Livre suivant automatique : **Livre N° {num_livre_en_cours}**")

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
            col_dim1, col_dim2, col_dim3, col_dim4 = st.columns(4)
            with col_dim1: largeur = st.number_input("Largeur (mm)", min_value=0, value=int(donnees_edition["largeur"]) if donnees_edition else 160, step=1)
            with col_dim2: hauteur = st.number_input("Hauteur (mm)", min_value=0, value=int(donnees_edition["hauteur"]) if donnees_edition else 220, step=1)
            with col_dim3: epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=int(donnees_edition["epaisseur"]) if donnees_edition else 20, step=1)
            with col_dim4: ne_pas_rogner = st.checkbox("Ne pas rogner", value=bool(donnees_edition["ne_pas_rogner"]) if donnees_edition else False)

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
            st.subheader("8. Suppléments optionnels (Max 4)")

            def afficher_prix_indicatif(nom_supplement):
                """Affiche le tarif sous la cellule si un supplément est sélectionné"""
                if nom_supplement and nom_supplement != "-- Aucun --":
                    prix = PRIX_SUPPLEMENTS.get(nom_supplement, 0.00)
                    st.caption(f"💰 *Prix indicatif : {prix:.2f} €*")
                else:
                    st.caption(" ") # Conserve l'alignement vertical

            sup1_def = donnees_edition["supplement_1"] if (donnees_edition and donnees_edition["supplement_1"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --"
            sup2_def = donnees_edition["supplement_2"] if (donnees_edition and donnees_edition["supplement_2"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --"
            sup3_def = donnees_edition["supplement_3"] if (donnees_edition and donnees_edition["supplement_3"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --"
            sup4_def = donnees_edition["supplement_4"] if (donnees_edition and donnees_edition["supplement_4"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --"

            liste_choix_sups = ["-- Aucun --"] + OPTIONS_SUPPLEMENTS
            c_sup1, c_sup2 = st.columns(2)
            with c_sup1: 
                supplement_1 = st.selectbox("Supplément 1", options=liste_choix_sups, index=liste_choix_sups.index(sup1_def))
                afficher_prix_indicatif(supplement_1)
                supplement_2 = st.selectbox("Supplément 2", options=liste_choix_sups, index=liste_choix_sups.index(sup2_def))
                afficher_prix_indicatif(supplement_2)
            with c_sup2:
                supplement_3 = st.selectbox("Supplément 3", options=liste_choix_sups, index=liste_choix_sups.index(sup3_def))
                afficher_prix_indicatif(supplement_3)
                supplement_4 = st.selectbox("Supplément 4", options=liste_choix_sups, index=liste_choix_sups.index(sup4_def))
                afficher_prix_indicatif(supplement_4)

            # Affichage dynamique du cumul pour la clarté du devis d'atelier
            total_sups = sum([PRIX_SUPPLEMENTS.get(s, 0.0) for s in [supplement_1, supplement_2, supplement_3, supplement_4]])
            if total_sups > 0:
                st.info(f"📊 **Sous-total suppléments pour ce livre :** {total_sups:.2f} €")

            st.write("---")
            if st.button("💾 Valider l'enregistrement", type="primary", use_container_width=True):
                donnees_fiche = {
                    "nom_client": nom_client_valide, "numero_train": numero_train, "numero_livre": num_livre_en_cours,
                    "nature_doc": nature_doc, "text_doc": text_doc, "option_autre": option_autre, "repro_scanne": repro_scanne, "repro_report": repro_report,
                    "hauteur": hauteur, "largeur": largeur, "epaisseur": epaisseur, "ne_pas_rogner": ne_pas_rogner, "traitement": traitement, "type_reliure": type_reliure, "type_couture": type_couture,
                    "agraphes": agraphes, "nombre_cahiers": nombre_cahiers, "sans_titrage": sans_titrage, "titrage_sens": titrage_sens, "lignes_sup": lignes_sup, "titrage_couleur": titrage_couleur, "police": police, "type_toile": type_toile, "couleur": couleur,
                    "cocher_piece_titre": cocher_piece_titre, "couleur_pieces_toile": couleur_pieces_toile, "marquage_pieces": marquage_pieces, "hauteur_maquette": hauteur_maquette,
                    "supplement_1": "" if supplement_1 == "-- Aucun --" else supplement_1, 
                    "supplement_2": "" if supplement_2 == "-- Aucun --" else supplement_2, 
                    "supplement_3": "" if supplement_3 == "-- Aucun --" else supplement_3, 
                    "supplement_4": "" if supplement_4 == "-- Aucun --" else supplement_4
                }
                enregistrer_ou_mettre_a_jour_livre(donnees_fiche)
                st.success("Données enregistrées avec succès sur Supabase !")
                if "livre_selectionne" in st.session_state: del st.session_state.livre_selectionne
                st.rerun()

        with col_visualisation:
            st.header("📊 Suivi en direct du Train")
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
            else: 
                st.info("Aucun livre encore enregistré dans ce Train.")
