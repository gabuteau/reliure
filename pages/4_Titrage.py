import io
import json
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import streamlit as st
from supabase import create_client


# ==============================================================================
# 1. MOTEUR DE CONVERSION & EXPORT SYSTEM 3
# ==============================================================================

TABLE_ACCENTS_EXPORT = [
    ("É", "\\Af"), ("È", "\\Ae"), ("Ê", "\\Ag"), ("Ë", "\\Aj"),
    ("À", "\\Aa"), ("Â", "\\Ac"), ("Ä", "\\Ad"),
    ("Ç", "\\Am"),
    ("Î", "\\Au"), ("Ï", "\\Al"),
    ("Ô", "\\At"), ("Ö", "\\Az"),
    ("Ù", "\\Ax"), ("Û", "\\Aw"), ("Ü", "\\Ax"),
    ("°", "]"), ("N°", "N]")
]

TABLE_ACCENTS_IMPORT = [
    ("\\Af", "É"), ("\\Ae", "È"), ("\\Ag", "Ê"), ("\\Aj", "Ë"),
    ("\\Aa", "À"), ("\\Ac", "Â"), ("\\Ad", "Ä"),
    ("\\Am", "Ç"),
    ("\\Au", "Î"), ("\\Al", "Ï"),
    ("\\At", "Ô"), ("\\Az", "Ö"),
    ("\\Ax", "Ù"), ("\\Aw", "Û"),
    ("]", "°")
]


def decoder_texte_system3(texte):
    if not texte:
        return ""
    t = str(texte)
    for code, char in TABLE_ACCENTS_IMPORT:
        t = t.replace(code, char)
    t = re.sub(r"\\F[0-9]", "", t)
    t = re.sub(r"\\S[0-9]{3}", "", t)
    return t.strip()


def formater_texte_system3(texte):
    if not texte:
        return ""
    t = decoder_texte_system3(str(texte)).upper().strip()
    for char, code in TABLE_ACCENTS_EXPORT:
        t = t.replace(char, code)
    return t


def generer_bloc_livre_system3(
    num_sequence,
    nom_client,
    type_toile,
    couleur_toile,
    haut_maquette,
    larg_dos,
    df_lignes,
    griffe_texte="",
    griffe_pos_mm=15,
    sens_long=False,
    marquage_nom="OR",
    is_plat_couv=False,
    has_pieces=False,
    nb_pieces=0,
    couleur_piece=""
):
    code_client = (str(nom_client)[:10]).upper().ljust(10)

    if is_plat_couv:
        epaisseur_str = "99.0B"
        consigne = f"1{type_toile.upper()[:10]} - TITRAGE 1ERE COUV"
    else:
        epaisseur_str = f"{float(larg_dos):.1f}B".rjust(5)
        consigne = f"1{type_toile.upper()[:10]}"
        if has_pieces and nb_pieces > 0:
            c_p_court = (couleur_piece[:5]).upper()
            consigne += f" + {nb_pieces} P. {c_p_court}"

    offset_str = ".00".rjust(10)
    hauteur_str = f"{float(haut_maquette):.2f}".rjust(6)
    param_fixe = f" 1548 {consigne}".ljust(35)

    ligne_spec = f"       1{str(num_sequence).rjust(4)}{code_client}{epaisseur_str}{offset_str}{hauteur_str}{param_fixe}\n"

    code_ruban = "O1" if marquage_nom == "OR" else ("B1" if marquage_nom in ["BLANC", "ARGENT"] else "N1")

    if (sens_long or float(larg_dos) <= 20.0) and not is_plat_couv:
        h_attaque = int(haut_maquette) - 20
        bloc = ligne_spec
        lignes_texte_long = []
        if df_lignes is not None and not df_lignes.empty:
            for _, row in df_lignes.iterrows():
                txt_brut = str(row["Titrage"]).strip()
                for sous_txt in [l.strip() for l in txt_brut.split("\n") if l.strip()]:
                    lignes_texte_long.append(formater_texte_system3(sous_txt))

        if lignes_texte_long:
            for idx, txt in enumerate(lignes_texte_long, start=1):
                if idx == 1:
                    bloc += f"UCC{str(h_attaque).rjust(3)} 40{code_ruban}  1{txt}\n"
                else:
                    bloc += f"             {idx}{txt}\n"
        else:
            bloc += f"UCC{str(h_attaque).rjust(3)} 40{code_ruban}  1.\n"

        bloc += "//\n" + ("." * 350) + "\n"
        return bloc

    elements_a_dorer = []
    if df_lignes is not None and not df_lignes.empty:
        for _, row in df_lignes.iterrows():
            pos_y = int(row["Hauteur du titre (mm)"])
            txt_brut = str(row["Titrage"]).strip()
            sous_lignes = [l.strip() for l in txt_brut.split("\n") if l.strip()]
            for s_idx, sous_txt in enumerate(sous_lignes):
                pos_calculee = pos_y - (s_idx * 15)
                elements_a_dorer.append((pos_calculee, formater_texte_system3(sous_txt)))

    if griffe_texte and not is_plat_couv:
        mots_griffe = [l.strip() for l in griffe_texte.split("\n") if l.strip()]
        for g_idx, g_ligne in enumerate(mots_griffe):
            pos_g = int(griffe_pos_mm) + ((len(mots_griffe) - 1 - g_idx) * 8)
            elements_a_dorer.append((pos_g, formater_texte_system3(g_ligne)))

    elements_a_dorer.sort(key=lambda x: x[0], reverse=True)

    lignes_texte = []
    for pos_y, texte in elements_a_dorer:
        lignes_texte.append(f"           {str(pos_y).rjust(4)}{texte}")

    bloc = ligne_spec
    mode_axe = f"HCC      {code_ruban}"
    if lignes_texte:
        premiere_ligne = lignes_texte[0].replace("           ", mode_axe, 1)
        bloc += premiere_ligne + "\n"
        for l in lignes_texte[1:]:
            bloc += l + "\n"
    else:
        bloc += mode_axe + "250\n"

    bloc += "//\n"
    bloc += "." * 350 + "\n"
    return bloc


