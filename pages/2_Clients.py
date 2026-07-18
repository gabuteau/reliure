import streamlit as st
import psycopg2
import psycopg2.extras

def obtenir_connexion():
    return psycopg2.connect(st.secrets["PG_URL"])

def initialiser_tables_globales():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            nom TEXT PRIMARY KEY, adresse TEXT, telephone TEXT, email TEXT, contact_nom TEXT, notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarifs_clients (
            nom_client TEXT NOT NULL, designation TEXT NOT NULL, format_nom TEXT NOT NULL, montant REAL NOT NULL,
            PRIMARY KEY (nom_client, designation, format_nom)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_livres (
            nom_client TEXT NOT NULL, numero_train TEXT NOT NULL, numero_livre INTEGER NOT NULL,
            nature_doc TEXT, text_doc TEXT, option_autre TEXT, repro_scanne BOOLEAN, repro_report BOOLEAN,
            hauteur INTEGER, largeur INTEGER, epaisseur INTEGER, ne_pas_rogner BOOLEAN, traitement TEXT,
            type_reliure TEXT, type_couture TEXT, agraphes BOOLEAN, nombre_cahiers INTEGER, sans_titrage BOOLEAN,
            titrage_sens TEXT, lignes_sup INTEGER, titrage_couleur TEXT, police TEXT, type_toile TEXT, couleur TEXT,
            cocher_piece_titre BOOLEAN, couleur_pieces_toile TEXT, marquage_pieces TEXT, hauteur_maquette INTEGER,
            supplement_1 TEXT, supplement_2 TEXT, supplement_3 TEXT, supplement_4 TEXT,
            PRIMARY KEY (nom_client, numero_train, numero_livre)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS titrage_system3 (
            nom_client TEXT, numero_train TEXT, numero_livre INTEGER, date_saisie TEXT,
            toile TEXT, couleur_toile TEXT, piece_titre TEXT, couleur_piece TEXT,
            titrage_couleur TEXT, police TEXT, caractere TEXT, lignes_json TEXT,
            PRIMARY KEY (nom_client, numero_train, numero_livre)
        )
    """)
    conn.commit()
    conn.close()

def lister_tous_les_clients():
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM clients ORDER BY nom ASC")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients

def recuperer_fiche_client(nom_client):
    conn = obtenir_connexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM clients WHERE nom = %s", (nom_client,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def enregistrer_client(nom, adresse, contact, notes):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (nom, adresse, telephone, email, contact_nom, notes) 
        VALUES (%s, %s, '', '', %s, %s) 
        ON CONFLICT(nom) DO UPDATE SET adresse=EXCLUDED.adresse, contact_nom=EXCLUDED.contact_nom, notes=EXCLUDED.notes
    """, (nom, adresse, contact, notes))
    conn.commit()
    conn.close()

def supprimer_client_bdd(nom_client):
    conn = obtenir_connexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarifs_clients WHERE nom_client = %s", (nom_client,))
    cursor.execute("DELETE FROM fiches_livres WHERE nom_client = %s", (nom_client,))
    cursor.execute("DELETE FROM titrage_system3 WHERE nom_client = %s", (nom_client,))
    cursor.execute("DELETE FROM clients WHERE nom = %s", (nom_client,))
    conn.commit()
    conn.close()

st.set_page_config(page_title="Gestion des Clients", layout="wide")
st.title("🏢 Gestion de l'Annuaire des Clients")

initialiser_tables_globales()

action_client = st.radio("Action :", ["Sélectionner / Modifier un client", "➕ Créer un nouveau client"], horizontal=True)
st.write("---")

liste_clients_existants = lister_tous_les_clients()

if action_client == "➕ Créer un nouveau client":
    with st.form("form_creer_client"):
        nc_nom = st.text_input("Nom de l'établissement / Client *").strip()
        nc_contact = st.text_input("Nom du contact référent")
        nc_adresse = st.text_area("Adresse complète")
        nc_notes = st.text_area("Notes d'atelier spécifiques")
        if st.form_submit_button("💾 Enregistrer le nouveau client") and nc_nom:
            enregistrer_client(nc_nom, nc_adresse, nc_contact, nc_notes)
            st.success(f"Client '{nc_nom}' synchronisé sur Supabase.")
            st.rerun()
else:
    if liste_clients_existants:
        client_sel = st.selectbox("Choisir le client à gérer :", options=liste_clients_existants)
        fiche = recuperer_fiche_client(client_sel)
        if fiche:
            with st.form("form_modif_client"):
                mod_contact = st.text_input("Nom du contact référent", value=fiche["contact_nom"])
                mod_adresse = st.text_area("Adresse complète", value=fiche["adresse"])
                mod_notes = st.text_area("Notes d'atelier", value=fiche["notes"])
                if st.form_submit_button("💾 Sauvegarder les modifications"):
                    enregistrer_client(fiche["nom"], mod_adresse, mod_contact, mod_notes)
                    st.success("Fiche mise à jour.")
                    st.rerun()
            
            st.write("---")
            st.markdown("#### 🚨 Zone de danger")
            if f"confirm_delete_{fiche['nom']}" not in st.session_state:
                st.session_state[f"confirm_delete_{fiche['nom']}"] = False
            
            if not st.session_state[f"confirm_delete_{fiche['nom']}"]:
                if st.button(f"❌ Demander la suppression globale de {fiche['nom']}"):
                    st.session_state[f"confirm_delete_{fiche['nom']}"] = True
                    st.rerun()
            else:
                st.warning(f"Confirmer la suppression définitive de {fiche['nom']} sur le cloud ?")
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    if st.button("✔️ OUI, EFFACER TOUT"):
                        supprimer_client_bdd(fiche["nom"])
                        st.session_state[f"confirm_delete_{fiche['nom']}"] = False
                        st.rerun()
                with col_del2:
                    if st.button("🔄 Annuler"):
                        st.session_state[f"confirm_delete_{fiche['nom']}"] = False
                        st.rerun()
