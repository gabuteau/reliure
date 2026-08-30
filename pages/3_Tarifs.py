import streamlit as st
from supabase import create_client
import pandas as pd

@st.cache_resource
def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

FORMATS_COLONNES = [
    "115 x 185 (In 12)", "130 x 200 (In 8° écu)", "160 x 245 (In 8° raisin)",
    "175 x 270 (In 8° jésus)", "245 x 320 (In 4° raisin)", "270 x 350 (In 4° jésus)",
    "280 x 440 (Folio carré)", "320 x 490 (Folio raisin)", "350 x 540 (Folio jésus)",
    "440 x 600 (Grand folio)", "Plano A", "Plano B"
]

TARIFS_INITIALISATION = {
    "Pièce de titre": 5.05, "Sous titre": 7.01, "Titrage main": 9.83, "Titre caractère latin": 9.83,
    "Titre autre caractère": 9.83, "Griffe": 2.24, "Plats conservés": 12.52, "Onglets": 0.92,
    "Doublage japon": 6.81, "Charnières toile": 1.66, "Conservation de gardes": 12.70, "Couture sur nerfs": 18.22,
    "Couvrure sur nerf": 9.85, "Filets fleurons": 1.66, "Plaçure": 1.66, "Sup ouvrage déjà relié": 12.70,
    "Plaçure intercalaires": 1.12, "Doublage couverture": 3.19, "Montage de couverture": 2.24,
    "Fonds de cahiers": 1.23, "Pose antivol": 0.43, "Désacidification": 0.00, "Désinfection": 0.00,
    "Charnière cuir": 0.00, "Enlever agrafes": 0.00, "Couture manuelle sur rubans": 0.00
}

def lister_tous_les_clients():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("clients").select("nom").order("nom").execute()
        return [row["nom"] for row in reponse.data]
    except Exception as e:
        st.error(f"Erreur lors de la récupération des clients : {e}")
        return []

def dupliquer_grille_standard_pour_client(nom_client):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("tarifs_clients").select("designation").eq("nom_client", nom_client).limit(1).execute()
    if not reponse.data:
        lots_insertions = [
            {"nom_client": nom_client, "designation": des, "format_nom": fmt, "montant": mt}
            for des, mt in TARIFS_INITIALISATION.items()
            for fmt in FORMATS_COLONNES
        ]
        supabase.table("tarifs_clients").insert(lots_insertions).execute()

def ajouter_designation(nom_client, designation_nom, prix_defaut=0.0):
    supabase = obtenir_client_supabase()
    
    existante = (
        supabase.table("tarifs_clients")
        .select("designation")
        .eq("nom_client", nom_client)
        .eq("designation", designation_nom)
        .limit(1)
        .execute()
    )
    
    if existante.data:
        st.warning(f"La désignation « {designation_nom} » existe déjà pour ce client.")
        return False

    lignes_a_inserer = [
        {
            "nom_client": nom_client,
            "designation": designation_nom,
            "format_nom": fmt,
            "montant": round(float(prix_defaut), 2)
        }
        for fmt in FORMATS_COLONNES
    ]
    
    supabase.table("tarifs_clients").insert(lignes_a_inserer).execute()
    return True

def supprimer_designation(nom_client, designation_nom):
    supabase = obtenir_client_supabase()
    (
        supabase.table("tarifs_clients")
        .delete()
        .eq("nom_client", nom_client)
        .eq("designation", designation_nom)
        .execute()
    )

@st.dialog("Confirmer la suppression")
def dialogue_confirmation_suppression(nom_client, designation_nom):
    st.write(f"Êtes-vous sûr de vouloir supprimer la prestation **« {designation_nom} »** pour le client **{nom_client}** ?")
    st.caption("Cette action supprimera tous les tarifs associés à cette ligne pour l'ensemble des formats.")
    
    col_confirm, col_annul = st.columns(2)
    with col_confirm:
        if st.button("Oui, supprimer", type="primary", use_container_width=True):
            supprimer_designation(nom_client, designation_nom)
            st.success(f"Désignation « {designation_nom} » supprimée avec succès.")
            st.rerun()
    with col_annul:
        if st.button("Annuler", use_container_width=True):
            st.rerun()

