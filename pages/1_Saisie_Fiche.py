import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def lister_tous_les_clients():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("clients").select("nom").order("nom").execute()
        return [row["nom"] for row in reponse.data]
    except Exception:
        return []

def charger_types_toile_supabase():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("referentiel_toiles").select("type_toile").execute()
        types = sorted(list(set([row["type_toile"] for row in reponse.data])))
        return types if types else ["Buckram", "Fantasia", "Métisse"]
    except Exception:
        return ["Buckram", "Fantasia", "Métisse"]

def charger_couleurs_par_toile_supabase(type_toile):
    supabase = obtenir_client_supabase()
    try:
        reponse = (
            supabase.table("referentiel_toiles")
            .select("couleur")
            .eq("type_toile", type_toile)
            .order("couleur")
            .execute()
        )
        couleurs = [row["couleur"] for row in reponse.data]
        return couleurs if couleurs else ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]
    except Exception:
        return ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]

def enregistrer_fiche_livre(donnees):
    supabase = obtenir_client_supabase()
    try:
        supabase.table("fiches_livres").insert(donnees).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")
        return False

st.set_page_config(page_title="Saisie des Fiches Livres", layout="wide")
st.title("📚 Saisie des Fiches Livres")

liste_clients = lister_tous_les_clients()

if not liste_clients:
    st.warning("⚠️ Veillez à créer au moins un client dans l'annuaire avant de saisir des fiches.")
else:
    with st.form("form_saisie_fiche", clear_on_submit=False):
        st.subheader("1. Informations Générales")
        col1, col2, col3 = st.columns(3)
        with col1:
            sf_client = st.selectbox("Client référent *", options=liste_clients)
        with col2:
            sf_train = st.text_input("N° de Train *", placeholder="Ex: T2026-01").strip()
        with col3:
            sf_livre = st.number_input("N° du Livre *", min_value=1, value=1, step=1)

        st.write("---")
        st.subheader("2. Dimensions du Livre (mm)")
        cdim1, cdim2, cdim3 = st.columns(3)
        with cdim1:
            sf_hauteur = st.number_input("Hauteur (mm)", min_value=10, max_value=1000, value=220, step=1)
        with cdim2:
            sf_largeur = st.number_input("Largeur (mm)", min_value=10, max_value=1000, value=160, step=1)
        with cdim3:
            sf_epaisseur = st.number_input("Épaisseur / Dos (mm)", min_value=2, max_value=500, value=20, step=1)

        st.write("---")
        st.subheader("3. Reliure & Titrage")
        ctoi1, ctoi2, ctoi3, ctoi4 = st.columns(4)

        types_toiles = charger_types_toile_supabase()
        with ctoi1:
            sf_type_toile = st.selectbox("Type de toile", options=types_toiles)

        couleurs_dispos = charger_couleurs_par_toile_supabase(sf_type_toile)
        with ctoi2:
            sf_couleur_toile = st.selectbox("Couleur de la toile", options=couleurs_dispos)

        with ctoi3:
            sf_marquage = st.selectbox("Couleur du marquage", options=["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"], index=0)

        with ctoi4:
            # OPTION PAR DÉFAUT : "Classique" (Index 0)
            sf_sens_titrage = st.selectbox(
                "Sens du titrage par défaut",
                options=["Classique", "Long"],
                index=0,
                help="Classique = horizontal | Long = vertical de haut en bas"
            )

        st.write("---")
        st.subheader("4. Pièces de Titre (Optionnel)")
        cp1, cp2, cp3 = st.columns(3)
        with cp1:
            sf_has_piece = st.checkbox("Activer une pièce de titre")
        with cp2:
            sf_piece_couleur = st.selectbox("Couleur de la pièce", options=["Rouge", "Noir", "Bleu", "Marron", "Vert"], index=0, disabled=not sf_has_piece)
        with cp3:
            sf_piece_marquage = st.selectbox("Marquage sur pièce", options=["OR", "ARGENT", "BLANC", "NOIR"], index=0, disabled=not sf_has_piece)

        st.write("---")
        bouton_validation = st.form_submit_button("💾 Valider et enregistrer la fiche", type="primary", use_container_width=True)

    if bouton_validation:
        if not sf_train:
            st.error("Veuillez renseigner le N° de train.")
        else:
            donnees_fiche = {
                "nom_client": sf_client,
                "numero_train": sf_train,
                "numero_livre": int(sf_livre),
                "hauteur": int(sf_hauteur),
                "largeur": int(sf_largeur),
                "epaisseur": int(sf_epaisseur),
                "type_toile": sf_type_toile,
                "couleur": sf_couleur_toile,
                "titrage_couleur": sf_marquage,
                "sens_titrage": sf_sens_titrage,
                "cocher_piece_titre": sf_has_piece,
                "couleur_pieces_toile": sf_piece_couleur if sf_has_piece else "",
                "marquage_pieces": sf_piece_marquage if sf_has_piece else "",
                "nombre_pieces_titre": 1 if sf_has_piece else 0,
                "date_creation": str(datetime.now().date())
            }

            if enregistrer_fiche_livre(donnees_fiche):
                st.success(f"✅ Fiche livre N°{sf_livre} (Train {sf_train} - {sf_client}) enregistrée avec le sens '{sf_sens_titrage}'.")