def assembler_fichier_system3(numero_job, liste_blocs):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    job_formate = str(numero_job)[:8].ljust(8)
    en_tete = f"110 {job_formate}{timestamp}".ljust(114) + "\n"
    return en_tete + "".join(liste_blocs)


# ==============================================================================
# 2. ACCÈS BASE SUPABASE
# ==============================================================================

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
    return sorted(list(set([row["numero_train"] for row in reponse.data])), reverse=True)


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


def recuperer_griffe_client(nom_client):
    supabase = obtenir_client_supabase()
    try:
        reponse = (
            supabase.table("clients")
            .select("griffe, griffe_position_mm")
            .eq("nom", nom_client)
            .execute()
        )
        if reponse.data:
            r = reponse.data[0]
            txt = (r.get("griffe") or "").strip()
            pos_mm = r.get("griffe_position_mm")
            return txt, (pos_mm if pos_mm is not None else 15)
    except Exception:
        pass
    return "", 15


def charger_types_toile_supabase():
    supabase = obtenir_client_supabase()
    try:
        reponse = supabase.table("referentiel_toiles").select("type_toile").execute()
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
        return couleurs if couleurs else ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]
    except Exception:
        return ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]


def recuperer_specs_livre(client, train, num_livre):
    supabase = obtenir_client_supabase()
    num_livre_int = int(num_livre)

    try:
        reponse = (
            supabase.table("fiches_livres")
            .select(
                "largeur, hauteur, hauteur_maquette, epaisseur, type_toile, couleur,"
                " titrage_couleur, cocher_piece_titre, couleur_pieces_toile,"
                " marquage_pieces, nombre_pieces_titre, titrage_sens, police_style"
            )
            .eq("nom_client", str(client).strip())
            .eq("numero_train", str(train).strip())
            .eq("numero_livre", num_livre_int)
            .execute()
        )

        if reponse.data:
            r = reponse.data[0]
            hauteur_livre = r.get("hauteur") or 220
            return (
                hauteur_livre,
                r.get("largeur") or 160,
                r.get("epaisseur") or 20,
                r.get("type_toile") or "Buckram",
                r.get("couleur") or "Noir",
                r.get("titrage_couleur") or "OR",
                bool(r.get("cocher_piece_titre", False)),
                r.get("couleur_pieces_toile") or "Rouge",
                r.get("marquage_pieces") or "OR",
                r.get("nombre_pieces_titre") or 1,
                r.get("titrage_sens") or "Classique",
                r.get("police_style") or "Simple",
                r.get("hauteur_maquette") or (hauteur_livre + 5),
            )
    except Exception:
        pass

    return 220, 160, 20, "Buckram", "Noir", "OR", False, "Rouge", "OR", 1, "Classique", "Simple", 225


def recuperer_titrage_enregistre(client, train, num_livre):
    supabase = obtenir_client_supabase()
    try:
        num_livre_int = int(num_livre)
        reponse = (
            supabase.table("titrage_system3")
            .select("lignes_json, pieces_json")
            .eq("nom_client", str(client).strip())
            .eq("numero_train", str(train).strip())
            .eq("numero_livre", num_livre_int)
            .execute()
        )
        if reponse.data:
            rec = reponse.data[0]
            df_lignes = pd.DataFrame(json.loads(rec["lignes_json"])) if rec.get("lignes_json") else None
            df_pieces = pd.DataFrame(json.loads(rec["pieces_json"])) if rec.get("pieces_json") else None

            if df_lignes is not None and not df_lignes.empty and "Titrage" in df_lignes.columns:
                df_lignes["Titrage"] = df_lignes["Titrage"].apply(decoder_texte_system3)

            return df_lignes, df_pieces
    except Exception:
        pass
    return None, None


