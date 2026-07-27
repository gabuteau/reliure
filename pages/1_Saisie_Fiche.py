import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Composition Titrage",
    page_icon="📟",
    layout="wide"
)

st.title("📟 Composition & Aperçu du Titrage (S3)")
st.markdown("Réglage des polices, des orientations et des couleurs de dorure / marquage.")
st.write("---")

# --- LISTES DE SÉLECTION MISES À JOUR ---
LISTE_POLICES = ["Elzevir", "Didot", "Baton", "Garamond"]
LISTE_ORIENTATIONS = ["Long", "Classique"]
LISTE_COULEURS_MARQUAGE = ["OR", "ARGENT", "NOIR", "BLANC", "OXYDE", "AUTRE"]
LISTE_TOILES = ["Buckram", "Toile Fine", "Chagrin", "Fantasia", "Métisse"]

# --- FORMULAIRE DE SELECTION & RÉGLAGES ---
col_selection, col_options = st.columns(2)

with col_selection:
    st.subheader("📚 Ouvrage & Matière")
    client_nom = st.text_input("Client", value="Mairie de Périgueux")
    type_toile = st.selectbox("Type de Toile / Matière", LISTE_TOILES)
    couleur_toile = st.text_input("Couleur de la toile", value="Bleu Marine")

with col_options:
    st.subheader("⚙️ Paramètres de Marquage")
    police_titre = st.selectbox("Police de caractères", LISTE_POLICES)
    orientation = st.selectbox("Orientation du titrage", LISTE_ORIENTATIONS)
    couleur_marquage = st.selectbox("Couleur de marquage", LISTE_COULEURS_MARQUAGE)

st.write("---")

# --- COMPOSITION DU TITRAGE ---
st.subheader("✍️ Textes du Dos")

col_t1, col_t2 = st.columns(2)

with col_t1:
    titre_principal = st.text_input("Titre principal", value="DELIBERATIONS")
    sous_titre = st.text_input("Sous-titre / Precision", value="CONSEIL MUNICIPAL")

with col_t2:
    annee_tome = st.text_input("Année / Tome", value="2025 - T. I")
    pieces_annexes = st.text_input("Mentions complémentaires", value="")

# --- APERÇU DYNAMIQUE ---
st.write("---")
st.subheader("👁️ Prévisualisation du Titrage")

# Définition simple des couleurs pour la simulation visuelle
code_couleur_marquage = {
    "OR": "#D4AF37",
    "ARGENT": "#C0C0C0",
    "NOIR": "#000000",
    "BLANC": "#FFFFFF",
    "OXYDE": "#8B4513",
    "AUTRE": "#6C757D"
}.get(couleur_marquage, "#D4AF37")

html_preview = f"""
<div style="
    background-color: #1a2a3a;
    color: {code_couleur_marquage};
    padding: 30px;
    border-radius: 8px;
    text-align: center;
    font-family: sans-serif;
    border: 2px solid #ccc;
    max-width: 300px;
    margin: 0 auto;
">
    <div style="font-size: 12px; color: #aaa; margin-bottom: 15px;">TOILE : {type_toile.upper()} ({couleur_toile})</div>
    <div style="font-size: 18px; font-weight: bold; letter-spacing: 2px; margin-bottom: 10px;">{titre_principal}</div>
    <div style="font-size: 14px; margin-bottom: 20px;">{sous_titre}</div>
    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">{annee_tome}</div>
    <div style="font-size: 12px;">{pieces_annexes}</div>
    <div style="margin-top: 25px; font-size: 11px; color: #888;">POLICE : {police_titre} | SENS : {orientation}</div>
</div>
"""

st.components.v1.html(html_preview, height=260)

st.write("---")

if st.button("⬅️ Retour au Menu principal"):
    st.switch_page("app.py")
