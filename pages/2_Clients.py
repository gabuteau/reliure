import streamlit as st
from supabase import create_client

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def lister_tous_les_clients():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("clients").select("*").order("nom").execute()
        return reponse.data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des clients : {e}")
        return []

def enregistrer_ou_mettre_a_jour_client(donnees):
    supabase = obtenir_client_supabase()
    try:
        supabase.table("clients").upsert(donnees).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement : {e}")
        return False

def supprimer_client(nom_client):
    supabase = obtenir_client_supabase()
    try:
        supabase.table("clients").delete().eq("nom", nom_client).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression : {e}")
        return False

st.set_page_config(page_title="Gestion des Clients", layout="wide")
st.title("👤 Fiches Clients & Paramétrage Griffe")

col1, col2 = st.columns([1.2, 0.8])

clients_existants = lister_tous_les_clients()
noms_clients = [c["nom"] for c in clients_existants]

with col1:
    st.subheader("Saisie / Modification d'un Client")
    
    choix_action = st.radio("Action", ["Nouveau client", "Modifier un client existant"], horizontal=True)
    
    client_edition = None
    if choix_action == "Modifier un client existant":
        if not noms_clients:
            st.info("Aucun client enregistré pour le moment.")
        else:
            nom_sel = st.selectbox("Sélectionner le client à modifier", options=noms_clients)
            client_edition = next((c for c in clients_existants if c["nom"] == nom_sel), None)

    st.write("---")
    
    # Formulaire client
    nom_client = st.text_input(
        "Nom du client *", 
        value=client_edition["nom"] if client_edition else "",
        disabled=(choix_action == "Modifier un client existant")
    )
    
    c_contact1, c_contact2 = st.columns(2)
    with c_contact1:
        telephone = st.text_input(
            "Téléphone", 
            value=client_edition.get("telephone", "") if client_edition and client_edition.get("telephone") else ""
        )
    with c_contact2:
        email = st.text_input(
            "E-mail", 
            value=client_edition.get("email", "") if client_edition and client_edition.get("email") else ""
        )
    
    st.write("---")
    st.subheader("🏷️ Configuration par défaut de la Griffe")
    
    griffe = st.text_area(
        "Texte de la griffe (ex: BIBLIOTHÈQUE / VILLE DE NEUVIC)", 
        value=client_edition.get("griffe", "") if client_edition and client_edition.get("griffe") else "",
        help="Laisse vide si le client n'a pas de griffe récurrente."
    )
    
    griffe_pos_mm = st.number_input(
        "Position par défaut depuis le bas (mm)", 
        min_value=0, 
        max_value=200, 
        value=int(client_edition.get("griffe_position_mm", 15)) if client_edition and client_edition.get("griffe_position_mm") else 15,
        step=1
    )

    st.write("---")
    if st.button("💾 Enregistrer le client", type="primary", use_container_width=True):
        if not nom_client.strip():
            st.error("Le nom du client est obligatoire.")
        else:
            donnees_client = {
                "nom": nom_client.strip(),
                "telephone": telephone.strip(),
                "email": email.strip(),
                "griffe": griffe.strip(),
                "griffe_position_mm": griffe_pos_mm
            }
            if enregistrer_ou_mettre_a_jour_client(donnees_client):
                st.success(f"Client **{nom_client}** enregistré avec succès !")
                st.rerun()

with col2:
    st.subheader("📋 Répertoire des Clients")
    if clients_existants:
        for c in clients_existants:
            with st.expander(f"👤 **{c['nom']}**"):
                st.write(f"📞 **Tél** : {c.get('telephone') or 'Non renseigné'}")
                st.write(f"✉️ **E-mail** : {c.get('email') or 'Non renseigné'}")
                st.write(f"🏷️ **Griffe** : {c.get('griffe') or 'Aucune'}")
                st.write(f"📏 **Pos. Griffe** : {c.get('griffe_position_mm', 15)} mm")
                
                if st.button(f"🗑️ Supprimer {c['nom']}", key=f"del_{c['nom']}"):
                    if supprimer_client(c["nom"]):
                        st.success(f"Client {c['nom']} supprimé.")
                        st.rerun()
    else:
        st.info("Aucun client dans la base de données.")
