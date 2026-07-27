import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONNECTION SUPABASE ---
def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- CONFIGURATION STREAMLIT ---
st.set_page_config(
    page_title="Gestion des Toiles & Couleurs",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Référentiel des Toiles & Couleurs")
st.write("Gérez ici les types de toiles et les couleurs disponibles dans le formulaire de saisie des fiches.")
st.write("---")

supabase = obtenir_client_supabase()

# --- 1. FORMULAIRE D'AJOUT ---
st.subheader("➕ Ajouter une nouvelle déclinaison")

col_add1, col_add2, col_add3 = st.columns([2, 2, 1])

with col_add1:
    toiles_suggestions = ["Buckram", "Fantasia", "Métisse"]
    toile_saisie = st.selectbox("Type de toile", options=toiles_suggestions + ["-- Autre (Nouveau type) --"])
    if toile_saisie == "-- Autre (Nouveau type) --":
        type_toile_final = st.text_input("Saisir le nouveau type de toile", placeholder="Ex: Chagrin, Satin...")
    else:
        type_toile_final = toile_saisie

with col_add2:
    nouvelle_couleur = st.text_input("Nom de la couleur", placeholder="Ex: Bleu Marine, Bordeaux...")

with col_add3:
    st.write(" ")
    st.write(" ")
    if st.button("💾 Enregistrer", type="primary", use_container_width=True):
        if type_toile_final and nouvelle_couleur:
            try:
                supabase.table("referentiel_toiles").insert({
                    "type_toile": type_toile_final.strip(),
                    "couleur": nouvelle_couleur.strip(),
                    "actif": True
                }).execute()
                st.success(f"✅ La couleur '{nouvelle_couleur.strip()}' a été ajoutée pour la toile '{type_toile_final.strip()}'.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur d'enregistrement (ce couple Toile/Couleur existe peut-être déjà) : {e}")
        else:
            st.warning("Veuillez renseigner le type de toile et la couleur.")

st.write("---")

# --- 2. LISTAGE, MODIFICATION ET SUPPRESSION ---
st.subheader("📋 Liste des Couleurs par Toile")

try:
    reponse = supabase.table("referentiel_toiles").select("*").order("type_toile").order("couleur").execute()
    donnees = reponse.data

    if donnees:
        df = pd.DataFrame(donnees)

        # Filtre de recherche
        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            types_existants = sorted(list(set(df["type_toile"])))
            filtre_toile = st.selectbox("🔍 Filtrer par type de toile :", ["-- Tous les types --"] + types_existants)

        if filtre_toile != "-- Tous les types --":
            df_affiche = df[df["type_toile"] == filtre_toile]
        else:
            df_affiche = df

        st.write("")
        
        # En-tête du tableau d'édition
        col_h1, col_h2, col_h3, col_h4 = st.columns([2.5, 2.5, 1.5, 1.5])
        with col_h1: st.markdown("**Type de Toile**")
        with col_h2: st.markdown("**Couleur**")
        with col_h3: st.markdown("**Mise à jour**")
        with col_h4: st.markdown("**Action**")
        st.write("---")

        # Lignes d'édition dynamique
        for idx, row in df_affiche.iterrows():
            c1, c2, c3, c4 = st.columns([2.5, 2.5, 1.5, 1.5])
            
            with c1:
                st.write(f"**{row['type_toile']}**")
            
            with c2:
                # Champ modifiable pour le nom de la couleur
                couleur_modifiee = st.text_input(
                    label=f"couleur_{row['id']}", 
                    value=row['couleur'], 
                    key=f"input_couleur_{row['id']}", 
                    label_visibility="collapsed"
                )
            
            with c3:
                # Bouton de modification
                if couleur_modifiee != row['couleur']:
                    if st.button("✏️ Valider", key=f"btn_edit_{row['id']}", type="primary", use_container_width=True):
                        try:
                            supabase.table("referentiel_toiles").update({
                                "couleur": couleur_modifiee.strip()
                            }).eq("id", row['id']).execute()
                            st.success("Modifié !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                else:
                    st.caption("Inchangé")

            with c4:
                # Bouton de suppression
                if st.button("🗑️ Supprimer", key=f"btn_del_{row['id']}", use_container_width=True):
                    try:
                        supabase.table("referentiel_toiles").delete().eq("id", row['id']).execute()
                        st.success("Supprimé !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur de suppression : {e}")

    else:
        st.info("Aucune couleur n'est enregistrée dans la base de données.")

except Exception as e:
    st.error(f"Impossible de charger le référentiel des toiles : {e}")

st.write("---")
if st.button("⬅️ Retour au Menu principal"):
    st.switch_page("app.py")