def sauvegarder_titrage_sur_base(client, train, num_livre, date_saisie, df_lignes, df_pieces, specs_modifiees):
    supabase = obtenir_client_supabase()
    num_livre_int = int(num_livre)

    df_lignes_clean = df_lignes.copy() if df_lignes is not None else pd.DataFrame()
    if not df_lignes_clean.empty and "Titrage" in df_lignes_clean.columns:
        df_lignes_clean["Titrage"] = df_lignes_clean["Titrage"].apply(decoder_texte_system3)

    json_lignes = json.dumps(df_lignes_clean.to_dict(orient="records"), ensure_ascii=False)
    json_pieces = json.dumps(df_pieces.to_dict(orient="records"), ensure_ascii=False) if df_pieces is not None else "[]"

    donnees_titrage = {
        "nom_client": str(client).strip(),
        "numero_train": str(train).strip(),
        "numero_livre": num_livre_int,
        "date_saisie": str(date_saisie),
        "lignes_json": json_lignes,
        "pieces_json": json_pieces,
    }

    try:
        supabase.table("titrage_system3").upsert(
            donnees_titrage,
            on_conflict="nom_client,numero_train,numero_livre",
        ).execute()

        (
            supabase.table("fiches_livres")
            .update(specs_modifiees)
            .eq("nom_client", str(client).strip())
            .eq("numero_train", str(train).strip())
            .eq("numero_livre", num_livre_int)
            .execute()
        )
        return True
    except Exception as e:
        st.error("Erreur technique lors de l'enregistrement : " + str(e))
        return False


HEX_COULEURS_TOILE = {
    "Noir": "#1a1a1a", "Rouge": "#8b0000", "Bleu": "#0f2b5c",
    "Vert": "#1e4620", "Jaune": "#d4af37", "Orange": "#d96b27",
    "Violet": "#4a235a", "Marron": "#5c4033"
}

HEX_COULEURS_MARQUAGE = {
    "OR": "#ffd700", "ARGENT": "#e0e0e0", "BLANC": "#ffffff",
    "NOIR": "#000000", "AUTRE": "#c0c0c0"
}


# ==============================================================================
# 3. MOTEUR GRAPHIQUE (GABARIT DE VISUALISATION AVEC GESTION POLICES UTF-8)
# ==============================================================================

import os

# Cache des polices déjà résolues, pour éviter de refaire la recherche
# disque à chaque appel (l'app Streamlit ré-exécute le script en boucle).
_CACHE_POLICES = {}


def _chemins_police_dejavu(bold):
    """
    Construit une liste de chemins candidats vers une police garantissant
    une couverture Unicode complète des accents français (é, è, à, ê, î,
    ô, ù, ç, etc.), en incluant une police embarquée par la librairie
    matplotlib (installée avec pandas dans la plupart des environnements),
    ce qui garantit un résultat correct même sur des hébergements minimalistes
    (Streamlit Community Cloud, Docker "slim", etc.) où les polices système
    ne sont pas installées par défaut.
    """
    nom_fichier = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"

    chemins = [
        # 1) Police placée par l'utilisateur à côté du script (solution la
        #    plus fiable : à ajouter dans un dossier "fonts/" du dépôt).
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", nom_fichier),
        # 2) Emplacements système Linux courants (Debian/Ubuntu)
        f"/usr/share/fonts/truetype/dejavu/{nom_fichier}",
        f"/usr/local/share/fonts/{nom_fichier}",
        nom_fichier,
    ]

    # 3) Police embarquée dans le paquet matplotlib (présente sur quasiment
    #    tous les environnements Python de data / traitement, indépendante
    #    du système d'exploitation puisqu'installée via pip).
    try:
        import matplotlib
        chemins.append(os.path.join(matplotlib.get_data_path(), "fonts", "ttf", nom_fichier))
    except Exception:
        pass

    return chemins


def charger_police_compatible(taille_pt, bold=True):
    cle_cache = (taille_pt, bold)
    if cle_cache in _CACHE_POLICES:
        return _CACHE_POLICES[cle_cache]

    for chemin in _chemins_police_dejavu(bold):
        try:
            police = ImageFont.truetype(chemin, taille_pt)
            _CACHE_POLICES[cle_cache] = police
            return police
        except Exception:
            continue

    # Dernier recours : police bitmap Pillow (ASCII uniquement). Si on
    # arrive ici, les accents ne s'afficheront pas -> on prévient l'utilisateur
    # une seule fois pour ne pas polluer l'interface.
    if not _CACHE_POLICES.get("_alerte_affichee"):
        st.warning(
            "⚠️ Police Unicode introuvable sur ce serveur : les caractères "
            "accentués (É, È, À, Ê...) risquent de ne pas s'afficher dans "
            "le gabarit. Ajoutez un fichier 'fonts/DejaVuSans-Bold.ttf' à "
            "côté du script, ou ajoutez 'fonts-dejavu-core' dans un fichier "
            "packages.txt à la racine du projet."
        )
        _CACHE_POLICES["_alerte_affichee"] = True

    police = ImageFont.load_default()
    _CACHE_POLICES[cle_cache] = police
    return police