st.set_page_config(page_title="Grilles Tarifaires", layout="wide")
st.title("🏷️ Personnalisation des tarifs par Client (Vue Matrice)")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.info("Créez d'abord un client pour modifier sa grille tarifaire.")
else:
    client_tarif_sel = st.selectbox("Sélectionner un client pour ajuster ses prix :", options=liste_clients_existants)
    dupliquer_grille_standard_pour_client(client_tarif_sel)

    # Récupération des données du client
    supabase = obtenir_client_supabase()
    reponse_tarifs = (
        supabase.table("tarifs_clients")
        .select("designation, format_nom, montant")
        .eq("nom_client", client_tarif_sel)
        .execute()
    )
    
    if reponse_tarifs.data:
        df_tarifs = pd.DataFrame(reponse_tarifs.data)
        
        # Liste triée des désignations actuelles du client
        designations_actuelles = sorted(df_tarifs["designation"].unique().tolist())

        # --- Panneau de gestion des désignations (Ajout & Suppression) ---
        with st.expander("⚙️ Gérer les lignes de prestations (Ajouter / Supprimer)", expanded=False):
            tab_ajout, tab_suppr = st.tabs(["➕ Ajouter une désignation", "🗑️ Supprimer une désignation"])
            
            with tab_ajout:
                with st.form("form_nouvelle_designation", clear_on_submit=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        nouvelle_desig = st.text_input("Nom de la désignation :", placeholder="ex: Dorure à la feuille")
                    with col2:
                        prix_initial = st.number_input("Tarif par défaut (€) :", min_value=0.0, value=0.0, step=0.5, format="%.2f")
                    
                    bouton_ajouter = st.form_submit_button("Ajouter à la grille", use_container_width=True)
                    
                    if bouton_ajouter:
                        nom_nettoye = nouvelle_desig.strip()
                        if nom_nettoye:
                            if ajouter_designation(client_tarif_sel, nom_nettoye, prix_initial):
                                st.success(f"Désignation « {nom_nettoye} » ajoutée pour tous les formats !")
                                st.rerun()
                        else:
                            st.error("Le nom de la désignation ne peut pas être vide.")

            with tab_suppr:
                if designations_actuelles:
                    col_sel, col_btn = st.columns([3, 1])
                    with col_sel:
                        desig_a_supprimer = st.selectbox("Sélectionner la désignation à retirer :", options=designations_actuelles)
                    with col_btn:
                        st.write("") # Alignement vertical
                        st.write("")
                        if st.button("Supprimer la ligne", type="secondary", use_container_width=True):
                            dialogue_confirmation_suppression(client_tarif_sel, desig_a_supprimer)
                else:
                    st.info("Aucune prestation disponible à supprimer.")

        # --- Matrice pivotée et éditeur ---
        df_pivot = df_tarifs.pivot(index="designation", columns="format_nom", values="montant")
        df_pivot = df_pivot.reindex(columns=FORMATS_COLONNES)
        
        st.markdown("💡 *Modifiez directement les montants dans les cases ci-dessous, puis validez.*")
        df_edite = st.data_editor(df_pivot, use_container_width=True, num_rows="fixed")
        
        if st.button("💾 Enregistrer la nouvelle grille", type="primary"):
            enregistrements_a_maj = []
            
            for designation, row in df_edite.iterrows():
                for format_nom, nouveau_montant in row.items():
                    valeur_origine = df_pivot.loc[designation, format_nom]
                    
                    if round(float(nouveau_montant), 2) != round(float(valeur_origine), 2):
                        enregistrements_a_maj.append({
                            "nom_client": client_tarif_sel,
                            "designation": designation,
                            "format_nom": format_nom,
                            "montant": round(float(nouveau_montant), 2)
                        })
            
            if enregistrements_a_maj:
                with st.spinner("Enregistrement des modifications en cours..."):
                    try:
                        supabase.table("tarifs_clients").upsert(enregistrements_a_maj).execute()
                        st.success(f"🎉 Grille tarifaire mise à jour ! {len(enregistrements_a_maj)} prix modifié(s).")
                        st.rerun()
                    except Exception:
                        for record in enregistrements_a_maj:
                            supabase.table("tarifs_clients")\
                                .update({"montant": record["montant"]})\
                                .eq("nom_client", record["nom_client"])\
                                .eq("designation", record["designation"])\
                                .eq("format_nom", record["format_nom"])\
                                .execute()
                        st.success(f"🎉 Grille tarifaire mise à jour ! {len(enregistrements_a_maj)} prix modifié(s).")
                        st.rerun()
            else:
                st.info("Aucune modification détectée.")
