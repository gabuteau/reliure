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
        supabase.table("tarifs_clients").insert(lots_insertions).execute()

st.set_page_config(page_title="Grilles Tarifaires", layout="wide")
st.title("🏷️ Personnalisation des tarifs par Client (Vue Matrice)")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.info("Créez d'abord un client pour modifier sa grille tarifaire.")
else:
    client_tarif_sel = st.selectbox("Sélectionner un client pour ajuster ses prix :", options=liste_clients_existants)
    dupliquer_grille_standard_pour_client(client_tarif_sel)
    
    supabase = obtenir_client_supabase()
    # Correction : On récupère l'id pour permettre des updates ciblés sans doublons
    reponse_tarifs = supabase.table("tarifs_clients").select("id, designation, format_nom, montant").eq("nom_client", client_tarif_sel).execute()
    
    if reponse_tarifs.data:
        df_tarifs = pd.DataFrame(reponse_tarifs.data)
        
        # On construit le tableau visuel pour l'utilisateur
        df_pivot = df_tarifs.pivot(index="designation", columns="format_nom", values="montant")
        df_pivot = df_pivot.reindex(columns=FORMATS_COLONNES)
        
        st.markdown("💡 *Modifiez directement les montants dans les cases ci-dessous, puis validez.*")
        df_edite = st.data_editor(df_pivot, use_container_width=True, num_rows="fixed")
        
        if st.button("💾 Enregistrer la nouvelle grille"):
            changements = 0
            # On compare cellule par cellule pour n'envoyer que les modifications réelles via requêtes ciblées
            for designation, row in df_edite.iterrows():
                for format_nom, nouveau_montant in row.items():
                    valeur_origine = df_pivot.loc[designation, format_nom]
                    
                    if float(nouveau_montant) != float(valeur_origine):
                        # Sécurisation : On applique un update précis sur le trio unique
                        supabase.table("tarifs_clients")\
                            .update({"montant": float(nouveau_montant)})\
                            .eq("nom_client", client_tarif_sel)\
                            .eq("designation", designation)\
                            .eq("format_nom", format_nom)\
                            .execute()
                        changements += 1
            
            if changements > 0:
                st.success(f"🎉 Grille tarifaire mise à jour ! {changements} prix modifié(s).")
                st.rerun()
            else:
                st.info("Aucune modification détectée.")
