import streamlit as st
from supabase import create_client
from datetime import datetime

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
    reponse = supabase.table("fiches_livres").select("numero_train").eq("nom_client", client).execute()
    return sorted(list(set([row["numero_train"] for row in reponse.data])), reverse=True)

def lister_les_livres_du_train(client, train):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("numero_livre").eq("nom_client", client).eq("numero_train", train).order("numero_livre").execute()
    return [row["numero_livre"] for row in reponse.data]

def recuperer_livre_complet(client, train, num_livre):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("*").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
    return reponse.data[0] if reponse.data else None

# Configuration de la page
st.set_page_config(page_title="Impression Garde", layout="centered")

# --- Injection sécurisée du CSS via st.html() ---
st.html("""
    <style>
    @media print {
        #MainMenu, header, footer, div.stButton, div[data-testid="stSidebar"] {
            display: none !important;
        }
        .stMain {
            padding-top: 0px !important;
        }
        .print-container {
            border: 1px solid #000;
            padding: 30px;
            font-family: 'Courier New', Courier, monospace;
            color: #000;
            background-color: #fff;
        }
        h2, h3, h4 {
            color: #000 !important;
        }
    }
    .print-box {
        border: 1px solid #333;
        padding: 15px;
        border-radius: 5px;
        background-color: #fafafa;
        margin-bottom: 15px;
    }
    .field-label {
        font-weight: bold;
        color: #555;
    }
    .field-value {
        font-size: 1.1em;
        font-weight: bold;
        color: #000;
    }
    </style>
""")

st.title("🖨️ Génération — Impression Garde")

# --- Zone de sélection ---
with st.container():
    st.subheader("Sélection du document")
    c1, c2, c3 = st.columns(3)
    
    liste_clients = lister_tous_les_clients()
    with c1:
        client_sel = st.selectbox("Client", options=["-- Choisir --"] + liste_clients)
    
    if client_sel != "-- Choisir --":
        liste_trains = lister_les_trains_du_client(client_sel)
        with c2:
            train_sel = st.selectbox("N° du Train", options=["-- Choisir --"] + liste_trains)
            
        if train_sel != "-- Choisir --":
            liste_livres = lister_les_livres_du_train(client_sel, train_sel)
            with c3:
                livre_sel = st.selectbox("N° du Livre", options=["-- Choisir --"] + liste_livres)

st.write("---")

