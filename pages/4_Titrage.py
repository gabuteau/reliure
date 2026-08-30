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
    """Convertit les codes d'échappement System3 en texte français lisible."""
    if not texte:
        return ""
    t = str(texte)
    for code, char in TABLE_ACCENTS_IMPORT:
        t = t.replace(code, char)
    t = re.sub(r"\\F[0-9]", "", t)
    t = re.sub(r"\\S[0-9]{3}", "", t)
    return t.strip()


def formater_texte_system3(texte):
    """Nettoie et convertit le texte vers les codes d'échappement System3."""
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
    """Génère le bloc d'instructions machine pour une pièce."""
    code_client = (str(nom_client)[:10]).upper().ljust(10)[span_1](start_span)[span_1](end_span)

    if is_plat_couv:
        epaisseur_str = "99.0B[span_2](start_span)"[span_2](end_span)
        consigne = f"1{type_toile.upper()[:10]} - TITRAGE 1ERE COUV[span_3](start_span)"[span_3](end_span)
    else:
        epaisseur_str = f"{float(larg_dos):.1f}B".rjust(5)[span_4](start_span)[span_4](end_span)
        consigne = f"1{type_toile.upper()[:10]}[span_5](start_span)"[span_5](end_span)
        if has_pieces and nb_pieces > 0:
            c_p_court = (couleur_piece[:5]).upper()[span_6](start_span)[span_6](end_span)
            consigne += f" + {nb_pieces} P. {c_p_court}[span_7](start_span)"[span_7](end_span)

    offset_str = ".00".rjust(10)[span_8](start_span)[span_8](end_span)
    hauteur_str = f"{float(haut_maquette):.2f}".rjust(6)[span_9](start_span)[span_9](end_span)
    param_fixe = f" 1548 {consigne}".ljust(35)[span_10](start_span)[span_10](end_span)

    ligne_spec = f"       1{str(num_sequence).rjust(4)}{code_client}{epaisseur_str}{offset_str}{hauteur_str}{param_fixe}\n[span_11](start_span)"[span_11](end_span)

    code_ruban = "O1" if marquage_nom == "OR" else ("B1" if marquage_nom in ["BLANC", "ARGENT"] else "N1")[span_12](start_span)[span_12](end_span)

    # A. Mode Longitudinal (UCC)
    if (sens_long or float(larg_dos) <= 20.0) and not is_plat_couv:[span_13](start_span)[span_13](end_span)
        h_attaque = int(haut_maquette) - 20[span_14](start_span)[span_14](end_span)
        bloc = ligne_spec[span_15](start_span)[span_15](end_span)
        lignes_texte_long = [][span_16](start_span)[span_16](end_span)
        if df_lignes is not None and not df_lignes.empty:[span_17](start_span)[span_17](end_span)
            for _, row in df_lignes.iterrows():[span_18](start_span)[span_18](end_span)
                txt_brut = str(row["Titrage"]).strip()[span_19](start_span)[span_19](end_span)
                for sous_txt in [l.strip() for l in txt_brut.split("\n") if l.strip()]:[span_20](start_span)[span_20](end_span)
                    lignes_texte_long.append(formater_texte_system3(sous_txt))[span_21](start_span)[span_21](end_span)

        if lignes_texte_long:[span_22](start_span)[span_22](end_span)
            for idx, txt in enumerate(lignes_texte_long, start=1):[span_23](start_span)[span_23](end_span)
                if idx == 1:[span_24](start_span)[span_24](end_span)
                    bloc += f"UCC{str(h_attaque).rjust(3)} 40{code_ruban}  1{txt}\n[span_25](start_span)"[span_25](end_span)
                else:
                    bloc += f"             {idx}{txt}\n[span_26](start_span)"[span_26](end_span)
        else:
            bloc += f"UCC{str(h_attaque).rjust(3)} 40{code_ruban}  1.\n[span_27](start_span)"[span_27](end_span)

        bloc += "//\n" + ("." * 350) + "\n[span_28](start_span)"[span_28](end_span)
        return bloc[span_29](start_span)[span_29](end_span)

    # B. Mode Horizontal Centré (HCC)
    elements_a_dorer = [][span_30](start_span)[span_30](end_span)
    if df_lignes is not None and not df_lignes.empty:[span_31](start_span)[span_31](end_span)
        for _, row in df_lignes.iterrows():[span_32](start_span)[span_32](end_span)
            pos_y = int(row["Hauteur du titre (mm)"])[span_33](start_span)[span_33](end_span)
            txt_brut = str(row["Titrage"]).strip()[span_34](start_span)[span_34](end_span)
            sous_lignes = [l.strip() for l in txt_brut.split("\n") if l.strip()][span_35](start_span)[span_35](end_span)
            for s_idx, sous_txt in enumerate(sous_lignes):[span_36](start_span)[span_36](end_span)
                pos_calculee = pos_y - (s_idx * 15)[span_37](start_span)[span_37](end_span)
                elements_a_dorer.append((pos_calculee, formater_texte_system3(sous_txt)))[span_38](start_span)[span_38](end_span)

    if griffe_texte and not is_plat_couv:[span_39](start_span)[span_39](end_span)
        mots_griffe = [l.strip() for l in griffe_texte.split("\n") if l.strip()][span_40](start_span)[span_40](end_span)
        for g_idx, g_ligne in enumerate(mots_griffe):[span_41](start_span)[span_41](end_span)
            pos_g = int(griffe_pos_mm) + ((len(mots_griffe) - 1 - g_idx) * 8)[span_42](start_span)[span_42](end_span)
            elements_a_dorer.append((pos_g, formater_texte_system3(g_ligne)))[span_43](start_span)[span_43](end_span)

    elements_a_dorer.sort(key=lambda x: x[0], reverse=True)[span_44](start_span)[span_44](end_span)

    lignes_texte = [][span_45](start_span)[span_45](end_span)
    for pos_y, texte in elements_a_dorer:[span_46](start_span)[span_46](end_span)
        lignes_texte.append(f"           {str(pos_y).rjust(4)}{texte}")[span_47](start_span)[span_47](end_span)

    bloc = ligne_spec[span_48](start_span)[span_48](end_span)
    mode_axe = f"HCC      {code_ruban}[span_49](start_span)"[span_49](end_span)
    if lignes_texte:[span_50](start_span)[span_50](end_span)
        premiere_ligne = lignes_texte[0].replace("           ", mode_axe, 1)[span_51](start_span)[span_51](end_span)
        bloc += premiere_ligne + "\n[span_52](start_span)"[span_52](end_span)
        for l in lignes_texte[1:]:[span_53](start_span)[span_53](end_span)
            bloc += l + "\n[span_54](start_span)"[span_54](end_span)
    else:
        bloc += mode_axe + "250\n[span_55](start_span)"[span_55](end_span)

    bloc += "//\n[span_56](start_span)"[span_56](end_span)
    bloc += "." * 350 + "\n[span_57](start_span)"[span_57](end_span)
    return bloc[span_58](start_span)[span_58](end_span)


