import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd  # <-- Ajouté pour gérer les filtres de colonnes

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def charger_grille_tarifs():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("tarifs_clients").select("*").execute()
        return reponse.data
    except Exception as e:
        st.error(f"Erreur lors du chargement des tarifs : {e}")
        return []

def mettre_a_jour_tarif(id_tarif, champ_prix, nouveau_prix):
    supabase = obtenir_client_supabase()
    donnees_maj = {champ_prix: nouveau_prix}
    
    try:
        supabase.table("tarifs_clients").update(donnees_maj).eq("id", id_tarif).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour : {e}")
        return False

# Configuration de la page
st.set_page_config(page_title="Gestion des Tarifs", layout="centered")

st.title("⚙️ Administration — Grille Tarifaire")
st.write("Modifiez les prix de base appliqués lors de la saisie des nouvelles fiches de livres.")

tarifs_bruts = charger_grille_tarifs()

if tarifs_bruts:
    st.subheader("Grille des prix actuels")
    
    # --- CONVERSION EN DATAFRAME POUR ACTIVER LES FILTRES D'ENTÊTE ---
    df_tarifs = pd.DataFrame(tarifs_bruts)
    
    # Détection dynamique du nom de la colonne de prix et libellé
    colonnes_disponibles = df_tarifs.columns.tolist()
    champ_prix = next((c for c in ["prix_unitaire", "prix", "montant", "valeur"] if c in colonnes_disponibles), None)
    champ_libelle = next((c for c in ["libelle", "designation", "nom", "prestation"] if c in colonnes_disponibles), None)
    champ_client = next((c for c in ["nom_client", "client"] if c in colonnes_disponibles), None)
    
    if not champ_prix:
        st.error(f"Impossible de trouver la colonne du prix parmi : {colonnes_disponibles}")
        st.stop()

    # Configuration dynamique des colonnes pour l'éditeur
    configuration_colonnes = {
        "id": None,  # Masque l'identifiant technique
    }
    
    for col in colonnes_disponibles:
        if col == champ_prix:
            configuration_colonnes[col] = st.column_config.NumberColumn("Prix (€)", min_value=0.0, format="%.2f €", required=True)
        elif col == champ_libelle:
            configuration_colonnes[col] = st.column_config.TextColumn("Prestation", disabled=True)
        elif col == champ_client:
            configuration_colonnes[col] = st.column_config.TextColumn("Client", disabled=True)
        elif col != "id":
            configuration_colonnes[col] = st.column_config.TextColumn(col, disabled=True)
            
    # L'utilisation du DataFrame ici active automatiquement la recherche et le tri par en-tête
    df_edite = st.data_editor(
        df_tarifs,
        column_config=configuration_colonnes,
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("💾 Enregistrer la nouvelle grille de tarifs", type="primary", use_container_width=True):
        changements_effectues = 0
        
        # Comparaison ligne par ligne entre le DataFrame original et le modifié
        for (_, ligne_originale), (_, ligne_modifiee) in zip(df_tarifs.iterrows(), df_edite.iterrows()):
            # On compare les prix (conversion en float pour éviter les faux doublons de type)
            prix_orig = float(ligne_originale[champ_prix]) if ligne_originale[champ_prix] is not None else 0.0
            prix_mod = float(ligne_modifiee[champ_prix]) if ligne_modifiee[champ_prix] is not None else 0.0
            
            if prix_orig != prix_mod:
                succes = mettre_a_jour_tarif(ligne_modifiee["id"], champ_prix, prix_mod)
                if succes:
                    changements_effectues += 1
        
        if changements_effectues > 0:
            st.success(f"🎉 Grille mise à jour ! {changements_effectues} tarif(s) modifié(s).")
            st.rerun()
        else:
            st.info("Aucun changement de tarif n'a été détecté.")
else:
    st.warning("La table 'tarifs_clients' ne renvoie aucune donnée.")
