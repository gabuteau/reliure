import streamlit as st
import base64
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Menu principal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INJECTION CSS (STRUCTURE SIDEBAR & LOGO + TRICHE NOM RECTIFIÉE) ---
st.html(
    """
    <style>
        /* Réorganisation de la barre latérale en Flexbox */
        [data-testid="stSidebarUserContent"] {
            display: flex;
            flex-direction: column;
        }
        
        /* Positionne le logo tout en haut */
        .logo-container {
            order: 1;
            margin-bottom: 20px;
        }
        
        /* Positionne le menu de navigation natif sous le logo */
        [data-testid="stSidebarNav"] {
            order: 2;
        }
        
        /* TRICHE : Remplacement propre du texte "app" par "Menu principal" */
        [data-testid="stSidebarNavItems"] li:first-child a [data-testid="stSidebarNavLinkWrapper"] {
            visibility: hidden;
            position: relative;
        }
        [data-testid="stSidebarNavItems"] li:first-child a [data-testid="stSidebarNavLinkWrapper"]::after {
            content: "Menu principal";
            visibility: visible;
            position: absolute;
            left: 0;
            top: 0;
            white-space: nowrap;
        }
        
        /* Positionne le pied de page tout en bas */
        .sidebar-footer {
            order: 3;
        }

        /* Style du lien image */
        .logo-link {
            display: block;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        .logo-link:hover {
            opacity: 0.8;
        }
    </style>
    """
)
# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # 1. Zone du Logo (Ordre 1)
    st.html('<div class="logo-container">')
    chemin_logo = "logo_reliure.jpg"
    if os.path.exists(chemin_logo):
        with open(chemin_logo, "rb") as f:
            data_logo = base64.b64encode(f.read()).decode()
        st.html(f'<a href="/" target="_self" class="logo-link"><img src="data:image/jpeg;base64,{data_logo}" style="width: 100%;"></a>')
    else:
        if st.button("📚 Menu principal", key="nav_home_fallback", use_container_width=True):
            st.switch_page("Menu_principal.py")
    st.html('</div>')
            
    # 2. Le menu de navigation natif s'intercale ici (Ordre 2)
            
    # 3. Zone Pied de page (Ordre 3)
    st.html('<div class="sidebar-footer">')
    st.write("---")
    st.caption("Système de Gestion d'Atelier — 2026")
    st.html('</div>')


# --- CORPS PRINCIPAL ---
st.title("📚 Système de Gestion de l'Atelier de Reliure")
st.markdown("### Outil centralisé de suivi de production et d'administration")
st.write("---")

# Zone d'information / Rappels pratiques
st.info("💡 **Rappel d'impression** : Pour imprimer une fiche de garde ou une fiche technique d'atelier, utilisez le raccourci clavier natif de votre navigateur : **Ctrl + P** (ou **Cmd + P** sur Mac).")

st.write("---")

# Découpage fonctionnel de l'accueil en 3 colonnes
col_prod, col_tarifs, col_admin = st.columns(3)

with col_prod:
    with st.container(border=True):
        st.markdown("### 🛠️ Production & Suivi")
        st.markdown("""
        Enregistrez les caractéristiques des ouvrages, gérez les étapes de fabrication et éditez vos fiches d'atelier.
        """)
        st.write(" ")
        
        if st.button("📝 Saisie & Suivi de Fiche", key="nav_saisie", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Saisie_Fiche.py")
            
        if st.button("🖨️ Impression Fiche Garde", key="nav_print", use_container_width=True):
            st.switch_page("pages/5_Impression_Garde.py")
            
        if st.button("📟 Composition Titrage (S3)", key="nav_titrage", use_container_width=True):
            st.switch_page("pages/4_Titrage.py")

with col_tarifs:
    with st.container(border=True):
        st.markdown("### 📊 Grilles Tarifaires")
        st.markdown("""
        Consultez et ajustez les prix des prestations et des suppléments selon vos deux modes de visualisation préférés.
        """)
        st.write(" ")
        
        if st.button("🏷️ Ajustement par Client (Matrice)", key="nav_tarifs_matrice", use_container_width=True):
            st.switch_page("pages/3_Tarifs.py")
            
        if st.button("⚙️ Recherche & Filtres (Liste)", key="nav_tarifs_liste", use_container_width=True):
            st.switch_page("pages/6_Configuration_Tarifs.py")

with col_admin:
    with st.container(border=True):
        st.markdown("### 🏢 Donneurs d'Ordres")
        st.markdown("""
        Gérez l'annuaire de vos clients, configurez les fiches de contacts et initialisez automatiquement leurs paramètres de facturation.
        """)
        st.write(" ")
        st.write(" ") 
        
        if st.button("👥 Annuaire & Fiches Clients", key="nav_clients", use_container_width=True):
            st.switch_page("pages/2_Clients.py")

st.write("---")
