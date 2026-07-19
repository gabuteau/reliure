import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

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
st.write("Modifiez les prix appliqués aux clients pour les fiches de livres.")

tarifs_bruts = charger_grille_tarifs()

if tarifs_bruts:
    # Conversion en DataFrame pour faciliter le filtrage
    df_tarifs = pd.DataFrame(tarifs_bruts)
    
    # Détection dynamique des colonnes
    colonnes_disponibles = df_tarifs.columns.tolist()
    champ_prix = next((c for c in ["prix_unitaire", "prix", "montant", "valeur"] if c in colonnes_disponibles), None)
    champ_libelle = next((c for c in ["libelle", "designation", "nom", "prestation"] if c in colonnes_disponibles), None)
    champ_client = next((c for c in ["nom_client", "client"] if c in colonnes_disponibles), None)
    
    if not champ_prix:
        st.error(f"Impossible de trouver la colonne du prix parmi : {colonnes_disponibles}")
        st.stop()

    # --- AJOUT DU FILTRE PAR CLIENT ---
    st.write("### 🔍 Choisir un client pour afficher sa grille")
    
    # On récupère la liste unique des clients présents dans la table tarif
    if champ_client and champ_client in df_tarifs.columns:
        liste_clients = sorted(df_tarifs[champ_client].unique().tolist())
        
        # On essaie de pré-sélectionner Invelac par défaut s'il est dans la liste
        index_defaut = liste_clients.index("Invelac") if "Invelac" in liste_clients else 0
        
        client_selectionne = st.selectbox(
            "Filtrer par client :", 
            options=["Tous les clients"] + liste_clients,
            index=index_defaut + 1 if "Invelac" in liste_clients else 0
        )
        
        # Application du filtre sur le DataFrame
        if client_selectionne != "Tous les clients":
            df_filtré = df_tarifs[df_tarifs[champ_client] == client_selectionne].copy()
        else:
            df_filtré = df_tarifs.copy()
    else:
        df_filtré = df_tarifs.copy()
        st.warning("Impossible de filtrer : colonne client introuvable dans la table.")

    st.subheader(f"Grille des prix actuels — {client_selectionne}")

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
            
    # Affichage du tableau filtré
    df_edite = st.data_editor(
        df_filtré,
        column_config=configuration_colonnes,
        use_container_width=True,
        hide_index=True,
        key="editeur_tarifs_filtres"
    )
    
    if st.button("💾 Enregistrer la nouvelle grille de tarifs", type="primary", use_container_width=True):
        changements_effectues = 0
        
        # On compare les lignes du tableau filtré avant et après édition
        for (_, ligne_originale), (_, ligne_modifiee) in zip(df_filtré.iterrows(), df_edite.iterrows()):
            prix_orig = float(ligne_originale[champ_prix]) if ligne_originale[champ_prix] is not None else 0.0
            prix_mod = float(ligne_modifiee[champ_prix]) if ligne_modifiee[champ_prix] is not None else 0.0
            
            if prix_orig != prix_mod:
                succes = mettre_a_jour_tarif(ligne_modifiee["id"], champ_prix, prix_mod)
                if succes:
                    changements_effectues += 1
        
        if changements_effectues > 0:
            st.success(f"🎉 Grille mise à jour ! {changements_effectues} tarif(s) modifié(s) pour {client_selectionne}.")
            st.rerun()
        else:
            st.info("Aucun changement de tarif n'a été détecté.")
else:
    st.warning("La table 'tarifs_clients' ne renvoie aucune donnée.")
