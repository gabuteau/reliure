import streamlit as st
from supabase import create_client
from datetime import datetime

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def charger_grille_tarifs():
    supabase = obtenir_client_supabase()
    try:
        # On retire l'order-by pour éviter l'erreur de colonne inexistante
        reponse = supabase.table("tarifs_clients").select("*").execute()
        return reponse.data
    except Exception as e:
        st.error(f"Erreur lors du chargement des tarifs : {e}")
        return []

def mettre_a_jour_tarif(id_tarif, champ_prix, nouveau_prix):
    supabase = obtenir_client_supabase()
    donnees_maj = {champ_prix: nouveau_prix}
    
    # On ajoute la date de mise à jour uniquement si la colonne existe (optionnel)
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

tarifs = charger_grille_tarifs()

if tarifs:
    st.subheader("Grille des prix actuels")
    
    # Détection dynamique du nom de la colonne de prix (souvent 'prix', 'montant', ou 'prix_unitaire')
    colonnes_disponibles = tarifs[0].keys()
    champ_prix = next((c for c in ["prix_unitaire", "prix", "montant", "valeur"] if c in colonnes_disponibles), None)
    champ_libelle = next((c for c in ["libelle", "designation", "nom", "prestation"] if c in colonnes_disponibles), None)
    
    if not champ_prix:
        st.error(f"Impossible de trouver la colonne du prix parmi : {list(colonnes_disponibles)}")
        st.stop()

    # Configuration dynamique des colonnes pour l'éditeur
    configuration_colonnes = {
        "id": None,  # Masque l'identifiant
    }
    
    for col in colonnes_disponibles:
        if col == champ_prix:
            configuration_colonnes[col] = st.column_config.NumberColumn("Prix (€)", min_value=0.0, format="%.2f €", required=True)
        elif col == champ_libelle:
            configuration_colonnes[col] = st.column_config.TextColumn("Prestation", disabled=True)
        elif col != "id":
            configuration_colonnes[col] = st.column_config.TextColumn(col, disabled=True)
            
    donnees_editees = st.data_editor(
        tarifs,
        column_config=configuration_colonnes,
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("💾 Enregistrer la nouvelle grille de tarifs", type="primary", use_container_width=True):
        changements_effectues = 0
        
        for ligne_originale, ligne_modifiee in zip(tarifs, donnees_editees):
            if ligne_originale[champ_prix] != ligne_modifiee[champ_prix]:
                succes = mettre_a_jour_tarif(ligne_modifiee["id"], champ_prix, ligne_modifiee[champ_prix])
                if succes:
                    changements_effectues += 1
        
        if changements_effectues > 0:
            st.success(f"🎉 Grille mise à jour ! {changements_effectues} tarif(s) modifié(s).")
            st.rerun()
        else:
            st.info("Aucun changement de tarif n'a été détecté.")
else:
    st.warning("La table 'tarifs_clients' ne renvoie aucune donnée.")
