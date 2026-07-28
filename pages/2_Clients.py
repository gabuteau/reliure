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
  reponse = (
      supabase.table("clients").select("*").eq("nom", nom_client).execute()
  )
  return reponse.data[0] if reponse.data else None


def enregistrer_client(nom, adresse, contact, notes, griffe):
  supabase = obtenir_client_supabase()
  donnees = {
      "nom": nom,
      "adresse": adresse,
      "contact_nom": contact,
      "notes": notes,
      "griffe": griffe,
  }

  try:
    # 1. Vérification si le client existe déjà
    verification = (
        supabase.table("clients").select("nom").eq("nom", nom).execute()
    )

    if verification.data:
      # 2. Mise à jour si existant
      supabase.table("clients").update(donnees).eq("nom", nom).execute()
    else:
      # 3. Insertion propre si nouveau client
      supabase.table("clients").insert(donnees).execute()

      # --- DUPLICATION DES TARIFS INVELAC PAR DÉFAUT ---
      try:
        tarifs_invelac = (
            supabase.table("tarifs_clients")
            .select("*")
            .eq("nom_client", "Invelac")
            .execute()
        )

        if tarifs_invelac.data:
          nouvelles_lignes_tarifs = []
          for t in tarifs_invelac.data:
            nouvel_item = t.copy()
            if "id" in nouvel_item:
              del nouvel_item["id"]
            nouvel_item["nom_client"] = nom
            nouvelles_lignes_tarifs.append(nouvel_item)

          supabase.table("tarifs_clients").insert(
              nouvelles_lignes_tarifs
          ).execute()
      except Exception as e_tarifs:
        st.warning(
            "Le client a été créé, mais la copie des tarifs par défaut"
            f" (Invelac) a échoué : {e_tarifs}"
        )
      # --- FIN DUPLICATION ---

  except Exception as e:
    st.error(f"Détail de l'erreur retournée par la base : {e}")


def supprimer_client_globale(nom_client):
  supabase = obtenir_client_supabase()
  supabase.table("tarifs_clients").delete().eq(
      "nom_client", nom_client
  ).execute()
  supabase.table("fiches_livres").delete().eq(
      "nom_client", nom_client
  ).execute()
  supabase.table("titrage_system3").delete().eq(
      "nom_client", nom_client
  ).execute()
  supabase.table("clients").delete().eq("nom", nom_client).execute()


# --- CONFIGURATION ET INTERFACE STREAMLIT ---
st.set_page_config(page_title="Gestion des Clients", layout="wide")
st.title("🏢 Gestion de l'Annuaire des Clients")

action_client = st.radio(
    "Action :",
    ["Sélectionner / Modifier un client", "➕ Créer un nouveau client"],
    horizontal=True,
)
st.write("---")

liste_clients_existants = lister_tous_les_clients()

if action_client == "➕ Créer un nouveau client":
  with st.form("form_creer_client"):
    nc_nom = st.text_input("Nom de l'établissement / Client *").strip()
    nc_contact = st.text_input("Nom du contact référent")
    nc_adresse = st.text_area("Adresse complète")
    nc_notes = st.text_area("Notes d'atelier spécifiques")

    st.write("---")
    st.markdown("##### 🏷️ Option Griffe (Marquage fixe de bas de dos)")
    activer_griffe_creation = st.checkbox("Activer une griffe pour ce client")
    nc_griffe = ""
    if activer_griffe_creation:
      nc_griffe = st.text_area(
          "Libellé de la griffe (1 à 3 lignes max)",
          placeholder="Ex: E.N.S.\nou\nARCHIVES\nDEPARTEMENTALES",
          height=90,
      )

    if st.form_submit_button("💾 Enregistrer le nouveau client") and nc_nom:
      enregistrer_client(
          nc_nom,
          nc_adresse,
          nc_contact,
          nc_notes,
          nc_griffe.strip() if activer_griffe_creation else "",
      )
      st.success(f"Client '{nc_nom}' synchronisé via API Supabase.")
      st.rerun()

else:
  if liste_clients_existants:
    client_sel = st.selectbox(
        "Choisir le client à gérer :", options=liste_clients_existants
    )
    fiche = recuperer_fiche_client(client_sel)

    if fiche:
      griffe_actuelle = fiche.get("griffe") or ""

      with st.form("form_modif_client"):
        mod_contact = st.text_input(
            "Nom du contact référent", value=fiche.get("contact_nom", "")
        )
        mod_adresse = st.text_area(
            "Adresse complète", value=fiche.get("adresse", "")
        )
        mod_notes = st.text_area(
            "Notes d'atelier", value=fiche.get("notes", "")
        )

        st.write("---")
        st.markdown("##### 🏷️ Option Griffe (Marquage fixe de bas de dos)")
        activer_griffe_modif = st.checkbox(
            "Activer la griffe pour ce client",
            value=bool(griffe_actuelle.strip()),
        )
        mod_griffe = ""
        if activer_griffe_modif:
          mod_griffe = st.text_area(
              "Libellé de la griffe (1 à 3 lignes max)",
              value=griffe_actuelle,
              placeholder="Ex: E.N.S.",
              height=90,
          )

        if st.form_submit_button("💾 Sauvegarder les modifications"):
          enregistrer_client(
              fiche["nom"],
              mod_adresse,
              mod_contact,
              mod_notes,
              mod_griffe.strip() if activer_griffe_modif else "",
          )
          st.success("Fiche client mise à jour.")
          st.rerun()

      st.write("---")
      st.markdown("#### 🚨 Zone de danger")

      key_session_del = f"confirm_delete_{fiche['nom']}"
      if key_session_del not in st.session_state:
        st.session_state[key_session_del] = False

      if not st.session_state[key_session_del]:
        if st.button(
            f"❌ Demander la suppression globale de {fiche['nom']}"
        ):
          st.session_state[key_session_del] = True
          st.rerun()
      else:
        st.warning(
            f"Confirmer la suppression définitive de {fiche['nom']} sur le"
            " cloud ?"
        )
        col_del1, col_del2 = st.columns(2)
        with col_del1:
          if st.button("✔️ OUI, EFFACER TOUT"):
            supprimer_client_globale(fiche["nom"])
            st.session_state[key_session_del] = False
            st.rerun()
        with col_del2:
          if st.button("🔄 Annuler"):
            st.session_state[key_session_del] = False
            st.rerun()
  else:
    st.info("Aucun client enregistré pour le moment dans la base.")