def assembler_fichier_system3(numero_job, liste_blocs):
    """Génère l'en-tête global et concatène les blocs du lot."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")[span_59](start_span)[span_59](end_span)
    job_formate = str(numero_job)[:8].ljust(8)[span_60](start_span)[span_60](end_span)
    en_tete = f"110 {job_formate}{timestamp}".ljust(114) + "\n[span_61](start_span)"[span_61](end_span)
    return en_tete + "".join(liste_blocs)[span_62](start_span)[span_62](end_span)


# ==============================================================================
# 2. ACCÈS BASE SUPABASE
# ==============================================================================

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])[span_63](start_span)[span_63](end_span)


def lister_tous_les_clients():
    supabase = obtenir_client_supabase()[span_64](start_span)[span_64](end_span)
    try:
        reponse = supabase.table("clients").select("nom").order("nom").execute()[span_65](start_span)[span_65](end_span)
        return [row["nom"] for row in reponse.data][span_66](start_span)[span_66](end_span)
    except Exception:
        return [][span_67](start_span)[span_67](end_span)


def lister_les_trains_du_client(client):
    supabase = obtenir_client_supabase()[span_68](start_span)[span_68](end_span)
    reponse = (
        supabase.table("fiches_livres")
        .select("numero_train")
        .eq("nom_client", client)
        .execute()
    )[span_69](start_span)[span_69](end_span)
    return sorted(list(set([row["numero_train"] for row in reponse.data])), reverse=True)[span_70](start_span)[span_70](end_span)


def lister_les_livres_du_train(client, train):
    supabase = obtenir_client_supabase()[span_71](start_span)[span_71](end_span)
    reponse = (
        supabase.table("fiches_livres")
        .select("numero_livre")
        .eq("nom_client", client)
        .eq("numero_train", train)
        .order("numero_livre")
        .execute()
    )[span_72](start_span)[span_72](end_span)
    return [row["numero_livre"] for row in reponse.data][span_73](start_span)[span_73](end_span)


def recuperer_griffe_client(nom_client):
    supabase = obtenir_client_supabase()[span_74](start_span)[span_74](end_span)
    try:
        reponse = (
            supabase.table("clients")
            .select("griffe, griffe_position_mm")
            .eq("nom", nom_client)
            .execute()
        )[span_75](start_span)[span_75](end_span)
        if reponse.data:[span_76](start_span)[span_76](end_span)
            r = reponse.data[0][span_77](start_span)[span_77](end_span)
            txt = (r.get("griffe") or "").strip()[span_78](start_span)[span_78](end_span)
            pos_mm = r.get("griffe_position_mm")[span_79](start_span)[span_79](end_span)
            return txt, (pos_mm if pos_mm is not None else 15)[span_80](start_span)[span_80](end_span)
    except Exception:
        pass
    return "", 15[span_81](start_span)[span_81](end_span)


def charger_types_toile_supabase():
    supabase = obtenir_client_supabase()[span_82](start_span)[span_82](end_span)
    try:
        reponse = supabase.table("referentiel_toiles").select("type_toile").execute()[span_83](start_span)[span_83](end_span)
        types = sorted(list(set([row["type_toile"] for row in reponse.data])))[span_84](start_span)[span_84](end_span)
        return types if types else ["Buckram", "Fantasia", "Métisse"][span_85](start_span)[span_85](end_span)
    except Exception:
        return ["Buckram", "Fantasia", "Métisse"][span_86](start_span)[span_86](end_span)


def charger_couleurs_par_toile_supabase(type_toile):
    supabase = obtenir_client_supabase()[span_87](start_span)[span_87](end_span)
    try:
        reponse = (
            supabase.table("referentiel_toiles")
            .select("couleur")
            .eq("type_toile", type_toile)
            .order("couleur")
            .execute()
        )[span_88](start_span)[span_88](end_span)
        couleurs = [row["couleur"] for row in reponse.data][span_89](start_span)[span_89](end_span)
        return couleurs if couleurs else ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"][span_90](start_span)[span_90](end_span)
    except Exception:
        return ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"][span_91](start_span)[span_91](end_span)


def recuperer_specs_livre(client, train, num_livre):
    supabase = obtenir_client_supabase()[span_92](start_span)[span_92](end_span)
    num_livre_int = int(num_livre)[span_93](start_span)[span_93](end_span)

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
        )[span_94](start_span)[span_94](end_span)

        if reponse.data:[span_95](start_span)[span_95](end_span)
            r = reponse.data[0][span_96](start_span)[span_96](end_span)
            hauteur_livre = r.get("hauteur") or 220[span_97](start_span)[span_97](end_span)
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
            )[span_98](start_span)[span_98](end_span)
    except Exception:
        pass

    return 220, 160, 20, "Buckram", "Noir", "OR", False, "Rouge", "OR", 1, "Classique", "Simple", 225[span_99](start_span)[span_99](end_span)


def recuperer_titrage_enregistre(client, train, num_livre):
    supabase = obtenir_client_supabase()[span_100](start_span)[span_100](end_span)
    try:
        num_livre_int = int(num_livre)[span_101](start_span)[span_101](end_span)
        reponse = (
            supabase.table("titrage_system3")
            .select("lignes_json, pieces_json")
            .eq("nom_client", str(client).strip())
            .eq("numero_train", str(train).strip())
            .eq("numero_livre", num_livre_int)
            .execute()
        )[span_102](start_span)[span_102](end_span)
        if reponse.data:[span_103](start_span)[span_103](end_span)
            rec = reponse.data[0][span_104](start_span)[span_104](end_span)
            df_lignes = pd.DataFrame(json.loads(rec["lignes_json"])) if rec.get("lignes_json") else None[span_105](start_span)[span_105](end_span)
            df_pieces = pd.DataFrame(json.loads(rec["pieces_json"])) if rec.get("pieces_json") else None[span_106](start_span)[span_106](end_span)

            if df_lignes is not None and not df_lignes.empty and "Titrage" in df_lignes.columns:
                df_lignes["Titrage"] = df_lignes["Titrage"].apply(decoder_texte_system3)

            return df_lignes, df_pieces[span_107](start_span)[span_107](end_span)
    except Exception:
        pass
    return None, None[span_108](start_span)[span_108](end_span)


def sauvegarder_titrage_sur_base(client, train, num_livre, date_saisie, df_lignes, df_pieces, specs_modifiees):
    supabase = obtenir_client_supabase()[span_109](start_span)[span_109](end_span)
    num_livre_int = int(num_livre)[span_110](start_span)[span_110](end_span)

    df_lignes_clean = df_lignes.copy() if df_lignes is not None else pd.DataFrame()
    if not df_lignes_clean.empty and "Titrage" in df_lignes_clean.columns:
        df_lignes_clean["Titrage"] = df_lignes_clean["Titrage"].apply(decoder_texte_system3)

    json_lignes = json.dumps(df_lignes_clean.to_dict(orient="records"), ensure_ascii=False)
    json_pieces = json.dumps(df_pieces.to_dict(orient="records"), ensure_ascii=False) if df_pieces is not None else "[][span_111](start_span)"[span_111](end_span)

    donnees_titrage = {
        "nom_client": str(client).strip(),
        "numero_train": str(train).strip(),
        "numero_livre": num_livre_int,
        "date_saisie": str(date_saisie),
        "lignes_json": json_lignes,
        "pieces_json": json_pieces,
    }[span_112](start_span)[span_112](end_span)

    try:
        supabase.table("titrage_system3").upsert(
            donnees_titrage,
            on_conflict="nom_client,numero_train,numero_livre",
        ).execute()[span_113](start_span)[span_113](end_span)

        (
            supabase.table("fiches_livres")
            .update(specs_modifiees)
            .eq("nom_client", str(client).strip())
            .eq("numero_train", str(train).strip())
            .eq("numero_livre", num_livre_int)
            .execute()
        )[span_114](start_span)[span_114](end_span)
        return True[span_115](start_span)[span_115](end_span)
    except Exception as e:
        st.error("Erreur technique lors de l'enregistrement : " + str(e))[span_116](start_span)[span_116](end_span)
        return False[span_117](start_span)[span_117](end_span)


HEX_COULEURS_TOILE = {
    "Noir": "#1a1a1a", "Rouge": "#8b0000", "Bleu": "#0f2b5c",
    "Vert": "#1e4620", "Jaune": "#d4af37", "Orange": "#d96b27",
    "Violet": "#4a235a", "Marron": "#5c4033"
}[span_118](start_span)[span_118](end_span)

HEX_COULEURS_MARQUAGE = {
    "OR": "#ffd700", "ARGENT": "#e0e0e0", "BLANC": "#ffffff",
    "NOIR": "#000000", "AUTRE": "#c0c0c0"
}[span_119](start_span)[span_119](end_span)


# ==============================================================================
# 3. MOTEUR GRAPHIQUE (GABARIT DE VISUALISATION AVEC GESTION POLICES UTF-8)
# ==============================================================================

def charger_police_compatible(taille_pt, bold=True):
    """Charge une police TrueType supportant l'UTF-8 et les accents français."""
    polices_a_tester = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "arial.ttf",
        "Arial.ttf"
    ]
    for nom_fnt in polices_a_tester:
        try:
            return ImageFont.truetype(nom_fnt, taille_pt)
        except Exception:
            continue
    return ImageFont.load_default()


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
    facteur_px = 2.5[span_120](start_span)[span_120](end_span)
    h_dos_px = max(min(int(haut_maquette * facteur_px), 600), 350)[span_121](start_span)[span_121](end_span)
    w_dos_px = max(min(int(larg_dos * facteur_px), 250), 60)[span_122](start_span)[span_122](end_span)

    w_regle_px = 80[span_123](start_span)[span_123](end_span)
    w_totale = w_regle_px + w_dos_px + 30[span_124](start_span)[span_124](end_span)
    h_totale = h_dos_px + 40[span_125](start_span)[span_125](end_span)

    img = Image.new("RGBA", (w_totale, h_totale), (248, 249, 250, 255))[span_126](start_span)[span_126](end_span)
    draw = ImageDraw.Draw(img)[span_127](start_span)[span_127](end_span)

    is_double = (police_style == "Double")
    taille_titre_pt = 18 if is_double else 12

    # Polices TrueType chargées avec support complet des accents
    font = charger_police_compatible(taille_titre_pt, bold=True)
    font_small = charger_police_compatible(10, bold=False)
    font_griffe = charger_police_compatible(11, bold=True)

    px_par_mm = h_dos_px / haut_maquette[span_128](start_span)[span_128](end_span)

    def tracer_texte(pt, txt, fill_color, fnt, anc="mm", alg="center"):
        txt = decoder_texte_system3(txt)
        draw.text(pt, txt, fill=fill_color, font=fnt, anchor=anc, align=alg)[span_129](start_span)[span_129](end_span)
        if is_double:
            x, y = pt
            draw.text((x + 0.8, y), txt, fill=fill_color, font=fnt, anchor=anc, align=alg)

    def mesurer_taille_vertical(texte, fnt):
        texte = decoder_texte_system3(texte)
        if not texte:[span_130](start_span)[span_130](end_span)
            return 0, 0[span_131](start_span)[span_131](end_span)
        bbox = draw.textbbox((0, 0), texte, font=fnt)[span_132](start_span)[span_132](end_span)
        largeur_txt = int(round(bbox[2] - bbox[0]))[span_133](start_span)[span_133](end_span)
        hauteur_txt = int(round(bbox[3] - bbox[1]))[span_134](start_span)[span_134](end_span)
        return hauteur_txt, largeur_txt

    def tracer_texte_vertical(x_centre_colonne, y_centre, texte, fill_color, fnt):
        texte = decoder_texte_system3(texte)
        if not texte:[span_135](start_span)[span_135](end_span)
            return[span_136](start_span)[span_136](end_span)
        bbox = draw.textbbox((0, 0), texte, font=fnt)[span_137](start_span)[span_137](end_span)
        largeur_txt = int(round(bbox[2] - bbox[0]))[span_138](start_span)[span_138](end_span)
        hauteur_txt = int(round(bbox[3] - bbox[1]))[span_139](start_span)[span_139](end_span)
        if largeur_txt <= 0 or hauteur_txt <= 0:[span_140](start_span)[span_140](end_span)
            return[span_141](start_span)[span_141](end_span)

        marge = 6[span_142](start_span)[span_142](end_span)
        calque = Image.new("RGBA", (largeur_txt + marge * 2, hauteur_txt + marge * 2), (0, 0, 0, 0))[span_143](start_span)[span_143](end_span)
        calque_draw = ImageDraw.Draw(calque)[span_144](start_span)[span_144](end_span)
        calque_draw.text((marge - bbox[0], marge - bbox[1]), texte, fill=fill_color, font=fnt, anchor="la")[span_145](start_span)[span_145](end_span)
        if is_double:
            calque_draw.text((marge - bbox[0] + 0.8, marge - bbox[1]), texte, fill=fill_color, font=fnt, anchor="la")

        calque_pivote = calque.rotate(90, expand=True)[span_146](start_span)[span_146](end_span)
        pos_x = int(x_centre_colonne - calque_pivote.width / 2)[span_147](start_span)[span_147](end_span)
        pos_y = int(y_centre - calque_pivote.height / 2)[span_148](start_span)[span_148](end_span)
        img.paste(calque_pivote, (pos_x, pos_y), calque_pivote)[span_149](start_span)[span_149](end_span)

    # Règle millimétrique
    draw.line([(w_regle_px, 20), (w_regle_px, 20 + h_dos_px)], fill="#cccccc", width=2)[span_150](start_span)[span_150](end_span)
    paliers_mm = list(range(0, int(haut_maquette) + 1, 10))[span_151](start_span)[span_151](end_span)
    if paliers_mm[-1] != int(haut_maquette):[span_152](start_span)[span_152](end_span)
        paliers_mm.append(int(haut_maquette))[span_153](start_span)[span_153](end_span)

    for mm in paliers_mm:[span_154](start_span)[span_154](end_span)
        y_mm = 20 + h_dos_px - (mm * px_par_mm)[span_155](start_span)[span_155](end_span)
        draw.line([(w_regle_px - 6, y_mm), (w_regle_px, y_mm)], fill="#555555", width=1)[span_156](start_span)[span_156](end_span)
        draw.text((w_regle_px - 50, y_mm - 6), f"{mm} mm", fill="#555555", font=font_small)[span_157](start_span)[span_157](end_span)

    # Dos
    x_dos = w_regle_px + 15[span_158](start_span)[span_158](end_span)
    y_dos = 20[span_159](start_span)[span_159](end_span)
    draw.rectangle([(x_dos, y_dos), (x_dos + w_dos_px, y_dos + h_dos_px)], fill=c_toile_hex, outline="#111111", width=2)[span_160](start_span)[span_160](end_span)

    # Pièces de titre
    if has_pieces and df_pieces is not None and not df_pieces.empty:[span_161](start_span)[span_161](end_span)
        for _, row_p in df_pieces.iterrows():[span_162](start_span)[span_162](end_span)
            pos_p_mm = row_p["Position (mm depuis le bas)"][span_163](start_span)[span_163](end_span)
            haut_p_mm = row_p["Hauteur pièce (mm)"][span_164](start_span)[span_164](end_span)
            c_p_nom = row_p["Couleur pièce"][span_165](start_span)[span_165](end_span)
            m_p_nom = row_p["Couleur marquage"][span_166](start_span)[span_166](end_span)
            txt_p = decoder_texte_system3(str(row_p.get("Titre sur pièce", "")).strip())

            if pd.notna(pos_p_mm) and pd.notna(haut_p_mm):[span_167](start_span)[span_167](end_span)
                bg_p_hex = HEX_COULEURS_TOILE.get(c_p_nom, "#8b0000")[span_168](start_span)[span_168](end_span)
                txt_p_hex = HEX_COULEURS_MARQUAGE.get(m_p_nom, "#ffd700")[span_169](start_span)[span_169](end_span)
                h_p_px = haut_p_mm * px_par_mm[span_170](start_span)[span_170](end_span)
                y_p_px = y_dos + h_dos_px - (pos_p_mm * px_par_mm) - h_p_px[span_171](start_span)[span_171](end_span)

                draw.rectangle([(x_dos, y_p_px), (x_dos + w_dos_px, y_p_px + h_p_px)], fill=bg_p_hex, outline="#ffffff", width=1)[span_172](start_span)[span_172](end_span)

                if txt_p and txt_p != "None":[span_173](start_span)[span_173](end_span)
                    lignes_p = [l.strip().upper() for l in txt_p.split("\n") if l.strip()][span_174](start_span)[span_174](end_span)
                    if is_long:[span_175](start_span)[span_175](end_span)
                        ecart_col_px = 24 if is_double else 16
                        nb_cols = len(lignes_p)[span_176](start_span)[span_176](end_span)
                        x_base_center = x_dos + (w_dos_px / 2)[span_177](start_span)[span_177](end_span)
                        y_centre_zone = y_p_px + (h_p_px / 2)[span_178](start_span)[span_178](end_span)
                        hauteur_zone_dispo = h_p_px - 12[span_179](start_span)[span_179](end_span)
                        for idx_col, ligne in enumerate(lignes_p):[span_180](start_span)[span_180](end_span)
                            offset_col = (idx_col - (nb_cols - 1) / 2) * ecart_col_px[span_181](start_span)[span_181](end_span)
                            x_col = x_base_center + offset_col[span_182](start_span)[span_182](end_span)
                            _, hauteur_prevue = mesurer_taille_vertical(ligne, font)[span_183](start_span)[span_183](end_span)
                            c_finale = "#d9534f" if hauteur_prevue > hauteur_zone_dispo else txt_p_hex[span_184](start_span)[span_184](end_span)
                            tracer_texte_vertical(x_col, y_centre_zone, ligne, c_finale, font)[span_185](start_span)[span_185](end_span)
                    else:
                        txt_p_full = "\n".join(lignes_p)[span_186](start_span)[span_186](end_span)
                        bbox_p = draw.textbbox((0, 0), txt_p_full, font=font, align="center")[span_187](start_span)[span_187](end_span)
                        w_txt_p = bbox_p[2] - bbox_p[0][span_188](start_span)[span_188](end_span)
                        c_finale = "#d9534f" if w_txt_p > (w_dos_px - 4) else txt_p_hex[span_189](start_span)[span_189](end_span)
                        tracer_texte((x_dos + (w_dos_px / 2), y_p_px + (h_p_px / 2)), txt_p_full, c_finale, font, "mm", "center")[span_190](start_span)[span_190](end_span)

    # Lignes directes sur le dos
    if df_lignes is not None and not df_lignes.empty:[span_191](start_span)[span_191](end_span)
        for _, row_l in df_lignes.iterrows():[span_192](start_span)[span_192](end_span)
            mm_pos = row_l["Hauteur du titre (mm)"][span_193](start_span)[span_193](end_span)
            txt = decoder_texte_system3(str(row_l["Titrage"]).strip())

            if pd.notna(mm_pos) and txt and txt != "None":[span_194](start_span)[span_194](end_span)
                x_center = x_dos + (w_dos_px / 2)[span_195](start_span)[span_195](end_span)
                lignes_txt = [l.strip().upper() for l in txt.split("\n") if l.strip()][span_196](start_span)[span_196](end_span)

                if is_long:[span_197](start_span)[span_197](end_span)
                    y_repere_centre_px = y_dos + h_dos_px - (float(mm_pos) * px_par_mm)[span_198](start_span)[span_198](end_span)
                    ecart_col_px = 24 if is_double else 16
                    nb_cols = len(lignes_txt)[span_199](start_span)[span_199](end_span)
                    for idx_col, ligne in enumerate(lignes_txt):[span_200](start_span)[span_200](end_span)
                        offset_col = (idx_col - (nb_cols - 1) / 2) * ecart_col_px[span_201](start_span)[span_201](end_span)
                        x_col = x_center + offset_col[span_202](start_span)[span_202](end_span)
                        _, hauteur_prevue = mesurer_taille_vertical(ligne, font)[span_203](start_span)[span_203](end_span)
                        y_centre = y_repere_centre_px[span_204](start_span)[span_204](end_span)
                        is_debordement = ((y_centre + (hauteur_prevue / 2)) > (y_dos + h_dos_px - 2) or (y_centre - (hauteur_prevue / 2)) < y_dos)[span_205](start_span)[span_205](end_span)
                        couleur_ligne = "#d9534f" if is_debordement else c_marq_hex[span_206](start_span)[span_206](end_span)
                        tracer_texte_vertical(x_col, y_centre, ligne, couleur_ligne, font)[span_207](start_span)[span_207](end_span)
                else:
                    y_l_px = y_dos + h_dos_px - (float(mm_pos) * px_par_mm)[span_208](start_span)[span_208](end_span)
                    txt_full = "\n".join(lignes_txt)[span_209](start_span)[span_209](end_span)
                    bbox_txt = draw.textbbox((0, 0), txt_full, font=font, align="center")[span_210](start_span)[span_210](end_span)
                    w_txt = bbox_txt[2] - bbox_txt[0][span_211](start_span)[span_211](end_span)
                    couleur_ligne = "#d9534f" if w_txt > (w_dos_px - 4) else c_marq_hex[span_212](start_span)[span_212](end_span)
                    tracer_texte((x_center, y_l_px), txt_full, couleur_ligne, font, "mm", "center")[span_213](start_span)[span_213](end_span)

    # Griffe client
    if griffe_texte:[span_214](start_span)[span_214](end_span)
        griffe_claire = decoder_texte_system3(griffe_texte)
        x_center = x_dos + (w_dos_px / 2)[span_215](start_span)[span_215](end_span)
        chars_max = max(int((w_dos_px - 8) / 7), 1)[span_216](start_span)[span_216](end_span)
        mots = griffe_claire.replace("\n", " ").split()
        lignes_g, ligne_c = [], [][span_217](start_span)[span_217](end_span)
        for m in mots:[span_218](start_span)[span_218](end_span)
            if len(" ".join(ligne_c + [m])) <= chars_max:[span_219](start_span)[span_219](end_span)
                ligne_c.append(m)[span_220](start_span)[span_220](end_span)
            else:
                if ligne_c:[span_221](start_span)[span_221](end_span)
                    lignes_g.append(" ".join(ligne_c).upper())[span_222](start_span)[span_222](end_span)
                ligne_c = [m][span_223](start_span)[span_223](end_span)
        if ligne_c:[span_224](start_span)[span_224](end_span)
            lignes_g.append(" ".join(ligne_c).upper())[span_225](start_span)[span_225](end_span)

        interligne_px = 14[span_226](start_span)[span_226](end_span)
        y_derniere_px = y_dos + h_dos_px - (griffe_pos_mm * px_par_mm)[span_227](start_span)[span_227](end_span)
        for idx_l, txt_l in enumerate(lignes_g):[span_228](start_span)[span_228](end_span)
            y_px = y_derniere_px - ((len(lignes_g) - 1 - idx_l) * interligne_px)[span_229](start_span)[span_229](end_span)
            draw.text((x_center, y_px), txt_l, fill=c_marq_hex, font=font_griffe, anchor="mm", align="center")[span_230](start_span)[span_230](end_span)

    return img[span_231](start_span)[span_231](end_span)


