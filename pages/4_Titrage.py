import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import json

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
    """Récupère les dimensions physiques ainsi que l'habillage et le marquage du livre"""
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("largeur, hauteur, epaisseur, couleur, titrage_couleur").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
    if reponse.data:
        r = reponse.data[0]
        return r["largeur"], r["hauteur"], r["epaisseur"], r.get("couleur", "Noir"), r.get("titrage_couleur", "OR")
    return 160, 220, 20, "Noir", "OR"

def recuperer_titrage_enregistre(client, train, num_livre):
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("titrage_system3").select("lignes_json").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
        if reponse.data and reponse.data[0]["lignes_json"]:
            return pd.DataFrame(json.loads(reponse.data[0]["lignes_json"]))
    except Exception:
        pass
    return None

def sauvegarder_titrage_sur_base(client, train, num_livre, date_saisie, df_lignes):
    supabase = obtenir_client_supabase()
    liste_dictionnaires = df_lignes.to_dict(orient="records")
    json_texte = json.dumps(liste_dictionnaires, ensure_ascii=False)
    
    donnees_titrage = {
        "nom_client": client, "numero_train": train, "numero_livre": int(num_livre),
        "date_saisie": str(date_saisie), "lignes_json": json_texte
    }
    try:
        check = supabase.table("titrage_system3").select("numero_livre").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
        if check.data:
            supabase.table("titrage_system3").update(donnees_titrage).eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
        else:
            supabase.table("titrage_system3").insert(donnees_titrage).execute()
        return True
    except Exception as e:
        st.error(f"Erreur technique lors de l'enregistrement : {e}")
        return False

# Dictionnaires de conversion pour le rendu HTML
HEX_COULEURS_TOILE = {
    "Noir": "#1a1a1a", "Rouge": "#8b0000", "Bleu": "#0f2b5c", "Vert": "#1e4620",
    "Jaune": "#d4af37", "Orange": "#d96b27", "Violet": "#4a235a", "Marron": "#5c4033"
}

