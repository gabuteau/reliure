import streamlit as st
import psycopg2
import pandas as pd

def obtenir_connexion():
    return psycopg2.connect(st.secrets["PG_URL"])

FORMATS_COLONNES = ["115 x 185 (In 12)", "130 x 200 (In 8° écu)", "160 x 245 (In 8° raisin)", "175 x 270 (In 8° jésus)", "245 x 320 (In 4° raisin)", "270 x 350 (In 4° jésus)", "280 x 440 (Folio carré)", "320 x 490 (Folio raisin)", "350 x 540 (Folio jésus)", "440 x 600 (Grand folio)", "Plano A", "Plano B"]

TARIFS_INITIALISATION = {
    "Pièce de titre": 5.05, "Sous titre": 7.01, "Titrage main": 9.83, "Titre caractère latin": 9.83, "Titre autre caractère": 9.83, "Griffe": 2.24,
    "Plats conservés": 12.52, "Onglets": 0.92, "Doublage japon": 6.81, "Charnières toile": 1.66, "Conservation de gardes": 12.70, "Couture sur nerfs": 18.22,
    "Couvrure sur nerf": 9.85, "Filets fleurons": 1.66, "Plaçure": 1.66, "Sup ouvrage déjà relié": 12.70, "Plaçure intercalaires": 1.12, "Doublage couverture": 3.19,
    "Montage de couverture": 2.24, "Fonds de cahiers": 1.23, "Pose antivol": 0.43, "Désacidification": 0.00, "Désinfection": 0.00, "Charnière cuir": 0.00,
    "Enlever agrafes": 0.00, "Couture manuelle sur rubans": 0.00
}

def lister_tous_les_clients():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM clients ORDER BY nom ASC")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients

def dupliquer_grille_standard_pour_client(nom_client):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM tarifs_clients WHERE nom_client = %s LIMIT 1", (nom_client,))
    if not cursor.fetchone():
        for des, mt in TARIFS_INITIALISATION.items():
            for fmt in FORMATS_COLONNES:
                cursor.execute("INSERT INTO tarifs_clients (nom_client, designation, format_nom, montant) VALUES (%s, %s, %s, %s)", (nom_client, des, fmt, mt))
        conn.commit()
    conn.close()

st.set_page_config(page_title="Grilles Tarifaires", layout="wide")
st.title("🏷️ Personnalisation des tarifs par Client")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.info("Créez d'abord un client pour modifier sa grille tarifaire.")
else:
    client_tarif_sel = st.selectbox("Sélectionner un client pour ajuster ses prix :", options=liste_clients_existants)
    dupliquer_grille_standard_pour_client(client_tarif_sel)
    
    conn = obtenir_connexion()
    df_tarifs = pd.read_sql_query("SELECT designation as \"Désignation\", format_nom, montant FROM tarifs_clients WHERE nom_client = %s", conn, params=(client_tarif_sel,))
    conn.close()
    
    if not df_tarifs.empty:
        df_pivot = df_tarifs.pivot(index="Désignation", columns="format_nom", values="montant")
        df_pivot = df_pivot.reindex(columns=FORMATS_COLONNES)
        st.markdown("💡 *Modifiez directement les montants dans les cases ci-dessous, puis validez.*")
        df_edite = st.data_editor(df_pivot, use_container_width=True, num_rows="fixed")
        
        if st.button("💾 Enregistrer la nouvelle grille"):
            conn = obtenir_connexion()
            cursor = conn.cursor()
            for designation, row in df_edite.iterrows():
                for format_nom, montant in row.items():
                    cursor.execute("UPDATE tarifs_clients SET montant = %s WHERE nom_client = %s AND designation = %s AND format_nom = %s", (float(montant), client_tarif_sel, designation, format_nom))
            conn.commit()
            conn.close()
            st.success("Grille tarifaire mise à jour sur Supabase !")
