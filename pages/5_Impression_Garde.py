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
    reponse = supabase.table("fiches_livres").select("numero_train").eq("nom_client", client.strip()).execute()
    return sorted(list(set([row["numero_train"] for row in reponse.data])), reverse=True)

def lister_les_livres_du_train(client, train):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("numero_livre").eq("nom_client", client.strip()).eq("numero_train", train.strip()).order("numero_livre").execute()
    return [row["numero_livre"] for row in reponse.data]

def recuperer_livre_complet(client, train, num_livre):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("*").eq("nom_client", client.strip()).eq("numero_train", train.strip()).eq("numero_livre", num_livre).execute()
    return reponse.data[0] if reponse.data else None

def recuperer_tous_les_livres_du_train(client, train):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("*").eq("nom_client", client.strip()).eq("numero_train", train.strip()).order("numero_livre").execute()
    return reponse.data if reponse.data else []

# Configuration de la page
st.set_page_config(page_title="Impression Garde", layout="centered")

# --- Injection du style CSS d'impression ---
st.html("""
    <style>
    @media print {
        #MainMenu, header, footer, div.stButton, div[data-testid="stSidebar"], .no-print {
            display: none !important;
        }
        .stMain {
            padding-top: 0px !important;
        }
        .print-container {
            border: 2px solid #000 !important;
            padding: 30px !important;
            font-family: 'Courier New', Courier, monospace !important;
            color: #000 !important;
            background-color: #fff !important;
            page-break-after: always !important; /* Force un saut de page pour l'imprimante entre chaque livre */
            margin-bottom: 0px !important;
        }
    }
    .print-container {
        border: 1px solid #333;
        padding: 30px;
        font-family: Arial, sans-serif;
        background-color: #fff;
        color: #000;
        border-radius: 8px;
        margin-top: 20px;
        margin-bottom: 30px;
    }
    .print-box {
        border: 1px solid #ccc;
        padding: 15px;
        border-radius: 5px;
        background-color: #fafafa;
        margin-bottom: 20px;
    }
    .print-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .print-col {
        flex: 1;
        margin-right: 20px;
    }
    .print-col:last-child {
        margin-right: 0;
    }
    .field-label {
        font-weight: bold;
        color: #444;
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
with st.container(border=True):
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
            # Ajout de l'option globale pour le train complet
            options_livres = ["-- Choisir --", "🖨️ [TOUT LE TRAIN ENTIER]"] + [str(n) for n in liste_livres]
            with c3:
                livre_sel = st.selectbox("Sélection du volume", options=options_livres)

st.write("---")

def generer_bloc_html_fiche(data, date_str):
    """Génère la structure HTML propre pour une fiche unique"""
    rogner_str = "OUI" if data.get('ne_pas_rogner') else "NON"
    scanne_str = "OUI" if data.get('repro_scanne') else "NON"
    report_str = "OUI" if data.get('repro_report') else "NON"
    titrage_toile_str = "SANS TITRAGE" if data.get('sans_titrage') else f"{data.get('titrage_couleur')} ({data.get('titrage_sens')})"
    
    if data.get('cocher_piece_titre'):
        html_piece_titre = f"""
        <div style='margin-top: 10px;'>
            <span class='field-label'>Pièce de Titre :</span> <span class='field-value'>OUI</span> | 
            <span class='field-label'>Couleur :</span> <span class='field-value'>{data.get('couleur_pieces_toile')}</span> | 
            <span class='field-label'>Titrage :</span> <span class='field-value'>{data.get('marquage_pieces')}</span>
        </div>
        """
    else:
        html_piece_titre = "<div><span class='field-label'>Pièce de Titre :</span> <span class='field-value'>NON</span></div>"
        
    html_couture_details = ""
    if data.get('type_couture') == "Cahier manuel":
        html_couture_details = f"""
        <br>
        <span class='field-label'>Nombre de cahiers :</span> <span class='field-value'>{data.get('nombre_cahiers')}</span><br>
        <span class='field-label'>Agraphes :</span> <span class='field-value'>{'Oui' if data.get('agraphes') else 'Non'}</span>
        """

    sups = [data.get(f'supplement_{i}') for i in range(1, 5) if data.get(f'supplement_{i}')]
    html_sups = ""
    if sups:
        for s in sups:
            html_sups += f"<li><span class='field-value'>{s}</span></li>"
    else:
        html_sups = "<div><span class='field-value'>Aucun supplément</span></div>"

    return f"""
    <div class="print-container">
        <h2 style="text-align: center; text-decoration: underline; margin-bottom: 30px;">- Informations sur la page de garde -</h2>
        
        <div class="print-row">
            <div class="print-col">
                <span class="field-label">Client :</span> <span class="field-value">{data.get('nom_client')}</span><br>
                <span class="field-label">N° du Train :</span> <span class="field-value">{data.get('numero_train')}</span><br>
                <span class="field-label">N° du Livre :</span> <span class="field-value">{data.get('numero_livre')}</span>
            </div>
            <div class="print-col" style="text-align: right;">
                <span class="field-label">Date :</span> <span class="field-value">{date_str}</span>
            </div>
        </div>
        
        <br>
        
        <h3>📐 Dimensions & Format</h3>
        <div class="print-box">
            <div class="print-row">
                <div class="print-col">
                    <span class="field-label">Hauteur :</span> <span class="field-value">{data.get('hauteur')} mm</span><br>
                    <span class="field-label">Largeur :</span> <span class="field-value">{data.get('largeur')} mm</span><br>
                    <span class="field-label">Épaisseur :</span> <span class="field-value">{data.get('epaisseur')} mm</span>
                </div>
                <div class="print-col">
                    <span class="field-label">Hauteur Maquette :</span> <span class="field-value">{data.get('hauteur_maquette')} mm</span><br>
                    <span class="field-label">Ne pas Rogner :</span> <span class="field-value">{rogner_str}</span>
                </div>
            </div>
        </div>
        
        <h3>🛠️ Traitement & Technique</h3>
        <div class="print-box">
            <div class="print-row">
                <div class="print-col">
                    <span class="field-label">Traitement :</span> <span class="field-value">{data.get('traitement')}</span><br>
                    <span class="field-label">Type de reliure :</span> <span class="field-value">{data.get('type_reliure')}</span><br>
                    <span class="field-label">Type de couture :</span> <span class="field-value">{data.get('type_couture')}</span>
                    {html_couture_details}
                </div>
                <div class="print-col">
                    <span class="field-label">Scannée :</span> <span class="field-value">{scanne_str}</span><br>
                    <span class="field-label">Repat (Report) :</span> <span class="field-value">{report_str}</span>
                </div>
            </div>
        </div>
        
        <h3>🎨 Matériaux & Finitions</h3>
        <div class="print-box">
            <div style="margin-bottom: 10px;">
                <span class="field-label">Type de Toile :</span> <span class="field-value">{data.get('type_toile')}</span> | 
                <span class="field-label">Couleur :</span> <span class="field-value">{data.get('couleur')}</span> | 
                <span class="field-label">Titrage :</span> <span class="field-value">{titrage_toile_str}</span>
            </div>
            {html_piece_titre}
        </div>
        
        <h3>📌 Options & Suppléments</h3>
        <div class="print-box">
            <ul style="margin: 0; padding-left: 20px;">
                {html_sups}
            </ul>
        </div>
    </div>
    """

# --- Rendu des impressions ---
if client_sel != "-- Choisir --" and train_sel != "-- Choisir --" and 'livre_sel' in locals() and livre_sel != "-- Choisir --":
    
    date_commune = datetime.now().strftime("%d/%m/%Y")
    
    # CAS 1 : Impression globale de tout le train d'un coup
    if livre_sel == "🖨️ [TOUT LE TRAIN ENTIER]":
        liste_fiches = recuperer_tous_les_livres_du_train(client_sel, train_sel)
        
        if liste_fiches:
            st.info(f"💡 **Mode Train Complet** : {len(liste_fiches)} fiches prêtes. Lancez **Ctrl + P** pour générer le dossier d'impression d'un coup.")
            
            html_global = ""
            for fiche in liste_fiches:
                html_global += generer_bloc_html_fiche(fiche, date_commune)
                
            st.html(html_global)
        else:
            st.warning("Aucun livre trouvé dans ce train.")
            
    # CAS 2 : Impression d'une fiche unitaire
    else:
        fiche_unique = recuperer_livre_complet(client_sel, train_sel, int(livre_sel))
        if fiche_unique:
            st.info("💡 **Mode Fiche Unique** : Prête pour l'impression (**Ctrl + P**).")
            st.html(generer_bloc_html_fiche(fiche_unique, date_commune))
        else:
            st.error("Impossible de charger cette fiche de livre.")