# ==============================================================================
# 4. INTERFACE UTILISATEUR STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Titrage Système 3", layout="wide")[span_232](start_span)[span_232](end_span)
st.title("📟 Module de Composition Spécifique — Titrage Système 3")[span_233](start_span)[span_233](end_span)

liste_clients_existants = lister_tous_les_clients()[span_234](start_span)[span_234](end_span)

if not liste_clients_existants:[span_235](start_span)[span_235](end_span)
    st.warning("⚠️ Créez d'abord un client pour utiliser le module de titrage.")[span_236](start_span)[span_236](end_span)
else:
    t3_haut_maquette = 225[span_237](start_span)[span_237](end_span)
    t3_larg_dos_utile = 30[span_238](start_span)[span_238](end_span)
    t3_couleur_nom = "Noir[span_239](start_span)"[span_239](end_span)
    t3_marquage_nom = "OR[span_240](start_span)"[span_240](end_span)
    t3_sens_titrage = "Classique[span_241](start_span)"[span_241](end_span)
    t3_police_style = "Simple[span_242](start_span)"[span_242](end_span)
    has_pieces = False[span_243](start_span)[span_243](end_span)
    df_pieces_edite = None[span_244](start_span)[span_244](end_span)
    df_edite_lignes = None[span_245](start_span)[span_245](end_span)
    griffe_a_afficher = "[span_246](start_span)"[span_246](end_span)
    griffe_hauteur_mm = 15[span_247](start_span)[span_247](end_span)

    col_form_saisie, col_gabarit_visualisation = st.columns([1.2, 0.8])[span_248](start_span)[span_248](end_span)

    with col_form_saisie:[span_249](start_span)[span_249](end_span)
        st.subheader("Clé de sélection du Livre")[span_250](start_span)[span_250](end_span)
        c_meta1, c_meta2 = st.columns(2)[span_251](start_span)[span_251](end_span)
        with c_meta1:[span_252](start_span)[span_252](end_span)
            t3_client = st.selectbox("1. Client référent", options=liste_clients_existants)[span_253](start_span)[span_253](end_span)
            t3_trains = lister_les_trains_du_client(t3_client)[span_254](start_span)[span_254](end_span)
            t3_train_sel = st.selectbox("2. N° de train", options=["-- Choisir --"] + t3_trains)[span_255](start_span)[span_255](end_span)

        livre_charge_valide = False[span_256](start_span)[span_256](end_span)
        with c_meta2:[span_257](start_span)[span_257](end_span)
            t3_date = st.date_input("Date d'atelier", value=datetime.now())[span_258](start_span)[span_258](end_span)
            if t3_train_sel != "-- Choisir --":[span_259](start_span)[span_259](end_span)
                liste_livres = ["-- Choisir un livre --"] + lister_les_livres_du_train(t3_client, t3_train_sel)[span_260](start_span)[span_260](end_span)
                t3_livre_num = st.selectbox("3. N° du livre", options=liste_livres)[span_261](start_span)[span_261](end_span)

                if t3_livre_num and t3_livre_num != "-- Choisir un livre --":[span_262](start_span)[span_262](end_span)
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
                    ) = recuperer_specs_livre(t3_client, t3_train_sel, t3_livre_num)[span_263](start_span)[span_263](end_span)
                    livre_charge_valide = True[span_264](start_span)[span_264](end_span)
            else:
                t3_livre_num = None[span_265](start_span)[span_265](end_span)

    if not livre_charge_valide:[span_266](start_span)[span_266](end_span)
        st.write("---")[span_267](start_span)[span_267](end_span)
        st.info("💡 **En attente d'instructions :** Sélectionnez un **N° de train** et un **N° de livre** existants.")[span_268](start_span)[span_268](end_span)
    else:
        with col_form_saisie:[span_269](start_span)[span_269](end_span)
            st.write("---")[span_270](start_span)[span_270](end_span)
            st.subheader("📐 Caractéristiques du livre & Emplacement du titrage")[span_271](start_span)[span_271](end_span)

            is_plat_couv = st.checkbox("🏷️ Imprimer sur la 1ère de Couverture (Plat) au lieu du dos", value=False)[span_272](start_span)[span_272](end_span)

            c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)[span_273](start_span)[span_273](end_span)
            with c_dim1:[span_274](start_span)[span_274](end_span)
                st.metric("Hauteur du livre (mm)", int(init_haut))[span_275](start_span)[span_275](end_span)
            with c_dim2:[span_276](start_span)[span_276](end_span)
                t3_haut_maquette = st.number_input(
                    "Hauteur maquette (mm)",
                    min_value=10, max_value=1000,
                    value=int(init_haut_maquette),
                    step=1,
                )[span_277](start_span)[span_277](end_span)
            with c_dim3:[span_278](start_span)[span_278](end_span)
                larg_dos_defaut = 99 if is_plat_couv else int(init_ep + 10)[span_279](start_span)[span_279](end_span)
                t3_larg_dos_utile = st.number_input("Largeur utile (mm)", min_value=5, max_value=500, value=larg_dos_defaut, step=1)[span_280](start_span)[span_280](end_span)
            with c_dim4:[span_281](start_span)[span_281](end_span)
                idx_m = ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"].index(init_marquage) if init_marquage in ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"] else 0[span_282](start_span)[span_282](end_span)
                t3_marquage_nom = st.selectbox("Marquage général", ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"], index=idx_m)[span_283](start_span)[span_283](end_span)

            c_toi1, c_toi2, c_toi3, c_toi4 = st.columns(4)[span_284](start_span)[span_284](end_span)
            types_toiles_dispos = charger_types_toile_supabase()[span_285](start_span)[span_285](end_span)
            with c_toi1:[span_286](start_span)[span_286](end_span)
                idx_t = types_toiles_dispos.index(init_type_toile) if init_type_toile in types_toiles_dispos else 0[span_287](start_span)[span_287](end_span)
                t3_type_toile = st.selectbox("Type de toile", types_toiles_dispos, index=idx_t)[span_288](start_span)[span_288](end_span)

            couleurs_toile_dispos = charger_couleurs_par_toile_supabase(t3_type_toile)[span_289](start_span)[span_289](end_span)
            with c_toi2:[span_290](start_span)[span_290](end_span)
                idx_c = couleurs_toile_dispos.index(init_couleur_toile) if init_couleur_toile in couleurs_toile_dispos else 0[span_291](start_span)[span_291](end_span)
                t3_couleur_nom = st.selectbox("Couleur de la toile", couleurs_toile_dispos, index=idx_c)[span_292](start_span)[span_292](end_span)

            with c_toi3:[span_293](start_span)[span_293](end_span)
                idx_s = 1 if init_sens_titrage == "Long" else 0[span_294](start_span)[span_294](end_span)
                t3_sens_titrage = st.selectbox("Sens du titrage", ["Classique", "Long"], index=idx_s)[span_295](start_span)[span_295](end_span)

            with c_toi4:[span_296](start_span)[span_296](end_span)
                idx_pstyle = 1 if init_police_style == "Double" else 0[span_297](start_span)[span_297](end_span)
                t3_police_style = st.selectbox("Empreinte police", ["Simple", "Double"], index=idx_pstyle)[span_298](start_span)[span_298](end_span)

            griffe_registree, griffe_pos_defaut = recuperer_griffe_client(t3_client)[span_299](start_span)[span_299](end_span)
            griffe_hauteur_mm = griffe_pos_defaut[span_300](start_span)[span_300](end_span)

            if griffe_registree and not is_plat_couv:[span_301](start_span)[span_301](end_span)
                st.write("---")[span_302](start_span)[span_302](end_span)
                st.subheader("🏷️ Griffe Client")[span_303](start_span)[span_303](end_span)
                c_grf1, c_grf2 = st.columns([2, 1])[span_304](start_span)[span_304](end_span)
                with c_grf1:[span_305](start_span)[span_305](end_span)
                    inclure_griffe = st.checkbox(f"Imprimer la griffe ({decoder_texte_system3(griffe_registree).replace(chr(10), ' / ')})", value=True)[span_306](start_span)[span_306](end_span)
                with c_grf2:[span_307](start_span)[span_307](end_span)
                    if inclure_griffe:[span_308](start_span)[span_308](end_span)
                        griffe_hauteur_mm = st.number_input("Position bas (mm)", min_value=0, max_value=200, value=int(griffe_pos_defaut), step=1)[span_309](start_span)[span_309](end_span)
                        griffe_a_afficher = griffe_registree[span_310](start_span)[span_310](end_span)

            st.write("---")[span_311](start_span)[span_311](end_span)
            st.subheader("🧩 Pièces de titre")[span_312](start_span)[span_312](end_span)
            has_pieces = st.checkbox("Activer la/les pièce(s) de titre", value=init_has_piece)[span_313](start_span)[span_313](end_span)
            df_lignes_existant, df_pieces_existant = recuperer_titrage_enregistre(t3_client, t3_train_sel, t3_livre_num)[span_314](start_span)[span_314](end_span)

            if has_pieces and not is_plat_couv:[span_315](start_span)[span_315](end_span)
                df_pieces_initial = df_pieces_existant if (df_pieces_existant is not None and not df_pieces_existant.empty) else pd.DataFrame([{
                    "Position (mm depuis le bas)": int(t3_haut_maquette * 0.75),
                    "Hauteur pièce (mm)": 35,
                    "Couleur pièce": init_piece_couleur,
                    "Couleur marquage": init_piece_marquage,
                    "Titre sur pièce": "TITRE LIGNE 1\nSOUS-TITRE LIGNE 2",
                }])[span_316](start_span)[span_316](end_span)

                list_c = ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"][span_317](start_span)[span_317](end_span)
                list_m = ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"][span_318](start_span)[span_318](end_span)

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
                )[span_319](start_span)[span_319](end_span)

            st.write("---")[span_320](start_span)[span_320](end_span)
            st.subheader("✍️ Lignes de titrage (Position en mm)")[span_321](start_span)[span_321](end_span)

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

            st.write("---")[span_322](start_span)[span_322](end_span)
            if st.button("💾 Sauvegarder les modifications et le titrage", type="primary", use_container_width=True):[span_323](start_span)[span_323](end_span)
                c_p = df_pieces_edite.iloc[0]["Couleur pièce"] if (df_pieces_edite is not None and not df_pieces_edite.empty) else init_piece_couleur[span_324](start_span)[span_324](end_span)
                m_p = df_pieces_edite.iloc[0]["Couleur marquage"] if (df_pieces_edite is not None and not df_pieces_edite.empty) else init_piece_marquage[span_325](start_span)[span_325](end_span)

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
                }[span_326](start_span)[span_326](end_span)

                if sauvegarder_titrage_sur_base(
                    t3_client,
                    t3_train_sel,
                    t3_livre_num,
                    t3_date,
                    df_edite_lignes,
                    df_pieces_edite if has_pieces else None,
                    specs_mises_a_jour,
                ):[span_327](start_span)[span_327](end_span)
                    st.success(f"✅ Enregistré (Livre N°{t3_livre_num} — Train {t3_train_sel})")[span_328](start_span)[span_328](end_span)

            # --- ZONE D'EXPORT SYSTEM 3 (.S3T) ---
            st.write("---")[span_329](start_span)[span_329](end_span)
            st.subheader("🖨️ Génération du fichier machine (.S3T)")[span_330](start_span)[span_330](end_span)

            c_exp1, c_exp2 = st.columns(2)[span_331](start_span)[span_331](end_span)
            with c_exp1:[span_332](start_span)[span_332](end_span)
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
                )[span_333](start_span)[span_333](end_span)
                fichier_livre_unique = assembler_fichier_system3(
                    numero_job=f"{t3_train_sel}_{t3_livre_num}",
                    liste_blocs=[bloc_livre_actuel],
                )[span_334](start_span)[span_334](end_span)
                st.download_button(
                    label=f"📄 Télécharger le livre N°{t3_livre_num} (.S3T)",
                    data=fichier_livre_unique.encode("latin-1", errors="replace"),
                    file_name=f"LIVRE_{t3_train_sel}_{t3_livre_num}.S3T",
                    mime="text/plain",
                    use_container_width=True,
                )[span_335](start_span)[span_335](end_span)

            with c_exp2:[span_336](start_span)[span_336](end_span)
                if st.button(f"📦 Préparer le Train {t3_train_sel} entier", use_container_width=True):[span_337](start_span)[span_337](end_span)
                    livres_du_train = lister_les_livres_du_train(t3_client, t3_train_sel)[span_338](start_span)[span_338](end_span)
                    blocs_train = [][span_339](start_span)[span_339](end_span)
                    for seq, n_livre in enumerate(livres_du_train, start=1):[span_340](start_span)[span_340](end_span)
                        specs_l = recuperer_specs_livre(t3_client, t3_train_sel, n_livre)[span_341](start_span)[span_341](end_span)
                        h_maq, ep, t_toile, sens_t, marq_l = specs_l[12], specs_l[2], specs_l[3], specs_l[10], specs_l[5][span_342](start_span)[span_342](end_span)
                        c_toile, h_piece, n_piece, c_piece_toile = specs_l[4], specs_l[6], specs_l[9], specs_l[7][span_343](start_span)[span_343](end_span)
                        df_lig, _ = recuperer_titrage_enregistre(t3_client, t3_train_sel, n_livre)[span_344](start_span)[span_344](end_span)

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
                        )[span_345](start_span)[span_345](end_span)
                        blocs_train.append(b)[span_346](start_span)[span_346](end_span)

                    fichier_train_complet = assembler_fichier_system3(
                        numero_job=t3_train_sel,
                        liste_blocs=blocs_train,
                    )[span_347](start_span)[span_347](end_span)
                    st.download_button(
                        label=f"⬇️ Télécharger le train complet ({len(livres_du_train)} livres)",
                        data=fichier_train_complet.encode("latin-1", errors="replace"),
                        file_name=f"TRAIN_{t3_train_sel}.S3T",
                        mime="text/plain",
                        use_container_width=True,
                    )[span_348](start_span)[span_348](end_span)

        with col_gabarit_visualisation:[span_349](start_span)[span_349](end_span)
            st.subheader("📐 Gabarit dynamique du dos à dorer")[span_350](start_span)[span_350](end_span)
            hex_toile = HEX_COULEURS_TOILE.get(t3_couleur_nom, "#1a1a1a")[span_351](start_span)[span_351](end_span)
            hex_marq = HEX_COULEURS_MARQUAGE.get(t3_marquage_nom, "#ffd700")[span_352](start_span)[span_352](end_span)

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
            )[span_353](start_span)[span_353](end_span)

            buf = io.BytesIO()[span_354](start_span)[span_354](end_span)
            img_gabarit.save(buf, format="PNG")[span_355](start_span)[span_355](end_span)
            st.image(buf.getvalue(), use_container_width=False)[span_356](start_span)[span_356](end_span)