def generer_image_gabarit(
    haut_maquette,
    larg_dos,
    c_toile_hex,
    c_marq_hex,
    is_long,
    has_pieces,
    df_pieces,
    df_lignes,
    griffe_texte="",
    griffe_pos_mm=15,
    police_style="Simple",
):
    facteur_px = 2.5
    h_dos_px = max(min(int(haut_maquette * facteur_px), 600), 350)
    w_dos_px = max(min(int(larg_dos * facteur_px), 250), 60)

    w_regle_px = 80
    w_totale = w_regle_px + w_dos_px + 30
    h_totale = h_dos_px + 40

    img = Image.new("RGBA", (w_totale, h_totale), (248, 249, 250, 255))
    draw = ImageDraw.Draw(img)

    is_double = (police_style == "Double")
    taille_titre_pt = 18 if is_double else 12

    font = charger_police_compatible(taille_titre_pt, bold=True)
    font_small = charger_police_compatible(10, bold=False)
    font_griffe = charger_police_compatible(11, bold=True)

    px_par_mm = h_dos_px / haut_maquette

    def tracer_texte(pt, txt, fill_color, fnt, anc="mm", alg="center"):
        txt = decoder_texte_system3(txt)
        draw.text(pt, txt, fill=fill_color, font=fnt, anchor=anc, align=alg)
        if is_double:
            x, y = pt
            draw.text((x + 0.8, y), txt, fill=fill_color, font=fnt, anchor=anc, align=alg)

    def mesurer_taille_vertical(texte, fnt):
        texte = decoder_texte_system3(texte)
        if not texte:
            return 0, 0
        bbox = draw.textbbox((0, 0), texte, font=fnt)
        largeur_txt = int(round(bbox[2] - bbox[0]))
        hauteur_txt = int(round(bbox[3] - bbox[1]))
        return hauteur_txt, largeur_txt

    def tracer_texte_vertical(x_centre_colonne, y_centre, texte, fill_color, fnt):
        texte = decoder_texte_system3(texte)
        if not texte:
            return
        bbox = draw.textbbox((0, 0), texte, font=fnt)
        largeur_txt = int(round(bbox[2] - bbox[0]))
        hauteur_txt = int(round(bbox[3] - bbox[1]))
        if largeur_txt <= 0 or hauteur_txt <= 0:
            return

        marge = 6
        calque = Image.new("RGBA", (largeur_txt + marge * 2, hauteur_txt + marge * 2), (0, 0, 0, 0))
        calque_draw = ImageDraw.Draw(calque)
        calque_draw.text((marge - bbox[0], marge - bbox[1]), texte, fill=fill_color, font=fnt, anchor="la")
        if is_double:
            calque_draw.text((marge - bbox[0] + 0.8, marge - bbox[1]), texte, fill=fill_color, font=fnt, anchor="la")

        calque_pivote = calque.rotate(90, expand=True)
        pos_x = int(x_centre_colonne - calque_pivote.width / 2)
        pos_y = int(y_centre - calque_pivote.height / 2)
        img.paste(calque_pivote, (pos_x, pos_y), calque_pivote)

    draw.line([(w_regle_px, 20), (w_regle_px, 20 + h_dos_px)], fill="#cccccc", width=2)
    paliers_mm = list(range(0, int(haut_maquette) + 1, 10))
    if paliers_mm[-1] != int(haut_maquette):
        paliers_mm.append(int(haut_maquette))

    for mm in paliers_mm:
        y_mm = 20 + h_dos_px - (mm * px_par_mm)
        draw.line([(w_regle_px - 6, y_mm), (w_regle_px, y_mm)], fill="#555555", width=1)
        draw.text((w_regle_px - 50, y_mm - 6), f"{mm} mm", fill="#555555", font=font_small)

    x_dos = w_regle_px + 15
    y_dos = 20
    draw.rectangle([(x_dos, y_dos), (x_dos + w_dos_px, y_dos + h_dos_px)], fill=c_toile_hex, outline="#111111", width=2)

    if has_pieces and df_pieces is not None and not df_pieces.empty:
        for _, row_p in df_pieces.iterrows():
            pos_p_mm = row_p["Position (mm depuis le bas)"]
            haut_p_mm = row_p["Hauteur pièce (mm)"]
            c_p_nom = row_p["Couleur pièce"]
            m_p_nom = row_p["Couleur marquage"]
            txt_p = decoder_texte_system3(str(row_p.get("Titre sur pièce", "")).strip())

            if pd.notna(pos_p_mm) and pd.notna(haut_p_mm):
                bg_p_hex = HEX_COULEURS_TOILE.get(c_p_nom, "#8b0000")
                txt_p_hex = HEX_COULEURS_MARQUAGE.get(m_p_nom, "#ffd700")
                h_p_px = haut_p_mm * px_par_mm
                y_p_px = y_dos + h_dos_px - (pos_p_mm * px_par_mm) - h_p_px

                draw.rectangle([(x_dos, y_p_px), (x_dos + w_dos_px, y_p_px + h_p_px)], fill=bg_p_hex, outline="#ffffff", width=1)

                if txt_p and txt_p != "None":
                    lignes_p = [l.strip().upper() for l in txt_p.split("\n") if l.strip()]
                    if is_long:
                        ecart_col_px = 24 if is_double else 16
                        nb_cols = len(lignes_p)
                        x_base_center = x_dos + (w_dos_px / 2)
                        y_centre_zone = y_p_px + (h_p_px / 2)
                        hauteur_zone_dispo = h_p_px - 12
                        for idx_col, ligne in enumerate(lignes_p):
                            offset_col = (idx_col - (nb_cols - 1) / 2) * ecart_col_px
                            x_col = x_base_center + offset_col
                            _, hauteur_prevue = mesurer_taille_vertical(ligne, font)
                            c_finale = "#d9534f" if hauteur_prevue > hauteur_zone_dispo else txt_p_hex
                            tracer_texte_vertical(x_col, y_centre_zone, ligne, c_finale, font)
                    else:
                        txt_p_full = "\n".join(lignes_p)
                        bbox_p = draw.textbbox((0, 0), txt_p_full, font=font, align="center")
                        w_txt_p = bbox_p[2] - bbox_p[0]
                        c_finale = "#d9534f" if w_txt_p > (w_dos_px - 4) else txt_p_hex
                        tracer_texte((x_dos + (w_dos_px / 2), y_p_px + (h_p_px / 2)), txt_p_full, c_finale, font, "mm", "center")

    if df_lignes is not None and not df_lignes.empty:
        for _, row_l in df_lignes.iterrows():
            mm_pos = row_l["Hauteur du titre (mm)"]
            txt = decoder_texte_system3(str(row_l["Titrage"]).strip())

            if pd.notna(mm_pos) and txt and txt != "None":
                x_center = x_dos + (w_dos_px / 2)
                lignes_txt = [l.strip().upper() for l in txt.split("\n") if l.strip()]

                if is_long:
                    y_repere_centre_px = y_dos + h_dos_px - (float(mm_pos) * px_par_mm)
                    ecart_col_px = 24 if is_double else 16
                    nb_cols = len(lignes_txt)
                    for idx_col, ligne in enumerate(lignes_txt):
                        offset_col = (idx_col - (nb_cols - 1) / 2) * ecart_col_px
                        x_col = x_center + offset_col
                        _, hauteur_prevue = mesurer_taille_vertical(ligne, font)
                        y_centre = y_repere_centre_px
                        is_debordement = ((y_centre + (hauteur_prevue / 2)) > (y_dos + h_dos_px - 2) or (y_centre - (hauteur_prevue / 2)) < y_dos)
                        couleur_ligne = "#d9534f" if is_debordement else c_marq_hex
                        tracer_texte_vertical(x_col, y_centre, ligne, couleur_ligne, font)
                else:
                    y_l_px = y_dos + h_dos_px - (float(mm_pos) * px_par_mm)
                    txt_full = "\n".join(lignes_txt)
                    bbox_txt = draw.textbbox((0, 0), txt_full, font=font, align="center")
                    w_txt = bbox_txt[2] - bbox_txt[0]
                    couleur_ligne = "#d9534f" if w_txt > (w_dos_px - 4) else c_marq_hex
                    tracer_texte((x_center, y_l_px), txt_full, couleur_ligne, font, "mm", "center")

    if griffe_texte:
        griffe_claire = decoder_texte_system3(griffe_texte)
        x_center = x_dos + (w_dos_px / 2)
        chars_max = max(int((w_dos_px - 8) / 7), 1)
        mots = griffe_claire.replace("\n", " ").split()
        lignes_g, ligne_c = [], []
        for m in mots:
            if len(" ".join(ligne_c + [m])) <= chars_max:
                ligne_c.append(m)
            else:
                if ligne_c:
                    lignes_g.append(" ".join(ligne_c).upper())
                ligne_c = [m]
        if ligne_c:
            lignes_g.append(" ".join(ligne_c).upper())

        interligne_px = 14
        y_derniere_px = y_dos + h_dos_px - (griffe_pos_mm * px_par_mm)
        for idx_l, txt_l in enumerate(lignes_g):
            y_px = y_derniere_px - ((len(lignes_g) - 1 - idx_l) * interligne_px)
            draw.text((x_center, y_px), txt_l, fill=c_marq_hex, font=font_griffe, anchor="mm", align="center")

    return img


