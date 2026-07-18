import streamlit as st
from supabase import create_client

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def lister_tous_les_clients():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("clients").select("nom").order("nom").execute()
        return [row["nom"] for row in reponse.data]
    except Exception:
        return []

def recuperer_fiche_client(nom_client):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("clients").select("*").eq("nom", nom_client).execute()
    return reponse.data[0] if reponse.data else None

def enregistrer_client(nom, adresse, contact, notes):
    supabase = obtenir_client_supabase()
    # On n'envoie que les colonnes de base pour éviter tout conflit de structure
    donnees = {
        "nom": nom, 
        "adresse": adresse, 
        "contact_nom": contact, 
        "notes": notes
    }
    supabase.table("clients").upsert(donnees).execute()

def supprimer_client_globale(nom_client):
    supabase = obtenir_client_supabase()
    supabase.table("tarifs_clients").delete().eq("nom_client", nom_client).execute()
    supabase.table("fiches_livres").delete().eq("nom_client", nom_client).execute()
    supabase.table("titrage_system3").delete().eq("nom_client", nom_client).execute()
    supabase.table("clients").delete().eq("nom", nom_client).execute()

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
            st.success(f"Client '{nc_nom}' synchronisé via API Supabase.")
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
                        supprimer_client_globale(fiche["nom"])
                        st.session_state[f"confirm_delete_{fiche['nom']}"] = False
                        st.rerun()
                with col_del2:
                    if st.button("🔄 Annuler"):
                        st.session_state[f"confirm_delete_{fiche['nom']}"] = False
                        st.rerun()
