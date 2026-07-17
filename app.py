import streamlit as st
import sqlite3

st.set_page_config(page_title="Gestion Atelier Reliure", layout="wide")

st.title("📟 Menu Général — Atelier de Reliure")
st.write("---")

st.markdown("""
### Bienvenue dans votre outil de gestion d'atelier.
Veuillez sélectionner le module souhaité dans la **barre latérale gauche** pour commencer à travailler :

*   **📚 Saisie & Suivi des Livres** : Pour enregistrer vos fiches de livres et suivre les trains en cours.
*   **🏢 Fiches Clients** : Pour gérer votre annuaire et vos fiches d'atelier spécifiques.
*   **🏷️ Grilles Tarifaires Clients** : Pour ajuster les prix personnalisés par client et par format.
*   **📟 Titrage Système 3** : Pour composer vos dos et prévisualiser vos lignes de texte en direct.
""")

# Initialisation rapide des tables au premier lancement si besoin
DB_FILE = "base_reliure_v2.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS clients (nom TEXT PRIMARY KEY, adresse TEXT, telephone TEXT, email TEXT, contact_nom TEXT, notes TEXT)")
conn.commit()
conn.close()