import streamlit as st
from supabase import create_client
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

def mettre_a_jour_tarif(nom_client, designation, format_nom, champ_prix, nouveau_prix):
    supabase = obtenir_client_supabase()
    donnees_maj = {champ_prix: nouveau_prix}
    try:
        supabase.table("tarifs_clients")\
            .update(donnees_maj)\
            .eq("nom_client", nom_client)\
            .eq("designation", designation)\
            .eq("format_nom", format_nom)\
            .execute()
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
    df_tarifs = pd.DataFrame(tarifs_bruts)
    
    champ_client = "nom_client"
    champ_libelle = "designation"
    champ_format = "format_nom"
    champ_prix = "montant"

    st.write("### 🔍 Filtrer la grille tarifaire")
    col_filtre1, col_filtre2, col_filtre3 = st.columns(3)
    
    client_selectionne = "Tous les clients"
    if champ_client in df_tarifs.columns:
        liste_clients = sorted(df_tarifs[champ_client].dropna().unique().tolist())
        index_defaut = liste_clients.index("Invelac") if "Invelac" in liste_clients else 0
        
        with col_filtre1:
            client_selectionne = st.selectbox(
                "Client :", 
                options=["Tous les clients"] + liste_clients,
                index=index_defaut + 1 if "Invelac" in liste_clients else 0
            )
            
    if client_selectionne != "Tous les clients":
        df_etape1 = df_tarifs[df_tarifs[champ_client] == client_selectionne]
    else:
        df_etape1 = df_tarifs

    prestation_selectionnee = "Toutes les prestations"
    if champ_libelle in df_tarifs.columns:
        liste_prestations = sorted(df_etape1[champ_libelle].dropna().unique().tolist())
        
        with col_filtre2:
            prestation_selectionnee = st.selectbox(
                "Prestation :",
                options=["Toutes les prestations"] + liste_prestations
            )

    if prestation_selectionnee != "Toutes les prestations":
        df_etape2 = df_etape1[df_etape1[champ_libelle] == prestation_selectionnee]
    else:
        df_etape2 = df_etape1

    format_selectionne = "Tous les formats"
    if champ_format in df_tarifs.columns:
        liste_formats = sorted(df_etape2[champ_format].dropna().unique().tolist())
        
        with col_filtre3:
            format_selectionne = st.selectbox(
                "Format :",
                options=["Tous les formats"] + [str(f) for f in liste_formats]
            )

    if format_selectionne != "Tous les formats":
        df_filtré = df_etape2[df_etape2[champ_format].astype(str) == format_selectionne].copy()
    else:
        df_filtré = df_etape2.copy()

    st.write("---")
    st.subheader(f"📈 Grille affichée : {df_filtré.shape[0]} ligne(s) trouvée(s)")

    configuration_colonnes = {
        champ_prix: st.column_config.NumberColumn("Prix (€)", min_value=0.0, format="%.2f €", required=True),
        champ_libelle: st.column_config.TextColumn("Prestation", disabled=True),
        champ_client: st.column_config.TextColumn("Client", disabled=True),
        champ_format: st.column_config.TextColumn("Format", disabled=True)
    }
            
    st.data_editor(
        df_filtré,
        column_config=configuration_colonnes,
        use_container_width=True,
        hide_index=True,
        key="editeur_tarifs_composite"
    )
    
    if st.button("💾 Enregistrer la nouvelle grille de tarifs", type="primary", use_container_width=True):
        donnees_state = st.session_state["editeur_tarifs_composite"]
        lignes_modifiees = donnees_state.get("edited_rows", {})
        
        if lignes_modifiees:
            changements_effectues = 0
            
            for index_visuel, changements in lignes_modifiees.items():
                if champ_prix in changements:
                    nouveau_prix = changements[champ_prix]
                    ligne_originale = df_filtré.iloc[index_visuel]
                    
                    val_client = ligne_originale[champ_client]
                    val_prestation = ligne_originale[champ_libelle]
                    val_format = ligne_originale[champ_format]
                    
                    succes = mettre_a_jour_tarif(val_client, val_prestation, val_format, champ_prix, nouveau_prix)
                    if succes:
                        changements_effectues += 1
            
            if changements_effectues > 0:
                st.success(f"🎉 Grille mise à jour ! {changements_effectues} tarif(s) modifié(s).")
                st.rerun()
            else:
                st.info("Les modifications n'ont pas pu être enregistrées.")
        else:
            st.info("Aucun changement de tarif n'a été détecté.")
else:
    st.warning("La table 'tarifs_clients' ne renvoie aucune donnée.")