HEX_COULEURS_MARQUAGE = {
    "OR": "#ffd700", "ARGENT": "#e0e0e0", "BLANC": "#ffffff", "NOIR": "#000000"
}

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
        
        livre_charge_valide = False
        t3_larg_brute = 160 ; t3_haut_brute = 220 ; t3_epaisseur = 20
        t3_couleur_nom = "Noir" ; t3_marquage_nom = "OR"
        
        with c_meta2:
            t3_date = st.date_input("Date d'atelier", value=datetime.now())
            if t3_train_sel != "-- Choisir --":
                liste_livres = ["-- Choisir un livre --"] + lister_les_livres_du_train(t3_client, t3_train_sel)
                t3_livre_num = st.selectbox("3. N° du livre", options=liste_livres)
                
                if t3_livre_num and t3_livre_num != "-- Choisir un livre --":
                    t3_larg_brute, t3_haut_brute, t3_epaisseur, t3_couleur_nom, t3_marquage_nom = recuperer_specs_livre(t3_client, t3_train_sel, t3_livre_num)
                    livre_charge_valide = True
            else:
                t3_livre_num = None

    if not livre_charge_valide:
        st.write("---")
        st.info("💡 **En attente d'instructions :** Veuillez sélectionner un **N° de train** et un **N° de livre** existants pour charger le dos.")
    else:
        t3_largeur_dos_reelle = t3_epaisseur + 10
        couleur_fond_html = HEX_COULEURS_TOILE.get(t3_couleur_nom, "#fdf6e2")
        couleur_texte_html = HEX_COULEURS_MARQUAGE.get(t3_marquage_nom, "#ffd700")

        with col_form_saisie:
            st.write("---")
            st.subheader("📐 Caractéristiques physiques du dos (Lecture seule)")
            c_dim1, c_dim2, c_dim3 = st.columns(3)
            with c_dim1: st.number_input("Hauteur récupérée (mm)", value=int(t3_haut_brute), disabled=True)
            with c_dim2: st.number_input("Largeur utile du dos (Ép + 10mm)", value=int(t3_largeur_dos_reelle), disabled=True)
            with c_dim3: st.text_input("Finition d'atelier", value=f"Toile {t3_couleur_nom} / Marquage {t3_marquage_nom}", disabled=True)
            
            st.write("---")
            st.subheader("✍️ Composition des lignes (Position en mm)")
            
            df_existant = recuperer_titrage_enregistre(t3_client, t3_train_sel, t3_livre_num)
            if df_existant is not None:
                df_initial = df_existant
                st.caption("🔄 *Données de titrage existantes chargées depuis le Cloud.*")
            else:
                df_initial = pd.DataFrame([
                    {"Hauteur du titre (mm)": int(t3_haut_brute * 0.7), "Titrage": "NOUVEAU TITRE"},
                    {"Hauteur du titre (mm)": int(t3_haut_brute * 0.15), "Titrage": "COTE"}
                ])
                st.caption("✨ *Création d'un nouveau gabarit pour ce livre.*")
                
            df_edite_lignes = st.data_editor(
                df_initial,
                column_config={
                    "Hauteur du titre (mm)": st.column_config.NumberColumn("Position (mm depuis le bas)", min_value=0, max_value=int(t3_haut_brute), step=1, required=True),
                    "Titrage": st.column_config.TextColumn("Texte à imprimer", required=True)
                },
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_{t3_client}_{t3_train_sel}_{t3_livre_num}"
            )
            
            st.write("---")
            if st.button("💾 Sauvegarder le titrage du livre", type="primary", use_container_width=True):
                if sauvegarder_titrage_sur_base(t3_client, t3_train_sel, t3_livre_num, t3_date, df_edite_lignes):
                    st.success(f"✅ Composition enregistrée (Livre N°{t3_livre_num} — Train {t3_train_sel})")

        with col_gabarit_visualisation:
            st.subheader("📐 Gabarit dynamique du dos à dorer")
            
            facteur_px = 2.5
            hauteur_visuelle_px = max(min(int(t3_haut_brute * facteur_px), 600), 350)
            largeur_visuelle_px = max(min(int(t3_largeur_dos_reelle * facteur_px), 250), 60)
            px_par_mm = hauteur_visuelle_px / t3_haut_brute

            paliers_mm = list(range(0, int(t3_haut_brute) + 1, 10))
            if paliers_mm[-1] != int(t3_haut_brute): paliers_mm.append(int(t3_haut_brute))
                
            html_gabarit = f"""
            <div style="display: flex; font-family: monospace; background-color: #f8f9fa; padding: 20px; border-radius: 5px; min-height: {hauteur_visuelle_px + 60}px;">
                <div style="position: relative; height: {hauteur_visuelle_px}px; width: 60px; border-right: 2px solid #ccc; text-align: right; padding-right: 8px;">
            """
            for mm in paliers_mm:
                pos_depuis_bas = mm * px_par_mm
                correction_top = hauteur_visuelle_px - pos_depuis_bas - 6
                html_gabarit += f'<div style="position: absolute; top: {correction_top}px; right: 8px; font-size: 11px; color: #555;">{mm} mm —</div>'
                
            # Application de la couleur de toile récupérée pour le fond du dos
            html_gabarit += f"""
                </div>
                <div style="position: relative; width: {largeur_visuelle_px}px; height: {hauteur_visuelle_px}px; background-color: {couleur_fond_html}; border: 2px solid #111; margin-left: 20px; box-shadow: inset 0 0 10px rgba(0,0,0,0.3); transition: all 0.2s ease;">
                    <div style="position: absolute; width: 100%; top: 0; text-align: center; font-size: 10px; font-style: italic; background: rgba(255,255,255,0.7); color:#111; padding: 2px 0; border-bottom: 1px solid #111;">H: {t3_haut_brute}mm</div>
            """
            
            for _, row_data in df_edite_lignes.iterrows():
                mm_pos = row_data["Hauteur du titre (mm)"]
                txt = str(row_data["Titrage"]).strip()
                
                if pd.notna(mm_pos) and txt and txt != "None" and txt != "":
                    taille_estimee_texte_px = len(txt) * 8.5
                    
                    # Détection du débordement physique
                    if taille_estimee_texte_px > (largeur_visuelle_px - 6):
                        coloration_ligne = "#d9534f" # Alerte rouge en cas de dépassement
                        fond_alerte = "background-color: rgba(217, 83, 79, 0.2); border: 1px dashed #d9534f;"
                    else:
                        coloration_ligne = couleur_texte_html # Couleur officielle du marquage
                        fond_alerte = ""
                    
                    bottom_offset = float(mm_pos) * px_par_mm
                    top_offset_px = hauteur_visuelle_px - bottom_offset - 8
                    
                    html_gabarit += f"""
                    <div style="position: absolute; top: {top_offset_px}px; width: 100%; text-align: center; color: {coloration_ligne}; font-size: 13px; font-weight: bold; {fond_alerte} text-transform: uppercase; white-space: nowrap; overflow: visible;" title="Position: {mm_pos}mm">
                        {txt}
                    </div>
                    """
                    
            html_gabarit += f"""
                    <div style="position: absolute; width: 100%; bottom: 0; text-align: center; font-size: 10px; font-style: italic; background: rgba(255,255,255,0.7); color:#111; padding: 2px 0; border-top: 1px solid #111;">L: {t3_largeur_dos_reelle}mm</div>
                </div>
            </div>
            """
            st.components.v1.html(html_gabarit, height=hauteur_visuelle_px + 80)
