import json
from datetime import datetime
import pandas as pd
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


def lister_les_trains_du_client(client):
  supabase = obtenir_client_supabase()
  reponse = (
      supabase.table("fiches_livres")
      .select("numero_train")
      .eq("nom_client", client)
      .execute()
  )
  return sorted(
      list(set([row["numero_train"] for row in reponse.data])), reverse=True
  )


def lister_les_livres_du_train(client, train):
  supabase = obtenir_client_supabase()
  reponse = (
      supabase.table("fiches_livres")
      .select("numero_livre")
      .eq("nom_client", client)
      .eq("numero_train", train)
      .order("numero_livre")
      .execute()
  )
  return [row["numero_livre"] for row in reponse.data]


def charger_types_toile_supabase():
  supabase = obtenir_client_supabase()
  try:
    reponse = (
        supabase.table("referentiel_toiles").select("type_toile").execute()
    )
    types = sorted(list(set([row["type_toile"] for row in reponse.data])))
    return types if types else ["Buckram", "Fantasia", "Métisse"]
  except Exception:
    return ["Buckram", "Fantasia", "Métisse"]


def charger_couleurs_par_toile_supabase(type_toile):
  supabase = obtenir_client_supabase()
  try:
    reponse = (
        supabase.table("referentiel_toiles")
        .select("couleur")
        .eq("type_toile", type_toile)
        .order("couleur")
        .execute()
    )
    couleurs = [row["couleur"] for row in reponse.data]
    return (
        couleurs
        if couleurs
        else [
            "Noir",
            "Rouge",
            "Bleu",
            "Vert",
            "Jaune",
            "Orange",
            "Violet",
            "Marron",
        ]
    )
  except Exception:
    return [
        "Noir",
        "Rouge",
        "Bleu",
        "Vert",
        "Jaune",
        "Orange",
        "Violet",
        "Marron",
    ]


def recuperer_specs_livre(client, train, num_livre):
  """Récupère en toute sécurité les caractéristiques du livre avec typage explicite"""
  supabase = obtenir_client_supabase()
  try:
    num_livre_int = int(num_livre)
    reponse = (
        supabase.table("fiches_livres")
        .select(
            "largeur, hauteur, epaisseur, type_toile, couleur, titrage_couleur,"
            " cocher_piece_titre, couleur_pieces_toile, marquage_pieces,"
            " nombre_pieces_titre"
        )
        .eq("nomC'est bien noté. Pour que le calcul et l'affichage restent parfaitement souples, voici les ajustements intégrés aux règles :

1. **Hauteur Maquette dynamique :** La règle prend désormais par défaut la **hauteur finie + 5 mm** (débord / marge technique standard), tout en laissant ce champ **modifiable manuellement** en cas de besoin spécifique sur une commande ou un gabarit particulier.
2. **Nettoyage du visuel :** Les mentions de l'**épaisseur utile** et de la **hauteur du titre** sont retirées du rendu visuel pour ne pas surcharger le schéma et ne garder que l'essentiel pour le calage.

---

### Formule ajustée

$$\text{Hauteur Maquette} = \text{Hauteur Finie} + 5\text{ mm} \quad (\text{ajustable})$$

---

### Aperçu de la logique d'affichage

```text
[ Dimensions Finies ]
  ├── Largeur : [ X ] mm
  └── Hauteur : [ Y ] mm

[ Paramètres Technique / Maquette ]
  └── Hauteur Maquette : [ Y + 5 ] mm  <-- (Champ éditable)

[ Visuel Dynamique ]
  ┌─────────────────────────────┐
  │                             │
  │     Hauteur Maquette        │
  │      (L x H Maquette)       │
  │                             │
  └─────────────────────────────┘
  (Masqués : Épaisseur utile, Hauteur du titre)
