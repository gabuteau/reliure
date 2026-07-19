import streamlit as st

st.set_page_config(
    page_title="Gestion Reliure & Atelier",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Système de Gestion de l'Atelier de Reliure")
st.write("---")

st.markdown("""
### Bienvenue dans votre outil de gestion et de suivi de production
Ce système cloud centralise l'ensemble de l'activité de l'atelier, de la prise de commande à l'impression des fiches techniques de fabrication. Usez du menu latéral à gauche ou des boutons ci-dessous pour naviguer entre les différents modules.
""")

st.write("---")

# Cartes de présentation des modules disponibles
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Saisie & Suivi")
    st.markdown("""
    * **Saisie de Fiche** : Module principal permettant d'enregistrer un nouveau livre ou de modifier un volume existant. Il calcule en temps réel le sous-total des suppléments et détecte automatiquement le gabarit du format selon les dimensions saisies.
    * **Titrage (Système 3)** : Permet de composer la maquette de titrage spécifique d'un volume et de configurer la grille de lettrage.
    """)
    
    # Boutons de navigation (Ajustez le nom exact de vos fichiers de pages si nécessaire)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("👉 Aller à Saisie de Fiche", key="nav_saisie", use_container_width=True):
            st.switch_page("pages/1_Saisie_Fiche.py")
    with c_btn2:
        # Remplacer par le nom exact de votre fichier de titrage
        if st.button("👉 Aller au Titrage", key="nav_titrage", use_container_width=True):
            st.switch_page("pages/4_Titrage.py")

with col2:
    st.subheader("🖨️ Production & Impression")
    st.markdown("""
    * **Impression Garde** : Génère la fiche technique d'atelier au format standardisé, conforme au modèle manuscrit. Permet d'imprimer à la volée une fiche unitaire ou de lancer l'impression groupée de tout un train (avec sauts de page automatiques).
    * **Fiches Clients** : Permet de gérer la liste des donneurs d'ordres et de configurer leurs paramètres de facturation par défaut.
    """)
    
    c_btn3, c_btn4 = st.columns(2)
    with c_btn3:
        if st.button("🖨️ Aller à Impression Garde", key="nav_print", use_container_width=True):
            st.switch_page("pages/5_Impression_Garde.py")
    with c_btn4:
        # Remplacer par le nom exact de votre fichier client
        if st.button("👥 Aller aux Fiches Clients", key="nav_clients", use_container_width=True):
            st.switch_page("pages/2_Clients.py")

st.write("---")
st.info("💡 **Rappel d'utilisation** : Pour toute impression de document (Fiche de garde), utilisez le raccourci natif de votre navigateur **Ctrl + P** (ou **Cmd + P** sur Mac) une fois sur la page concernée.")
