import streamlit as st
from supabase import create_client
from datetime import datetime

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def charger_grille_tarifs():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("tarifs_base").select("*").order("code_prestation").execute()
        return reponse.data
    except Exception as e:
        st.error(f"Erreur lors du chargement des tarifs : {e}")
        return []

def mettre_a_jour_tarif(id_tarif, nouveau_prix):
    supabase = obtenir_client_supabase()
    try:
        supabase.table("tarifs_base").update({
            "prix_unitaire": nouveau_prix,
            "derniere_modification": datetime.now().isoformat()
        }).eq("id", id_tarif).execute()
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
    # Utilisation du composant natif data_editor de Streamlit pour une modification fluide style Excel
    st.subheader("Grille des prix actuels")
    
    # Configuration des colonnes pour bloquer la modification des codes/libellés et autoriser uniquement le prix
    configuration_colonnes = {
        "id": None,  # Masque l'ID
        "code_prestation": st.column_config.TextColumn("Code Système", disabled=True),
        "libelle": st.column_config.TextColumn("Prestation / Tranche", disabled=True),
        "prix_unitaire": st.column_config.NumberColumn("Prix Unitaire (€)", min_value=0.0, format="%.2f €", required=True),
        "derniere_modification": st.column_config.DatetimeColumn("Dernière MAJ", disabled=True, format="DD/MM/YYYY HH:mm")
    }
    
    # Rendu de la table éditable
    donnees_editees = st.data_editor(
        tarifs,
        column_config=configuration_colonnes,
        use_container_width=True,
        hide_index=True
    )
    
    # Détection des changements et bouton d'enregistrement
    if st.button("💾 Enregistrer la nouvelle grille de tarifs", type="primary", use_container_width=True):
        changements_effectues = 0
        
        # Comparaison de l'ancien tableau avec le nouveau pour n'envoyer que les lignes modifiées
        for ligne_originale, ligne_modifiee in zip(tarifs, donnees_editees):
            if ligne_originale["prix_unitaire"] != ligne_modifiee["prix_unitaire"]:
                succes = mettre_a_jour_tarif(ligne_modifiee["id"], ligne_modifiee["prix_unitaire"])
                if succes:
                    changements_effectues += 1
        
        if changements_effectues > 0:
            st.success(f"🎉 Grille mise à jour ! {changements_effectues} tarif(s) modifié(s) avec succès.")
            st.rerun()
        else:
            st.info("Aucun changement de tarif n'a été détecté.")
else:
    st.warning("La table 'tarifs_base' est vide ou introuvable sur Supabase.")