# --- Rendu de la fiche de garde ---
if client_sel != "-- Choisir --" and train_sel != "-- Choisir --" and 'livre_sel' in locals() and livre_sel != "-- Choisir --":
    
    data = recuperer_livre_complet(client_sel, train_sel, int(livre_sel))
    
    if data:
        st.info("💡 Pour imprimer cette fiche de garde : utilisez le raccourci **Ctrl + P** (ou Cmd + P sur Mac) de votre navigateur.")
        
        # Début du bloc imprimable
        st.markdown('<div class="print-container">', unsafe_allowed_html=True)
        
        st.markdown("<h2 style='text-align: center; text-decoration: underline; margin-bottom: 30px;'>Informations sur la page de garde</h2>", unsafe_allowed_html=True)
        
        # 1. En-tête Général
        c_entete_1, c_entete_2 = st.columns(2)
        with c_entete_1:
            st.markdown(f"<span class='field-label'>Client :</span> <span class='field-value'>{data['nom_client']}</span>", unsafe_allowed_html=True)
            st.markdown(f"<span class='field-label'>N° du Train :</span> <span class='field-value'>{data['numero_train']}</span>", unsafe_allowed_html=True)
            st.markdown(f"<span class='field-label'>N° du Livre :</span> <span class='field-value'>{data['numero_livre']}</span>", unsafe_allowed_html=True)
        with c_entete_2:
            date_du_jour = datetime.now().strftime("%d/%m/%Y")
            st.markdown(f"<span class='field-label'>Date :</span> <span class='field-value'>{date_du_jour}</span>", unsafe_allowed_html=True)
        
        st.markdown("<br>", unsafe_allowed_html=True)
        
        # 2. Dimensions & Format
        st.markdown("### 📐 Dimensions & Format")
        st.markdown('<div class="print-box">', unsafe_allowed_html=True)
        c_dim_1, c_dim_2 = st.columns(2)
        with c_dim_1:
            st.markdown(f"<span class='field-label'>Hauteur :</span> <span class='field-value'>{data['hauteur']} mm</span>", unsafe_allowed_html=True)
            st.markdown(f"<span class='field-label'>Largeur :</span> <span class='field-value'>{data['largeur']} mm</span>", unsafe_allowed_html=True)
            st.markdown(f"<span class='field-label'>Épaisseur :</span> <span class='field-value'>{data['epaisseur']} mm</span>", unsafe_allowed_html=True)
        with c_dim_2:
            st.markdown(f"<span class='field-label'>Hauteur Maquette :</span> <span class='field-value'>{data['hauteur_maquette']} mm</span>", unsafe_allowed_html=True)
            rogner_str = "NON" if data['ne_pas_rogner'] else "OUI"
            st.markdown(f"<span class='field-label'>Ne pas Rogner :</span> <span class='field-value'>{rogner_str}</span>", unsafe_allowed_html=True)
        st.markdown('</div>', unsafe_allowed_html=True)
        
        # 3. Traitement & Technique
        st.markdown("### 🛠️ Traitement & Technique")
        st.markdown('<div class="print-box">', unsafe_allowed_html=True)
        c_tech_1, c_tech_2 = st.columns(2)
        with c_tech_1:
            st.markdown(f"<span class='field-label'>Traitement :</span> <span class='field-value'>{data['traitement']}</span>", unsafe_allowed_html=True)
            st.markdown(f"<span class='field-label'>Type de reliure :</span> <span class='field-value'>{data['type_reliure']}</span>", unsafe_allowed_html=True)
            st.markdown(f"<span class='field-label'>Type de couture :</span> <span class='field-value'>{data['type_couture']}</span>", unsafe_allowed_html=True)
        with c_tech_2:
            scanne_str = "OUI" if data['repro_scanne'] else "NON"
            report_str = "OUI" if data['repro_report'] else "NON"
            st.markdown(f"<span class='field-label'>Scannée :</span> <span class='field-value'>{scanne_str}</span>", unsafe_allowed_html=True)
            st.markdown(f"<span class='field-label'>Repat (Report) :</span> <span class='field-value'>{report_str}</span>", unsafe_allowed_html=True)
            if data['type_couture'] == "Cahier manuel":
                st.markdown(f"<span class='field-label'>Nombre de cahiers :</span> <span class='field-value'>{data['nombre_cahiers']}</span>", unsafe_allowed_html=True)
                st.markdown(f"<span class='field-label'>Agraphes :</span> <span class='field-value'>{'Oui' if data['agraphes'] else 'Non'}</span>", unsafe_allowed_html=True)
        st.markdown('</div>', unsafe_allowed_html=True)
        
        # 4. Habillage & Finition
        st.markdown("### 🎨 Matériaux & Finitions")
        st.markdown('<div class="print-box">', unsafe_allowed_html=True)
        
        titrage_toile_str = "SANS TITRAGE" if data['sans_titrage'] else f"{data['titrage_couleur']} ({data['titrage_sens']})"
        st.markdown(
            f"<div style='margin-bottom: 10px;'>"
            f"<span class='field-label'>Type de Toile :</span> <span class='field-value'>{data['type_toile']}</span> | "
            f"<span class='field-label'>Couleur :</span> <span class='field-value'>{data['couleur']}</span> | "
            f"<span class='field-label'>Titrage :</span> <span class='field-value'>{titrage_toile_str}</span>"
            f"</div>", 
            unsafe_allowed_html=True
        )
        
        if data['cocher_piece_titre']:
            st.markdown(
                f"<div>"
                f"<span class='field-label'>Pièce de Titre :</span> <span class='field-value'>OUI</span> | "
                f"<span class='field-label'>Couleur :</span> <span class='field-value'>{data['couleur_pieces_toile']}</span> | "
                f"<span class='field-label'>Titrage :</span> <span class='field-value'>{data['marquage_pieces']}</span>"
                f"</div>", 
                unsafe_allowed_html=True
            )
        else:
            st.markdown(f"<div><span class='field-label'>Pièce de Titre :</span> <span class='field-value'>NON</span></div>", unsafe_allowed_html=True)
            
        st.markdown('</div>', unsafe_allowed_html=True)
        
        # 5. Suppléments / Options
        st.markdown("### 📌 Options & Suppléments")
        st.markdown('<div class="print-box">', unsafe_allowed_html=True)
        sups = [data[f'supplement_{i}'] for i in range(1, 5) if data[f'supplement_{i}']]
        if sups:
            for s in sups:
                st.markdown(f"- <span class='field-value'>{s}</span>", unsafe_allowed_html=True)
        else:
            st.markdown("<span class='field-value'>Aucun supplément</span>", unsafe_allowed_html=True)
        st.markdown('</div>', unsafe_allowed_html=True)
        
        st.markdown('</div>', unsafe_allowed_html=True)
    else:
        st.error("Impossible de récupérer les informations de ce livre.")
