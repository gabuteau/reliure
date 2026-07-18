import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

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

def recuperer_specs_livre(client, train, num_livre):
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("largeur, hauteur, epaisseur").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
    if reponse.data:
        return reponse.data[0]["largeur"], reponse.data[0]["hauteur"], reponse.data[0]["epaisseur"]
    return 160, 220, 20  # Valeurs par défaut

st.set_page_config(page_title="Titrage Système 3", layout="wide")
st.title("📟 Module de Composition Spécifique — Titrage Système 3")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.warning("⚠️ Créez d'abord un client pour utiliser le module de titrage.")
else:
    col_form_saisie, col_gabarit_visualisation = st.columns([1.1, 0.9])
    
    with col_form_saisie:
        st.subheader("Clé de sélection du Livre")
        c_meta1, c_meta2 = st.columns(2)
        with c_meta1:
            t3_client = st.selectbox("1. Client référent", options=liste_clients_existants)
            t3_trains = lister_les_trains_du_client(t3_client)
            t3_train_sel = st.selectbox("2. N° de train", options=["-- Choisir --"] + t3_trains)
        
        # Initialisation aux valeurs standards d'atelier
        t3_larg_brute = 160
        t3_haut_brute = 220
        t3_epaisseur = 20
        liste_livres = []
        
        with c_meta2:
            t3_date = st.date_input("Date d'atelier", value=datetime.now())
            if t3_train_sel != "-- Choisir --":
                liste_livres = lister_les_livres_du_train(t3_client, t3_train_sel)
                t3_livre_num = st.selectbox("3. N° du livre", options=liste_livres)
                
                if t3_livre_num:
                    t3_larg_brute, t3_haut_brute, t3_epaisseur = recuperer_specs_livre(t3_client, t3_train_sel, t3_livre_num)
            else:
                st.info("Sélectionnez un train pour charger les livres.")
                t3_livre_num = None

        # Règle d'atelier : Largeur du dos = Épaisseur réelle + 10mm
        t3_largeur_dos_reelle = t3_epaisseur + 10

        st.write("---")
        st.subheader("📐 Caractéristiques physiques du dos (Lecture seule)")
        c_dim1, c_dim2, c_dim3 = st.columns(3)
        with c_dim1: st.number_input("Hauteur récupérée (mm)", value=int(t3_haut_brute), disabled=True)
        with c_dim2: st.number_input("Épaisseur d'origine (mm)", value=int(t3_epaisseur), disabled=True)
        with c_dim3: st.number_input("Largeur utile du dos (Ép + 10mm)", value=int(t3_largeur_dos_reelle), disabled=True)
        
        st.write("---")
        st.subheader("✍️ Composition des lignes (Position en mm)")
        
        # Initialisation du tableau avec des positions millimétriques réelles cohérentes
        if "df_lignes_system3_mm" not in st.session_state:
            st.session_state.df_lignes_system3_mm = pd.DataFrame([
                {"Hauteur du titre (mm)": 150, "Titrage": "TITRE EXEMPLE"},
                {"Hauteur du titre (mm)": 30, "Titrage": "COTE"}
            ])
            
        df_edite_lignes = st.data_editor(
            st.session_state.df_lignes_system3_mm,
            column_config={
                "Hauteur du titre (mm)": st.column_config.NumberColumn(
                    "Position (mm depuis le bas)", 
                    min_value=0, 
                    max_value=int(t3_haut_brute), 
                    step=1, 
                    required=True
                ),
                "Titrage": st.column_config.TextColumn("Texte à imprimer", required=True)
            },
            num_rows="dynamic",
            use_container_width=True
        )

    with col_gabarit_visualisation:
        st.subheader("📐 Gabarit dynamique du dos à dorer")
        
        # Échelle de conversion : 1 mm de livre = 2.5 pixels à l'écran
        facteur_px = 2.5
        
        hauteur_visuelle_px = int(t3_haut_brute * facteur_px)
        largeur_visuelle_px = int(t3_largeur_dos_reelle * facteur_px)
        
        # Bornes d'affichage pour conserver le confort de lecture sur l'écran
        hauteur_visuelle_px = max(min(hauteur_visuelle_px, 600), 350)
        largeur_visuelle_px = max(min(largeur_visuelle_px, 250), 60)
        
        # Le rapport réel de conversion pixel par millimètre pour ce livre spécifique
        px_par_mm = hauteur_visuelle_px / t3_haut_brute

        # Génération des paliers de la règle (tous les 10 mm en partant du bas)
        html_graduations = ""
        paliers_mm = list(range(0, int(t3_haut_brute) + 1, 10))
        if paliers_mm[-1] != int(t3_haut_brute):
            paliers_mm.append(int(t3_haut_brute))
            
        html_gabarit = f"""
        <div style="display: flex; font-family: monospace; background-color: #f8f9fa; padding: 20px; border-radius: 5px; min-height: {hauteur_visuelle_px + 60}px;">
            <!-- Règle graduée en millimètres réels -->
            <div style="position: relative; height: {hauteur_visuelle_px}px; width: 60px; border-right: 2px solid #ccc; text-align: right; padding-right: 8px;">
        """
        
        for mm in paliers_mm:
            pos_depuis_bas = mm * px_par_mm
            # Ajustement visuel pour aligner le texte sur le trait de repère
            correction_top = hauteur_visuelle_px - pos_depuis_bas - 6
            html_gabarit += f'<div style="position: absolute; top: {correction_top}px; right: 8px; font-size: 11px; color: #555;">{mm} mm —</div>'
            
        html_gabarit += f"""
            </div>
            <!-- Le dos du livre dimensionné d'après l'épaisseur + 10mm -->
            <div style="position: relative; width: {largeur_visuelle_px}px; height: {hauteur_visuelle_px}px; background-color: #fdf6e2; border: 2px solid #111; margin-left: 20px; box-shadow: inset 0 0 10px rgba(0,0,0,0.15); transition: all 0.2s ease;">
                <div style="position: absolute; width: 100%; top: 0; text-align: center; font-size: 10px; font-style: italic; background: #ddd; padding: 2px 0; border-bottom: 1px solid #111;">H: {t3_haut_brute}mm</div>
        """
        
        # Intégration des lignes de texte avec alerte de débordement
        for _, row_data in df_edite_lignes.iterrows():
            mm_pos = row_data["Hauteur du titre (mm)"]
            txt = str(row_data["Titrage"]).strip()
            
            if pd.notna(mm_pos) and txt and txt != "None":
                # Estimation de la taille du texte à l'écran (environ 8.5px de large par caractère en gras)
                taille_estimee_texte_px = len(txt) * 8.5
                
                # Alerte visuelle : Si le texte estimé est plus large que le dos, on écrit en rouge, sinon en noir standard
                couleur_texte = "#d9534f" if taille_estimee_texte_px > (largeur_visuelle_px - 6) else "#111"
                indication_style = "font-size: 13px; font-weight: bold;" if couleur_texte == "#111" else "font-size: 13px; font-weight: bold; background-color: #f2dede; border-radius: 2px;"
                
                bottom_offset = float(mm_pos) * px_par_mm
                # Compensation pour centrer verticalement la ligne sur son repère en mm
                top_offset_px = hauteur_visuelle_px - bottom_offset - 8
                
                html_gabarit += f"""
                <div style="position: absolute; top: {top_offset_px}px; width: 100%; text-align: center; color: {couleur_texte}; {indication_style} text-transform: uppercase; white-space: nowrap; overflow: visible;" title="Position: {mm_pos}mm">
                    {txt}
                </div>
                """
                
        html_gabarit += f"""
                <div style="position: absolute; width: 100%; bottom: 0; text-align: center; font-size: 10px; font-style: italic; background: #ddd; padding: 2px 0; border-top: 1px solid #111;">L: {t3_largeur_dos_reelle}mm</div>
            </div>
        </div>
        """
        st.components.v1.html(html_gabarit, height=hauteur_visuelle_px + 80)
