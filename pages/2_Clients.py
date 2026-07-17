import streamlit as st
import sqlite3

DB_FILE = "base_reliure_v2.db"

def lister_tous_les_clients():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM clients ORDER BY nom ASC")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients

def recuperer_fiche_client(nom_client):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE nom = ?", (nom_client,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def enregistrer_client(nom, adresse, contact, notes):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (nom, adresse, telephone, email, contact_nom, notes) VALUES (?, ?, '', '', ?, ?) ON CONFLICT(nom) DO UPDATE SET adresse=excluded.adresse, contact_nom=excluded.contact_nom, notes=excluded.notes", (nom, adresse, contact, notes))
    conn.commit()
    conn.close()

def supprimer_client_bdd(nom_client):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarifs_clients WHERE nom_client = ?", (nom_client,))
    cursor.execute("DELETE FROM fiches_livres WHERE nom_client = ?", (nom_client,))
    cursor.execute("DELETE FROM clients WHERE nom = ?", (nom_client,))
    conn.commit()
    conn.close()

st.set_page_config(page_title="Gestion des Clients", layout="wide")
st.title("🏢 Gestion de l'Annuaire des Clients")

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
            st.success(f"Client '{nc_nom}' ajouté avec succès.")
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
                    st.success("Fiche client mise à jour.")
                    st.rerun()
            
            st.write("---")
            st.markdown("#### 🚨 Zone de danger")
            st.error("⚠️ **Attention :** La suppression d'un client est définitive et irréversible. Cela effacera complètement sa fiche d'annuaire, sa grille de tarifs personnalisés ainsi que l'intégralité de ses trains de livres d'atelier.")
            
            if f"confirm_delete_{fiche['nom']}" not in st.session_state:
                st.session_state[f"confirm_delete_{fiche['nom']}"] = False
            
            if not st.session_state[f"confirm_delete_{fiche['nom']}"]:
                if st.button(f"❌ Demander la suppression globale de {fiche['nom']}"):
                    st.session_state[f"confirm_delete_{fiche['nom']}"] = True
                    st.rerun()
            else:
                st.warning(f"Êtes-vous absolument sûr de vouloir détruire {fiche['nom']} ainsi que tous ses tarifs et historiques de trains ?")
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    if st.button("✔️ OUI, CONFIRMER LA SUPPRESSION DÉFINITIVE"):
                        supprimer_client_bdd(fiche["nom"])
                        st.session_state[f"confirm_delete_{fiche['nom']}"] = False
                        st.rerun()
                with col_del2:
                    if st.button("🔄 Annuler l'action"):
                        st.session_state[f"confirm_delete_{fiche['nom']}"] = False
                        st.rerun()