# ==============================================================================
# 4. INTERFACE UTILISATEUR STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Titrage Système 3", layout="wide")
st.title("📟 Module de Composition Spécifique — Titrage Système 3")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
    st.warning("⚠️ Créez d'abord un client pour utiliser le module de titrage.")
else:
    t3_haut_maquette = 225
    t3_larg_dos_utile = 30
    t3_couleur_nom = "Noir"
    t3_marquage_nom = "OR"
    t3_sens_titrage = "Classique"
    t3_police_style = "Simple"
    has_pieces = False
    df_pieces_edite = None
    df_edite_lignes = None
    griffe_a_afficher = ""
    griffe_hauteur_mm = 15

    col_form_saisie, col_gabarit_visualisation = st.columns([1.2, 0.8])

    with col_form_saisie:
        st.subheader("Clé de sélection du Livre")
        c_meta1, c_meta2 = st.columns(2)
        with c_meta1:
            t3_client = st.selectbox("1. Client référent", options=liste_clients_existants)
            t3_trains = lister_les_trains_du_client(t3_client)
            t3_train_sel = st.selectbox("2. N° de train", options=["-- Choisir --"] + t3_trains)

        livre_charge_valide = False
        with c_meta2:
            t3_date = st.date_input("Date d'atelier", value=datetime.now())
            if t3_train_sel != "-- Choisir --":
                liste_livres = ["-- Choisir un livre --"] + lister_les_livres_du_train(t3_client, t3_train_sel)
                t3_livre_num = st.selectbox("3. N° du livre", options=liste_livres)

                if t3_livre_num and t3_livre_num != "-- Choisir un livre --":
                    (
                        init_haut,
                        init_larg,
                        init_ep,
                        init_type_toile,
                        init_couleur_toile,
                        init_marquage,
                        init_has_piece,
                        init_piece_couleur,
                        init_piece_marquage,
                        init_nb_pieces,
                        init_sens_titrage,
                        init_police_style,
                        init_haut_maquette,
                    ) = recuperer_specs_livre(t3_client, t3_train_sel, t3_livre_num)
                    livre_charge_valide = True
            else:
                t3_livre_num = None

    if not livre_charge_valide:
        st.write("---")
        st.info("💡 **En attente d'instructions :** Sélectionnez un **N° de train** et un **N° de livre** existants.")
    else:
        with col_form_saisie:
            st.write("---")
            st.subheader("📐 Caractéristiques du livre & Emplacement du titrage")

            is_plat_couv = st.checkbox("🏷️ Imprimer sur la 1ère de Couverture (Plat) au lieu du dos", value=False)

            c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)
            with c_dim1:
                st.metric("Hauteur du livre (mm)", int(init_haut))
            with c_dim2:
                t3_haut_maquette = st.number_input(
                    "Hauteur maquette (mm)",
                    min_value=10, max_value=1000,
                    value=int(init_haut_maquette),
                    step=1,
                )
            with c_dim3:
                larg_dos_defaut = 99 if is_plat_couv else int(init_ep + 10)
                t3_larg_dos_utile = st.number_input("Largeur utile (mm)", min_value=5, max_value=500, value=larg_dos_defaut, step=1)
            with c_dim4:
                idx_m = ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"].index(init_marquage) if init_marquage in ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"] else 0
                t3_marquage_nom = st.selectbox("Marquage général", ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"], index=idx_m)

            c_toi1, c_toi2, c_toi3, c_toi4 = st.columns(4)
            types_toiles_dispos = charger_types_toile_supabase()
            with c_toi1:
                idx_t = types_toiles_dispos.index(init_type_toile) if init_type_toile in types_toiles_dispos else 0
                t3_type_toile = st.selectbox("Type de toile", types_toiles_dispos, index=idx_t)

            couleurs_toile_dispos = charger_couleurs_par_toile_supabase(t3_type_toile)
            with c_toi2:
                idx_c = couleurs_toile_dispos.index(init_couleur_toile) if init_couleur_toile in couleurs_toile_dispos else 0
                t3_couleur_nom = st.selectbox("Couleur de la toile", couleurs_toile_dispos, index=idx_c)

            with c_toi3:
                idx_s = 1 if init_sens_titrage == "Long" else 0
                t3_sens_titrage = st.selectbox("Sens du titrage", ["Classique", "Long"], index=idx_s)

            with c_toi4:
                idx_pstyle = 1 if init_police_style == "Double" else 0
                t3_police_style = st.selectbox("Empreinte police", ["Simple", "Double"], index=idx_pstyle)

            griffe_registree, griffe_pos_defaut = recuperer_griffe_client(t3_client)
            griffe_hauteur_mm = griffe_pos_defaut

            if griffe_registree and not is_plat_couv:
                st.write("---")
                st.subheader("🏷️ Griffe Client")
                c_grf1, c_grf2 = st.columns([2, 1])
                with c_grf1:
                    inclure_griffe = st.checkbox(f"Imprimer la griffe ({decoder_texte_system3(griffe_registree).replace(chr(10), ' / ')})", value=True)
                with c_grf2:
                    if inclure_griffe:
                        griffe_hauteur_mm = st.number_input("Position bas (mm)", min_value=0, max_value=200, value=int(griffe_pos_defaut), step=1)
                        griffe_a_afficher = griffe_registree

            st.write("---")
            st.subheader("🧩 Pièces de titre")
            has_pieces = st.checkbox("Activer la/les pièce(s) de titre", value=init_has_piece)
            df_lignes_existant, df_pieces_existant = recuperer_titrage_enregistre(t3_client, t3_train_sel, t3_livre_num)

            if has_pieces and not is_plat_couv:
                df_pieces_initial = df_pieces_existant if (df_pieces_existant is not None and not df_pieces_existant.empty) else pd.DataFrame([{
                    "Position (mm depuis le bas)": int(t3_haut_maquette * 0.75),
                    "Hauteur pièce (mm)": 35,
                    "Couleur pièce": init_piece_couleur,
                    "Couleur marquage": init_piece_marquage,
                    "Titre sur pièce": "TITRE LIGNE 1\nSOUS-TITRE LIGNE 2",
                }])

                list_c = ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]
                list_m = ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"]

                df_pieces_edite = st.data_editor(
                    df_pieces_initial,
                    column_config={
                        "Position (mm depuis le bas)": st.column_config.NumberColumn("Position bas (mm)", min_value=0, max_value=t3_haut_maquette, step=1, required=True),
                        "Hauteur pièce (mm)": st.column_config.NumberColumn("Hauteur (mm)", min_value=5, max_value=t3_haut_maquette, step=1, required=True),
                        "Couleur pièce": st.column_config.SelectboxColumn("Couleur pièce", options=list_c, required=True),
                        "Couleur marquage": st.column_config.SelectboxColumn("Marquage", options=list_m, required=True),
                        "Titre sur pièce": st.column_config.TextColumn("Titre / Texte (Multiligne)", required=False),
                    },
                    num_rows="dynamic",
                    use_container_width=True,
                    key=f"editor_pieces_{t3_client}_{t3_train_sel}_{t3_livre_num}",
                )

            st.write("---")
            st.subheader("✍️ Lignes de titrage (Position en mm)")

            df_lignes_initial = df_lignes_existant if (df_lignes_existant is not None and not df_lignes_existant.empty) else pd.DataFrame([{
                "Hauteur du titre (mm)": int(t3_haut_maquette * 0.20),
                "Titrage": "TITRE",
            }])

            df_edite_lignes = st.data_editor(
                df_lignes_initial,
                column_config={
                    "Hauteur du titre (mm)": st.column_config.NumberColumn("Position (mm depuis le bas)", min_value=0, max_value=t3_haut_maquette, step=1, required=True),
                    "Titrage": st.column_config.TextColumn("Texte à imprimer (avec accents français)", required=True),
                },
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_lignes_{t3_client}_{t3_train_sel}_{t3_livre_num}",
            )

            st.write("---")
            if st.button("💾 Sauvegarder les modifications et le titrage", type="primary", use_container_width=True):
                c_p = df_pieces_edite.iloc[0]["Couleur pièce"] if (df_pieces_edite is not None and not df_pieces_edite.empty) else init_piece_couleur
                m_p = df_pieces_edite.iloc[0]["Couleur marquage"] if (df_pieces_edite is not None and not df_pieces_edite.empty) else init_piece_marquage

                specs_mises_a_jour = {
                    "hauteur_maquette": t3_haut_maquette,
                    "largeur": init_larg,
                    "epaisseur": max(t3_larg_dos_utile - 10, 0) if not is_plat_couv else init_ep,
                    "type_toile": t3_type_toile,
                    "couleur": t3_couleur_nom,
                    "titrage_couleur": t3_marquage_nom,
                    "cocher_piece_titre": has_pieces,
                    "couleur_pieces_toile": c_p,
                    "marquage_pieces": m_p,
                    "nombre_pieces_titre": len(df_pieces_edite) if df_pieces_edite is not None else 0,
                    "titrage_sens": t3_sens_titrage,
                    "police_style": t3_police_style,
                }

                if sauvegarder_titrage_sur_base(
                    t3_client,
                    t3_train_sel,
                    t3_livre_num,
                    t3_date,
                    df_edite_lignes,
                    df_pieces_edite if has_pieces else None,
                    specs_mises_a_jour,
                ):
                    st.success(f"✅ Enregistré (Livre N°{t3_livre_num} — Train {t3_train_sel})")

            # --- ZONE D'EXPORT SYSTEM 3 (.S3T) ---
            st.write("---")
            st.subheader("🖨️ Génération du fichier machine (.S3T)")

            c_exp1, c_exp2 = st.columns(2)
            with c_exp1:
                bloc_livre_actuel = generer_bloc_livre_system3(
                    num_sequence=1,
                    nom_client=t3_client,
                    type_toile=t3_type_toile,
                    couleur_toile=t3_couleur_nom,
                    haut_maquette=t3_haut_maquette,
                    larg_dos=t3_larg_dos_utile,
                    df_lignes=df_edite_lignes,
                    griffe_texte=griffe_a_afficher,
                    griffe_pos_mm=griffe_hauteur_mm,
                    sens_long=(t3_sens_titrage == "Long"),
                    marquage_nom=t3_marquage_nom,
                    is_plat_couv=is_plat_couv,
                    has_pieces=has_pieces,
                    nb_pieces=len(df_pieces_edite) if df_pieces_edite is not None else 0,
                    couleur_piece=(df_pieces_edite.iloc[0]["Couleur pièce"] if (df_pieces_edite is not None and not df_pieces_edite.empty) else "")
                )
                fichier_livre_unique = assembler_fichier_system3(
                    numero_job=f"{t3_train_sel}_{t3_livre_num}",
                    liste_blocs=[bloc_livre_actuel],
                )
                st.download_button(
                    label=f"📄 Télécharger le livre N°{t3_livre_num} (.S3T)",
                    data=fichier_livre_unique.encode("latin-1", errors="replace"),
                    file_name=f"LIVRE_{t3_train_sel}_{t3_livre_num}.S3T",
                    mime="text/plain",
                    use_container_width=True,
                )

            with c_exp2:
                if st.button(f"📦 Préparer le Train {t3_train_sel} entier", use_container_width=True):
                    livres_du_train = lister_les_livres_du_train(t3_client, t3_train_sel)
                    blocs_train = []
                    for seq, n_livre in enumerate(livres_du_train, start=1):
                        specs_l = recuperer_specs_livre(t3_client, t3_train_sel, n_livre)
                        h_maq, ep, t_toile, sens_t, marq_l = specs_l[12], specs_l[2], specs_l[3], specs_l[10], specs_l[5]
                        c_toile, h_piece, n_piece, c_piece_toile = specs_l[4], specs_l[6], specs_l[9], specs_l[7]
                        df_lig, _ = recuperer_titrage_enregistre(t3_client, t3_train_sel, n_livre)

                        b = generer_bloc_livre_system3(
                            num_sequence=seq,
                            nom_client=t3_client,
                            type_toile=t_toile,
                            couleur_toile=c_toile,
                            haut_maquette=h_maq,
                            larg_dos=ep + 10,
                            df_lignes=df_lig,
                            griffe_texte=griffe_a_afficher,
                            griffe_pos_mm=griffe_hauteur_mm,
                            sens_long=(sens_t == "Long"),
                            marquage_nom=marq_l,
                            is_plat_couv=False,
                            has_pieces=h_piece,
                            nb_pieces=n_piece,
                            couleur_piece=c_piece_toile
                        )
                        blocs_train.append(b)

                    fichier_train_complet = assembler_fichier_system3(
                        numero_job=t3_train_sel,
                        liste_blocs=blocs_train,
                    )
                    st.download_button(
                        label=f"⬇️ Télécharger le train complet ({len(livres_du_train)} livres)",
                        data=fichier_train_complet.encode("latin-1", errors="replace"),
                        file_name=f"TRAIN_{t3_train_sel}.S3T",
                        mime="text/plain",
                        use_container_width=True,
                    )

        with col_gabarit_visualisation:
            st.subheader("📐 Gabarit dynamique du dos à dorer")
            hex_toile = HEX_COULEURS_TOILE.get(t3_couleur_nom, "#1a1a1a")
            hex_marq = HEX_COULEURS_MARQUAGE.get(t3_marquage_nom, "#ffd700")

            img_gabarit = generer_image_gabarit(
                t3_haut_maquette,
                t3_larg_dos_utile,
                hex_toile,
                hex_marq,
                t3_sens_titrage == "Long",
                has_pieces,
                df_pieces_edite,
                df_edite_lignes,
                griffe_texte=griffe_a_afficher,
                griffe_pos_mm=griffe_hauteur_mm,
                police_style=t3_police_style,
            )

            buf = io.BytesIO()
            img_gabarit.save(buf, format="PNG")
            st.image(buf.getvalue(), use_container_width=False)
