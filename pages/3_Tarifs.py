import streamlit as st
from supabase import create_client
import pandas as pd

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

FORMATS_COLONNES = ["115 x 185 (In 12)", "130 x 200 (In 8° écu)", "160 x 245 (In 8° raisin)", "175 x 270 (In 8° jésus)", "245 x 320 (In 4° raisin)", "270 x 350 (In 4° jésus)", "280 x 440 (Folio carré)", "320 x 490 (Folio raisin)", "350 x 540 (Folio jésus)", "440 x 600 (Grand folio)", "Plano A", "Plano B"]

TARIFS_INITIALISATION = {
    "Pièce de titre": 5.05, "Sous titre": 7.01, "Titrage main": 9.83, "Titre caractère latin": 9.83, "Titre autre caractère": 9.83, "Griffe": 2.24,
    "Plats conservés": 12.52, "Onglets": 0.92, "Doublage japon": 6.81, "Charnières toile": 1.66, "Conservation de gardes": 12.70, "Couture sur nerfs": 18.22,
    "Couvrure sur nerf": 9.85, "Filets fleurons": 1.66, "Plaçure": 1.66, "Sup ouvrage déjà relié": 12.70, "Plaçure intercalaires": 1.12, "Doublage couverture": 3.19,
    "Montage de couverture": 2.24, "Fonds de cahiers": 1.23, "Pose antivol": 0.43, "Désacidification": 0.00, "Désinfection": 0.00, "Charnière cuir": 0.00,
    "Enlever agrafes": 0.00, "Couture manuelle sur rubans": 0.00
}

def lister_tous_les_clients():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("clients").select("nom").order("nom").execute()
        return [row["nom"] for row in reponse.data]
    except Exception:
        return []

def dupliquer_grille_standard_pour_client(nom_client):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("tarifs_clients").select("designation").eq("nom_client", nom_client).limit(1).execute()
    if not reponse.data:
        lots_insertions = []
        for des, mt in TARIFS_INITIALISATION.items():
            for fmt in FORMATS_COLONNES:
                lots_insertions.append({"nom_client": nom_client, "designation": des, "format_nom": fmt, "montant": mt})
        # Supabase gère l'insertion par paquets très bien en HTTP
        supabase.table("tarifs_clients").insert(lots_insertions).execute()

st.set_page_config(page_title="Grilles Tarifaires", layout="wide")
st.title("🏷️ Personnalisation des tarifs par Client")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.info("Créez d'abord un client pour modifier sa grille tarifaire.")
else:
    client_tarif_sel = st.selectbox("Sélectionner un client pour ajuster ses prix :", options=liste_clients_existants)
    dupliquer_grille_standard_pour_client(client_tarif_sel)
    
    supabase = obtenir_client_supabase()
    reponse_tarifs = supabase.table("tarifs_clients").select("designation, format_nom, montant").eq("nom_client", client_tarif_sel).execute()
    
    if reponse_tarifs.data:
        df_tarifs = pd.DataFrame(reponse_tarifs.data)
        df_tarifs.columns = ["Désignation", "format_nom", "montant"]
        df_pivot = df_tarifs.pivot(index="Désignation", columns="format_nom", values="montant")
        df_pivot = df_pivot.reindex(columns=FORMATS_COLONNES)
        st.markdown("💡 *Modifiez directement les montants dans les cases ci-dessous, puis validez.*")
        df_edite = st.data_editor(df_pivot, use_container_width=True, num_rows="fixed")
        
        if st.button("💾 Enregistrer la nouvelle grille"):
            lots_updates = []
            for designation, row in df_edite.iterrows():
                for format_nom, montant in row.items():
                    lots_updates.append({"nom_client": client_tarif_sel, "designation": designation, "format_nom": format_nom, "montant": float(montant)})
            supabase.table("tarifs_clients").upsert(lots_updates).execute()
            st.success("Grille tarifaire mise à jour via API Supabase !")
