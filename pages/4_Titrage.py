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
    supabase = obtenir_client_supabase()
    reponse = supabase.table("fiches_livres").select("largeur, hauteur, epaisseur").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
    if reponse.data:
        return reponse.data[0]["largeur"], reponse.data[0]["hauteur"], reponse.data[0]["epaisseur"]
    return 160, 220, 20

def recuperer_titrage_enregistre(client, train, num_livre):
    """Va chercher si un titrage existe déjà pour ce livre spécifique"""
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("titrage_system3").select("lignes_json").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
        if reponse.data and reponse.data[0]["lignes_json"]:
            donnees_charges = json.loads(reponse.data[0]["lignes_json"])
            return pd.DataFrame(donnees_charges)
    except Exception:
        pass
    return None

def sauvegarder_titrage_sur_base(client, train, num_livre, date_saisie, df_lignes):
    """Insère ou met à jour les lignes de titrage sur Supabase"""
    supabase = obtenir_client_supabase()
    # Conversion du tableau de saisie en texte JSON pour le stocker proprement dans une seule cellule
    liste_dictionnaires = df_lignes.to_dict(orient="records")
    json_texte = json.dumps(liste_dictionnaires, ensure_ascii=False)
    
    donnees_titrage = {
        "nom_client": client,
        "numero_train": train,
        "numero_livre": int(num_livre),
        "date_saisie": str(date_saisie),
        "lignes_json": json_texte
    }
    
    try:
        # Vérification de l'existence
        check = supabase.table("titrage_system3").select("numero_livre").eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
        if check.data:
            supabase.table("titrage_system3").update(donnees_titrage).eq("nom_client", client).eq("numero_train", train).eq("numero_livre", num_livre).execute()
        else:
            supabase.table("titrage_system3").insert(donnees_titrage).execute()
        return True
    except Exception as e:
        st.error(f"Erreur technique lors de l'enregistrement : {e}")
        return False

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
        
        # Initialisations de sécurité
        livre_charge_valide = False
        t3_larg_brute = 160
        t3_haut_brute = 220
        t3_epaisseur = 20
        
        with c_meta2:
            t3_date = st.date_input("Date d'atelier", value=datetime.now())
            if t3_train_sel != "-- Choisir --":
                liste_livres = ["-- Choisir un livre --"] + lister_les_livres_du_train(t3_client, t3_train_sel)
                t3_livre_num = st.selectbox("3. N° du livre", options=liste_livres)
                
                if t3_livre_num and t3_livre_num != "-- Choisir un livre --":
                    t3_larg_brute, t3_haut_brute, t3_epaisseur = recuperer_specs_livre(t3_client, t3_train_sel, t3_livre_num)
                    livre_charge_valide = True
            else:
                t3_livre_num = None

    # --- SÉCURITÉ : BLOCAGE SI AUCUN LIVRE SÉLECTIONNÉ ---
    if not livre_charge_valide:
        st.write("---")
        st.info("💡 **En attente d'instructions :** Veuillez sélectionner un **N° de train** et un **N° de livre** existants ci-dessus pour charger les caractéristiques et commencer la composition du titrage.")
    else:
        # Si un livre est valide, on affiche le reste de l'interface d'atelier
        t3_largeur_dos_reelle = t3_epaisseur + 10

        with col_form_saisie:
            st.write("---")
            st.subheader("📐 Caractéristiques physiques du dos (Lecture seule)")
            c_dim1, c_dim2, c_dim3 = st.columns(3)
            with c_dim1: st.number_input("Hauteur récupérée (mm)", value=int(t3_haut_brute), disabled=True)
            with c_dim2: st.number_input("Épaisseur d'origine (mm)", value=int(t3_epaisseur), disabled=True)
            with c_dim3: st.number_input("Largeur utile du dos (Ép + 10mm)", value=int(t3_largeur_dos_reelle), disabled=True)
            
            st.write("---")
            st.subheader("✍️ Composition des lignes (Position en mm)")
            
            # Système de chargement intelligent (Mémoire) :
            # On vérifie si un enregistrement existe déjà dans le cloud pour ce livre précis
            df_existant = recuperer_titrage_enregistre(t3_client, t3_train_sel, t3_livre_num)
            
            if df_existant is not None:
                df_initial = df_existant
                st.caption("🔄 *Données de titrage existantes chargées depuis le Cloud. Vous pouvez les modifier.*")
            else:
                # Modèle vierge par défaut si c'est la première fois
                df_initial = pd.DataFrame([
                    {"Hauteur du titre (mm)": int(t3_haut_brute * 0.7), "Titrage": "NOUVEAU TITRE"},
                    {"Hauteur du titre (mm)": int(t3_haut_brute * 0.15), "Titrage": "COTE"}
                ])
                st.caption("✨ *Aucun titrage enregistré pour ce livre. Création d'un nouveau gabarit.*")
                
            df_edite_lignes = st.data_editor(
                df_initial,
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
                use_container_width=True,
                key=f"editor_{t3_client}_{t3_train_sel}_{t3_livre_num}" # Clé unique pour forcer le rafraîchissement au changement de livre
            )
            
            st.write("---")
            if st.button("💾 Sauvegarder le titrage du livre", type="primary", use_container_width=True):
                succes = sauvegarder_titrage_sur_base(t3_client, t3_train_sel, t3_livre_num, t3_date, df_edite_lignes)
                if succes:
                    st.success(f"✅ Composition enregistrée avec succès pour le Livre N°{t3_livre_num} (Train {t3_train_sel}) !")

        with col_gabarit_visualisation:
            st.subheader("📐 Gabarit dynamique du dos à dorer")
            
            facteur_px = 2.5
            hauteur_visuelle_px = int(t3_haut_brute * facteur_px)
            largeur_visuelle_px = int(t3_largeur_dos_reelle * facteur_px)
            
            hauteur_visuelle_px = max(min(hauteur_visuelle_px, 600), 350)
            largeur_visuelle_px = max(min(largeur_visuelle_px, 250), 60)
            
            px_par_mm = hauteur_visuelle_px / t3_haut_brute

            paliers_mm = list(range(0, int(t3_haut_brute) + 1, 10))
            if paliers_mm[-1] != int(t3_haut_brute):
                paliers_mm.append(int(t3_haut_brute))
                
            html_gabarit = f"""
            <div style="display: flex; font-family: monospace; background-color: #f8f9fa; padding: 20px; border-radius: 5px; min-height: {hauteur_visuelle_px + 60}px;">
                <div style="position: relative; height: {hauteur_visuelle_px}px; width: 60px; border-right: 2px solid #ccc; text-align: right; padding-right: 8px;">
            """
            
            for mm in paliers_mm:
                pos_depuis_bas = mm * px_par_mm
                correction_top = hauteur_visuelle_px - pos_depuis_bas - 6
                html_gabarit += f'<div style="position: absolute; top: {correction_top}px; right: 8px; font-size: 11px; color: #555;">{mm} mm —</div>'
                
            html_gabarit += f"""
                </div>
                <div style="position: relative; width: {largeur_visuelle_px}px; height: {hauteur_visuelle_px}px; background-color: #fdf6e2; border: 2px solid #111; margin-left: 20px; box-shadow: inset 0 0 10px rgba(0,0,0,0.15); transition: all 0.2s ease;">
                    <div style="position: absolute; width: 100%; top: 0; text-align: center; font-size: 10px; font-style: italic; background: #ddd; padding: 2px 0; border-bottom: 1px solid #111;">H: {t3_haut_brute}mm</div>
            """
            
            for _, row_data in df_edite_lignes.iterrows():
                mm_pos = row_data["Hauteur du titre (mm)"]
                txt = str(row_data["Titrage"]).strip()
                
                if pd.notna(mm_pos) and txt and txt != "None" and txt != "":
                    taille_estimee_texte_px = len(txt) * 8.5
                    couleur_texte = "#d9534f" if taille_estimee_texte_px > (largeur_visuelle_px - 6) else "#111"
                    indication_style = "font-size: 13px; font-weight: bold;" if couleur_texte == "#111" else "font-size: 13px; font-weight: bold; background-color: #f2dede; border-radius: 2px;"
                    
                    bottom_offset = float(mm_pos) * px_par_mm
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
