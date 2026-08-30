import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import re
import json

def obtenir_client_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])[span_2](start_span)[span_2](end_span)

def determiner_categorie_format(l, h):
    if l <= 115 and h <= 185: return "115 x 185 (In 12)[span_3](start_span)"[span_3](end_span)
    elif l <= 130 and h <= 200: return "130 x 200 (In 8° écu)[span_4](start_span)"[span_4](end_span)
    elif l <= 160 and h <= 245: return "160 x 245 (In 8° raisin)[span_5](start_span)"[span_5](end_span)
    elif l <= 175 and h <= 270: return "175 x 270 (In 8° jésus)[span_6](start_span)"[span_6](end_span)
    elif l <= 245 and h <= 320: return "245 x 320 (In 4° raisin)[span_7](start_span)"[span_7](end_span)
    elif l <= 270 and h <= 350: return "270 x 350 (In 4° jésus)[span_8](start_span)"[span_8](end_span)
    elif l <= 280 and h <= 440: return "280 x 440 (Folio carré)[span_9](start_span)"[span_9](end_span)
    elif l <= 320 and h <= 490: return "320 x 490 (Folio raisin)[span_10](start_span)"[span_10](end_span)
    elif l <= 350 and h <= 540: return "350 x 540 (Folio jésus)[span_11](start_span)"[span_11](end_span)
    elif l <= 440 and h <= 600: return "440 x 600 (Grand folio)[span_12](start_span)"[span_12](end_span)
    elif l <= 700: return "Plano A[span_13](start_span)"[span_13](end_span)
    else: return "Plano B[span_14](start_span)"[span_14](end_span)

def lister_tous_les_clients():
    supabase = obtenir_client_supabase()[span_15](start_span)[span_15](end_span)
    try:
        reponse = supabase.table("clients").select("nom").order("nom").execute()[span_16](start_span)[span_16](end_span)
        return [row["nom"] for row in reponse.data][span_17](start_span)[span_17](end_span)
    except Exception:
        return [][span_18](start_span)[span_18](end_span)

def lister_les_trains_du_client(client):
    supabase = obtenir_client_supabase()[span_19](start_span)[span_19](end_span)
    reponse = supabase.table("fiches_livres").select("numero_train").eq("nom_client", client.strip()).execute()[span_20](start_span)[span_20](end_span)
    return sorted(list(set([row["numero_train"] for row in reponse.data])), reverse=True)[span_21](start_span)[span_21](end_span)

def generer_automatiquement_numero_train(client):
    annee_courante = datetime.now().year[span_22](start_span)[span_22](end_span)
    prefixe = f"T{annee_courante}[span_23](start_span)"[span_23](end_span)
    supabase = obtenir_client_supabase()[span_24](start_span)[span_24](end_span)
    reponse = supabase.table("fiches_livres").select("numero_train").eq("nom_client", client.strip()).like("numero_train", f"{prefixe}%").execute()[span_25](start_span)[span_25](end_span)
    trains = list(set([row["numero_train"] for row in reponse.data]))[span_26](start_span)[span_26](end_span)
    if trains:
        trains.sort(reverse=True)[span_27](start_span)[span_27](end_span)
        str_num = trains[0][5:][span_28](start_span)[span_28](end_span)
        try:
            prochain_ordre = int(str_num) + 1[span_29](start_span)[span_29](end_span)
        except ValueError:
            prochain_ordre = 1[span_30](start_span)[span_30](end_span)
    else:
        prochain_ordre = 1[span_31](start_span)[span_31](end_span)
    return f"{prefixe}{prochain_ordre:03d}[span_32](start_span)"[span_32](end_span)

def determiner_prochain_numero_livre(client, train):
    supabase = obtenir_client_supabase()[span_33](start_span)[span_33](end_span)
    reponse = supabase.table("fiches_livres").select("numero_livre").eq("nom_client", client.strip()).eq("numero_train", train.strip()).execute()[span_34](start_span)[span_34](end_span)
    if not reponse.data:
        return 1[span_35](start_span)[span_35](end_span)
    nums = [int(row["numero_livre"]) for row in reponse.data if row["numero_livre"] is not None][span_36](start_span)[span_36](end_span)
    return (max(nums) + 1) if nums else 1[span_37](start_span)[span_37](end_span)

def recuperer_livre_specifique(client, train, num_livre):
    supabase = obtenir_client_supabase()[span_38](start_span)[span_38](end_span)
    reponse = supabase.table("fiches_livres").select("*").eq("nom_client", client.strip()).eq("numero_train", train.strip()).eq("numero_livre", num_livre).execute()[span_39](start_span)[span_39](end_span)
    return reponse.data[0] if reponse.data else None[span_40](start_span)[span_40](end_span)

def supprimer_livre_specifique(client, train, num_livre):
    supabase = obtenir_client_supabase()[span_41](start_span)[span_41](end_span)
    try:
        try:
            supabase.table("titrage_system3").delete().eq("nom_client", client.strip()).eq("numero_train", train.strip()).eq("numero_livre", num_livre).execute()[span_42](start_span)[span_42](end_span)
        except Exception:
            pass
        supabase.table("fiches_livres").delete().eq("nom_client", client.strip()).eq("numero_train", train.strip()).eq("numero_livre", num_livre).execute()[span_43](start_span)[span_43](end_span)
        return True[span_44](start_span)[span_44](end_span)
    except Exception as e:
        st.error(f"Erreur lors de la suppression : {e}")[span_45](start_span)[span_45](end_span)
        return False[span_46](start_span)[span_46](end_span)

def supprimer_train_complet(client, train):
    """Supprime l'intégralité des livres et des titrages associés à un train."""
    supabase = obtenir_client_supabase()
    try:
        try:
            supabase.table("titrage_system3").delete().eq("nom_client", client.strip()).eq("numero_train", train.strip()).execute()
        except Exception:
            pass
        supabase.table("fiches_livres").delete().eq("nom_client", client.strip()).eq("numero_train", train.strip()).execute()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression du train : {e}")
        return False

def recuperer_livres_du_train(client, train):
    supabase = obtenir_client_supabase()[span_47](start_span)[span_47](end_span)
    reponse = supabase.table("fiches_livres").select("numero_livre, nature_doc, text_doc, largeur, hauteur, type_reliure, couleur, cocher_piece_titre, couleur_pieces_toile").eq("nom_client", client.strip()).eq("numero_train", train.strip()).order("numero_livre").execute()[span_48](start_span)[span_48](end_span)
    
    donnees_formatees = [][span_49](start_span)[span_49](end_span)
    for r in reponse.data:[span_50](start_span)[span_50](end_span)
        pt_active = f"Oui ({r['couleur_pieces_toile']})" if r['cocher_piece_titre'] else "Non[span_51](start_span)"[span_51](end_span)
        donnees_formatees.append([[span_52](start_span)[span_52](end_span)
            r['numero_livre'], r['nature_doc'], r['text_doc'], r['largeur'], r['hauteur'], r['type_reliure'], r['couleur'], pt_active[span_53](start_span)[span_53](end_span)
        ])[span_54](start_span)[span_54](end_span)
    return donnees_formatees[span_55](start_span)[span_55](end_span)

def enregistrer_ou_mettre_a_jour_livre(donnees):
    supabase = obtenir_client_supabase()[span_56](start_span)[span_56](end_span)
    supabase.table("fiches_livres").upsert(donnees).execute()[span_57](start_span)[span_57](end_span)

def charger_types_toile_supabase():
    supabase = obtenir_client_supabase()[span_58](start_span)[span_58](end_span)
    try:
        reponse = supabase.table("referentiel_toiles").select("type_toile").execute()[span_59](start_span)[span_59](end_span)
        types = sorted(list(set([row["type_toile"] for row in reponse.data])))[span_60](start_span)[span_60](end_span)
        return types if types else ["Buckram", "Fantasia", "Métisse"][span_61](start_span)[span_61](end_span)
    except Exception:
        return ["Buckram", "Fantasia", "Métisse"][span_62](start_span)[span_62](end_span)

def charger_couleurs_par_toile_supabase(type_toile_selectionne):
    supabase = obtenir_client_supabase()[span_63](start_span)[span_63](end_span)
    try:
        reponse = supabase.table("referentiel_toiles") \
            .select("couleur") \
            .eq("type_toile", type_toile_selectionne) \
            .order("couleur") \
            .execute()[span_64](start_span)[span_64](end_span)
        couleurs = [row["couleur"] for row in reponse.data][span_65](start_span)[span_65](end_span)
        return couleurs if couleurs else liste_couleurs_generique[span_66](start_span)[span_66](end_span)
    except Exception:
        return liste_couleurs_generique[span_67](start_span)[span_67](end_span)


# --- PARSEUR ET DÉCODEUR SYSTEM 3 (.S3T) CORRIGÉ POSITIONNEL ---
def decoder_texte_system3(texte):
    """Convertit les codes d'échappement System3 en texte français lisible."""
    if not texte:[span_68](start_span)[span_68](end_span)
        return "[span_69](start_span)"[span_69](end_span)
    t = str(texte)[span_70](start_span)[span_70](end_span)
    remplacements_inverses = {
        "\\Af": "É", "\\Ae": "È", "\\Ag": "Ê", "\\Aj": "Ë",[span_71](start_span)[span_71](end_span)
        "\\Aa": "À", "\\Ac": "Â", "\\Ad": "Ä",[span_72](start_span)[span_72](end_span)
        "\\Am": "Ç",[span_73](start_span)[span_73](end_span)
        "\\Au": "Î", "\\Al": "Ï",[span_74](start_span)[span_74](end_span)
        "\\At": "Ô", "\\Az": "Ö",[span_75](start_span)[span_75](end_span)
        "\\Ax": "Ù", "\\Aw": "Û",[span_76](start_span)[span_76](end_span)
        "]": "°", "\\F1": "", "\\F5": "", "\\F6": "[span_77](start_span)"[span_77](end_span)
    }
    for code, char in remplacements_inverses.items():[span_78](start_span)[span_78](end_span)
        t = t.replace(code, char)[span_79](start_span)[span_79](end_span)
    t = re.sub(r"\\S\d{3}", "", t)[span_80](start_span)[span_80](end_span)
    return t.strip()[span_81](start_span)[span_81](end_span)

def parser_fichier_system3(contenu_texte):
    """Parse un fichier .S3T en respectant strictement les colonnes positionnelles."""
    lignes = [l.rstrip("\r\n") for l in contenu_texte.split("\n") if l.strip()][span_82](start_span)[span_82](end_span)
    if not lignes:[span_83](start_span)[span_83](end_span)
        return [][span_84](start_span)[span_84](end_span)

    blocs_bruts = [][span_85](start_span)[span_85](end_span)
    bloc_courant = [][span_86](start_span)[span_86](end_span)
    for l in lignes[1:]:[span_87](start_span)[span_87](end_span)
        if l.startswith("//"):[span_88](start_span)[span_88](end_span)
            if bloc_courant:[span_89](start_span)[span_89](end_span)
                blocs_bruts.append(bloc_courant)[span_90](start_span)[span_90](end_span)
                bloc_courant = [][span_91](start_span)[span_91](end_span)
        elif not l.startswith("..."):[span_92](start_span)[span_92](end_span)
            bloc_courant.append(l)[span_93](start_span)[span_93](end_span)

    livres_importes = [][span_94](start_span)[span_94](end_span)
    for bloc in blocs_bruts:[span_95](start_span)[span_95](end_span)
        if not bloc:[span_96](start_span)[span_96](end_span)
            continue[span_97](start_span)[span_97](end_span)
        
        # 1. Cartouche pièce (Ligne 1)
        ligne_entete = bloc[0].ljust(80)
        try:
            num_seq = int(ligne_entete[8:12].strip())[span_98](start_span)[span_98](end_span)
        except Exception:
            num_seq = len(livres_importes) + 1[span_99](start_span)[span_99](end_span)

        code_client = ligne_entete[12:22].strip()[span_100](start_span)[span_100](end_span)
        epaisseur_str = ligne_entete[22:27].replace("B", "").strip()[span_101](start_span)[span_101](end_span)
        hauteur_str = ligne_entete[37:43].strip()[span_102](start_span)[span_102](end_span)
        consigne_atelier = ligne_entete[48:].strip()[span_103](start_span)[span_103](end_span)

        try:
            epaisseur = float(epaisseur_str)[span_104](start_span)[span_104](end_span)
        except Exception:
            epaisseur = 20.0[span_105](start_span)[span_105](end_span)

        try:
            hauteur = float(hauteur_str)[span_106](start_span)[span_106](end_span)
        except Exception:
            hauteur = 220.0[span_107](start_span)[span_107](end_span)

        is_long = any(l.startswith("UCC") or l.startswith("ULL") for l in bloc) or (epaisseur <= 20.0)[span_108](start_span)[span_108](end_span)

        # Détection pièces de titre
        cocher_pt = "P." in consigne_atelier.upper() or "PIECE" in consigne_atelier.upper()[span_109](start_span)[span_109](end_span)
        couleur_pt = "Rouge[span_110](start_span)"[span_110](end_span)
        if "NOIR" in consigne_atelier.upper(): couleur_pt = "Noir[span_111](start_span)"[span_111](end_span)
        elif "ROUGE" in consigne_atelier.upper(): couleur_pt = "Rouge[span_112](start_span)"[span_112](end_span)
        elif "BLEU" in consigne_atelier.upper() or "BF" in consigne_atelier.upper() or "BX" in consigne_atelier.upper(): couleur_pt = "Bleu[span_113](start_span)"[span_113](end_span)
        elif "VERT" in consigne_atelier.upper() or "VF" in consigne_atelier.upper(): couleur_pt = "Vert[span_114](start_span)"[span_114](end_span)
        elif "MARRON" in consigne_atelier.upper() or "MF" in consigne_atelier.upper(): couleur_pt = "Marron[span_115](start_span)"[span_115](end_span)

        # 2. Extraction exacte du texte et de la hauteur Y par découpage positionnel strict
        lignes_titrage = [][span_116](start_span)[span_116](end_span)
        for l in bloc[1:]:[span_117](start_span)[span_117](end_span)
            # Cas A : Titrage en long UCC / ULL
            if l.startswith("UCC") or l.startswith("ULL"):[span_118](start_span)[span_118](end_span)
                texte_brut = re.sub(r"^(UCC|ULL)\d+\s+\d+[A-Z0-9]+\s+\d+", "", l).strip()[span_119](start_span)[span_119](end_span)
                if texte_brut and texte_brut != ".":[span_120](start_span)[span_120](end_span)
                    lignes_titrage.append({[span_121](start_span)[span_121](end_span)
                        "Hauteur du titre (mm)": int(hauteur * 0.70),[span_122](start_span)[span_122](end_span)
                        "Titrage": decoder_texte_system3(texte_brut)[span_123](start_span)[span_123](end_span)
                    })[span_124](start_span)[span_124](end_span)
            elif re.match(r"^\s*[1-9]\s+", l):[span_125](start_span)[span_125](end_span)
                texte_brut = re.sub(r"^\s*[1-9]\s+", "", l).strip()[span_126](start_span)[span_126](end_span)
                if texte_brut and texte_brut != ".":[span_127](start_span)[span_127](end_span)
                    lignes_titrage.append({[span_128](start_span)[span_128](end_span)
                        "Hauteur du titre (mm)": int(hauteur * 0.50),[span_129](start_span)[span_129](end_span)
                        "Titrage": decoder_texte_system3(texte_brut)[span_130](start_span)[span_130](end_span)
                    })[span_131](start_span)[span_131](end_span)

            # Cas B : Titrage standard HCC
            else:
                l_pad = l.ljust(80)
                # Zone de hauteur Y : colonnes 11 à 15
                zone_pos = l_pad[11:15].strip()
                # Zone de texte réel : à partir de la colonne 15
                texte_brut = l_pad[15:].strip()

                # Extraction des 1 à 3 derniers chiffres de la zone pour isoler la hauteur (ex: 6129 -> 129, 1119 -> 119)
                match_pos = re.search(r"(\d{1,3})$", zone_pos)
                if match_pos and texte_brut and texte_brut != ".":
                    val_y = int(match_pos.group(1))
                    lignes_titrage.append({
                        "Hauteur du titre (mm)": val_y,
                        "Titrage": decoder_texte_system3(texte_brut)
                    })

        df_l = pd.DataFrame(lignes_titrage) if lignes_titrage else pd.DataFrame([{"Hauteur du titre (mm)": int(hauteur * 0.20), "Titrage": "TITRE"}])[span_132](start_span)[span_132](end_span)

        livres_importes.append({[span_133](start_span)[span_133](end_span)
            "sequence": num_seq,[span_134](start_span)[span_134](end_span)
            "client_code": code_client,[span_135](start_span)[span_135](end_span)
            "largeur": max(int(hauteur * 0.65), 140),[span_136](start_span)[span_136](end_span)
            "hauteur": int(hauteur - 5) if hauteur > 30 else int(hauteur),[span_137](start_span)[span_137](end_span)
            "hauteur_maquette": int(hauteur),[span_138](start_span)[span_138](end_span)
            "epaisseur": int(epaisseur),[span_139](start_span)[span_139](end_span)
            "sens_titrage": "Long" if is_long else "Classique",[span_140](start_span)[span_140](end_span)
            "cocher_piece_titre": cocher_pt,[span_141](start_span)[span_141](end_span)
            "couleur_pieces_toile": couleur_pt,[span_142](start_span)[span_142](end_span)
            "nombre_pieces_titre": 2 if "2 P" in consigne_atelier.upper() else 1,[span_143](start_span)[span_143](end_span)
            "df_lignes": df_l[span_144](start_span)[span_144](end_span)
        })[span_145](start_span)[span_145](end_span)

    return livres_importes[span_146](start_span)[span_146](end_span)


# --- CONFIGURATION STREAMLIT ---
st.set_page_config(page_title="Saisie & Suivi des Livres", layout="wide")[span_147](start_span)[span_147](end_span)
st.title("📚 Saisie de Fiche — Devis + Traitements")[span_148](start_span)[span_148](end_span)

liste_clients_existants = lister_tous_les_clients()[span_149](start_span)[span_149](end_span)
liste_couleurs_generique = ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"][span_150](start_span)[span_150](end_span)

OPTIONS_SUPPLEMENTS = [[span_151](start_span)[span_151](end_span)
    "Plats conservés", "Onglets", "Doublage japon", "Charnières toile",[span_152](start_span)[span_152](end_span)
    "Conservation de gardes", "Couture sur nerfs", "Couvrure sur nerf",[span_153](start_span)[span_153](end_span)
    "Filets fleurons", "Plaçure", "Sup ouvrage déjà relié",[span_154](start_span)[span_154](end_span)
    "Plaçure intercalaires", "Doublage couverture", "Montage de couverture",[span_155](start_span)[span_155](end_span)
    "Fonds de cahiers", "Pose antivol", "Désacidification",[span_156](start_span)[span_156](end_span)
    "Désinfection", "Charnière cuir", "Enlever agrafes",[span_157](start_span)[span_157](end_span)
    "Couture manuelle sur rubans[span_158](start_span)"[span_158](end_span)
][span_159](start_span)[span_159](end_span)

PRIX_SUPPLEMENTS = {[span_160](start_span)[span_160](end_span)
    "Plats conservés": 15.00, "Onglets": 8.50, "Doublage japon": 22.00, "Charnières toile": 14.00,[span_161](start_span)[span_161](end_span)
    "Conservation de gardes": 12.00, "Couture sur nerfs": 35.00, "Couvrure sur nerf": 40.00,[span_162](start_span)[span_162](end_span)
    "Filets fleurons": 25.00, "Plaçure": 18.00, "Sup ouvrage déjà relié": 30.00,[span_163](start_span)[span_163](end_span)
    "Plaçure intercalaires": 15.00, "Doublage couverture": 20.00, "Montage de couverture": 17.50,[span_164](start_span)[span_164](end_span)
    "Fonds de cahiers": 12.50, "Pose antivol": 3.00, "Désacidification": 45.00,[span_165](start_span)[span_165](end_span)
    "Désinfection": 50.00, "Charnière cuir": 28.00, "Enlever agrafes": 9.00,[span_166](start_span)[span_166](end_span)
    "Couture manuelle sur rubans": 32.00[span_167](start_span)[span_167](end_span)
}[span_168](start_span)[span_168](end_span)

if not liste_clients_existants:[span_169](start_span)[span_169](end_span)
    st.warning("⚠️ Créez d'abord un client dans le module 'Fiches Clients'.")[span_170](start_span)[span_170](end_span)
else:
    col_saisie, col_visualisation = st.columns([1.2, 0.8])[span_171](start_span)[span_171](end_span)
    
    with col_saisie:[span_172](start_span)[span_172](end_span)
        st.subheader("Clé d'identification du Train")[span_173](start_span)[span_173](end_span)
        nom_client_valide = st.selectbox("1. Sélectionner le client", options=["-- Choisir un client --"] + liste_clients_existants)[span_174](start_span)[span_174](end_span)
        
        if nom_client_valide == "-- Choisir un client --":[span_175](start_span)[span_175](end_span)
            st.info("💡 Sélectionnez un client pour afficher ou créer un train de livres.")[span_176](start_span)[span_176](end_span)
            train_charge_valide = False[span_177](start_span)[span_177](end_span)
        else:
            liste_trains_existants = lister_les_trains_du_client(nom_client_valide)[span_178](start_span)[span_178](end_span)
            prochain_train_auto = generer_automatiquement_numero_train(nom_client_valide)[span_179](start_span)[span_179](end_span)

            # --- ZONE D'IMPORTATION DIRECTEMENT APRÈS LE CLIENT ---
            with st.expander("📥 Importer un fichier System3 (.S3T) pour ce client", expanded=False):[span_180](start_span)[span_180](end_span)
                st.caption(f"Charge un lot complet de livres et préremplit leurs titrages pour **{nom_client_valide}**.")[span_181](start_span)[span_181](end_span)
                fichier_uploade = st.file_uploader("Sélectionner un fichier .S3T", type=["s3t", "txt"], key=f"upload_s3t_{nom_client_valide}")[span_182](start_span)[span_182](end_span)
                
                if fichier_uploade is not None:[span_183](start_span)[span_183](end_span)
                    contenu_str = fichier_uploade.getvalue().decode("latin-1", errors="replace")[span_184](start_span)[span_184](end_span)
                    livres_importes = parser_fichier_system3(contenu_str)[span_185](start_span)[span_185](end_span)
                    
                    if livres_importes:[span_186](start_span)[span_186](end_span)
                        st.info(f"🔍 **{len(livres_importes)} livre(s)** détecté(s) dans le fichier.")[span_187](start_span)[span_187](end_span)
                        
                        train_cible_import = st.selectbox([span_188](start_span)[span_188](end_span)
                            "Affecter ces livres au Train :",[span_189](start_span)[span_189](end_span)
                            options=[f"[+] Nouveau Train : {prochain_train_auto}"] + liste_trains_existants,[span_190](start_span)[span_190](end_span)
                            key="sel_train_cible_import[span_191](start_span)"[span_191](end_span)
                        )[span_192](start_span)[span_192](end_span)
                        num_train_final = prochain_train_auto if train_cible_import.startswith("[+]") else train_cible_import[span_193](start_span)[span_193](end_span)
                        
                        if st.button(f"⚡ Valider l'importation vers {num_train_final}", type="primary", use_container_width=True):[span_194](start_span)[span_194](end_span)
                            supabase = obtenir_client_supabase()[span_195](start_span)[span_195](end_span)
                            for l_imp in livres_importes:[span_196](start_span)[span_196](end_span)
                                n_livre = l_imp["sequence"][span_197](start_span)[span_197](end_span)
                                
                                donnees_fiche_imp = {[span_198](start_span)[span_198](end_span)
                                    "nom_client": nom_client_valide.strip(),[span_199](start_span)[span_199](end_span)
                                    "numero_train": num_train_final.strip(),[span_200](start_span)[span_200](end_span)
                                    "numero_livre": n_livre,[span_201](start_span)[span_201](end_span)
                                    "nature_doc": "Périodique (Pério)",[span_202](start_span)[span_202](end_span)
                                    "text_doc": "Neuf",[span_203](start_span)[span_203](end_span)
                                    "option_autre": "N/A",[span_204](start_span)[span_204](end_span)
                                    "repro_scanne": False,[span_205](start_span)[span_205](end_span)
                                    "repro_report": False,[span_206](start_span)[span_206](end_span)
                                    "hauteur": l_imp["hauteur"],[span_207](start_span)[span_207](end_span)
                                    "hauteur_maquette": l_imp["hauteur_maquette"],[span_208](start_span)[span_208](end_span)
                                    "largeur": l_imp["largeur"],[span_209](start_span)[span_209](end_span)
                                    "epaisseur": l_imp["epaisseur"],[span_210](start_span)[span_210](end_span)
                                    "ne_pas_rogner": False,[span_211](start_span)[span_211](end_span)
                                    "traitement": "T1",[span_212](start_span)[span_212](end_span)
                                    "type_reliure": "Bradel",[span_213](start_span)[span_213](end_span)
                                    "type_couture": "Cahiers machine",[span_214](start_span)[span_214](end_span)
                                    "agraphes": False,[span_215](start_span)[span_215](end_span)
                                    "nombre_cahiers": 0,[span_216](start_span)[span_216](end_span)
                                    "sans_titrage": False,[span_217](start_span)[span_217](end_span)
                                    "titrage_sens": l_imp["sens_titrage"],[span_218](start_span)[span_218](end_span)
                                    "lignes_sup": 0,[span_219](start_span)[span_219](end_span)
                                    "titrage_couleur": "OR",[span_220](start_span)[span_220](end_span)
                                    "police": "Elzévir",[span_221](start_span)[span_221](end_span)
                                    "police_style": "Simple",[span_222](start_span)[span_222](end_span)
                                    "type_toile": "Buckram",[span_223](start_span)[span_223](end_span)
                                    "couleur": "Noir",[span_224](start_span)[span_224](end_span)
                                    "cocher_piece_titre": l_imp["cocher_piece_titre"],[span_225](start_span)[span_225](end_span)
                                    "couleur_pieces_toile": l_imp["couleur_pieces_toile"],[span_226](start_span)[span_226](end_span)
                                    "marquage_pieces": "OR",[span_227](start_span)[span_227](end_span)
                                    "nombre_pieces_titre": l_imp["nombre_pieces_titre"],[span_228](start_span)[span_228](end_span)
                                    "supplement_1": "",[span_229](start_span)[span_229](end_span)
                                    "supplement_2": "",[span_230](start_span)[span_230](end_span)
                                    "supplement_3": "",[span_231](start_span)[span_231](end_span)
                                    "supplement_4": "[span_232](start_span)"[span_232](end_span)
                                }[span_233](start_span)[span_233](end_span)
                                enregistrer_ou_mettre_a_jour_livre(donnees_fiche_imp)[span_234](start_span)[span_234](end_span)
                                
                                json_lignes = json.dumps(l_imp["df_lignes"].to_dict(orient="records"), ensure_ascii=False)[span_235](start_span)[span_235](end_span)
                                donnees_titrage_imp = {[span_236](start_span)[span_236](end_span)
                                    "nom_client": nom_client_valide.strip(),[span_237](start_span)[span_237](end_span)
                                    "numero_train": num_train_final.strip(),[span_238](start_span)[span_238](end_span)
                                    "numero_livre": n_livre,[span_239](start_span)[span_239](end_span)
                                    "date_saisie": str(datetime.now().date()),[span_240](start_span)[span_240](end_span)
                                    "lignes_json": json_lignes,[span_241](start_span)[span_241](end_span)
                                    "pieces_json": "[]",[span_242](start_span)[span_242](end_span)
                                }[span_243](start_span)[span_243](end_span)
                                supabase.table("titrage_system3").upsert([span_244](start_span)[span_244](end_span)
                                    donnees_titrage_imp,[span_245](start_span)[span_245](end_span)
                                    on_conflict="nom_client,numero_train,numero_livre[span_246](start_span)"[span_246](end_span)
                                ).execute()[span_247](start_span)[span_247](end_span)
                                
                            st.success(f"🎉 Importation terminée ! {len(livres_importes)} fiches créées dans le train {num_train_final}.")[span_248](start_span)[span_248](end_span)
                            st.session_state["train_selectionne_apres_import"] = num_train_final[span_249](start_span)[span_249](end_span)
                            st.rerun()[span_250](start_span)[span_250](end_span)

            st.write("---")[span_251](start_span)[span_251](end_span)
            # Étape 2 : Sélection du train
            options_train = ["-- Choisir un train --", "[+] Créer un nouveau train automatiquement"] + liste_trains_existants[span_252](start_span)[span_252](end_span)
            
            index_defaut_train = 0[span_253](start_span)[span_253](end_span)
            if "train_selectionne_apres_import" in st.session_state and st.session_state["train_selectionne_apres_import"] in options_train:[span_254](start_span)[span_254](end_span)
                index_defaut_train = options_train.index(st.session_state["train_selectionne_apres_import"])[span_255](start_span)[span_255](end_span)
                del st.session_state["train_selectionne_apres_import"][span_256](start_span)[span_256](end_span)

            train_selectionne = st.selectbox("2. Sélectionner le n° de train", options=options_train, index=index_defaut_train)[span_257](start_span)[span_257](end_span)
            
            if train_selectionne == "-- Choisir un train --":[span_258](start_span)[span_258](end_span)
                st.info("💡 Sélectionnez un numéro de train existant ou demandez une création automatique.")[span_259](start_span)[span_259](end_span)
                train_charge_valide = False[span_260](start_span)[span_260](end_span)
            else:
                train_charge_valide = True[span_261](start_span)[span_261](end_span)
                if train_selectionne == "[+] Créer un nouveau train automatiquement":[span_262](start_span)[span_262](end_span)
                    numero_train = prochain_train_auto[span_263](start_span)[span_263](end_span)
                else:
                    numero_train = train_selectionne[span_264](start_span)[span_264](end_span)

    if train_charge_valide:[span_265](start_span)[span_265](end_span)
        with col_saisie:[span_266](start_span)[span_266](end_span)
            st.write("---")[span_267](start_span)[span_267](end_span)
            st.header(f"📋 Saisie de la fiche — Train : {numero_train}")[span_268](start_span)[span_268](end_span)
            
            num_livre_en_cours = 1[span_269](start_span)[span_269](end_span)
            donnees_edition = None[span_270](start_span)[span_270](end_span)
            if "livre_selectionne" in st.session_state:[span_271](start_span)[span_271](end_span)
                num_livre_en_cours = st.session_state.livre_selectionne[span_272](start_span)[span_272](end_span)
                donnees_edition = recuperer_livre_specifique(nom_client_valide, numero_train, num_livre_en_cours)[span_273](start_span)[span_273](end_span)
                st.warning(f"🔄 Modification active : Livre N° {num_livre_en_cours}")[span_274](start_span)[span_274](end_span)
                if st.button("❌ Annuler la modification (Retour au mode création)"):[span_275](start_span)[span_275](end_span)
                    del st.session_state.livre_selectionne[span_276](start_span)[span_276](end_span)
                    st.rerun()[span_277](start_span)[span_277](end_span)
            else:
                num_livre_en_cours = determiner_prochain_numero_livre(nom_client_valide, numero_train)[span_278](start_span)[span_278](end_span)
                st.info(f"✨ Mode Création : Nouveau Livre N° {num_livre_en_cours}")[span_279](start_span)[span_279](end_span)

            st.write("---")[span_280](start_span)[span_280](end_span)
            nature_doc = st.radio("Nature :", ["Monographie (Mono)", "Périodique (Pério)"], horizontal=True, index=0 if donnees_edition and donnees_edition["nature_doc"] == "Monographie (Mono)" else (1 if donnees_edition and donnees_edition["nature_doc"] == "Périodique (Pério)" else 0))[span_281](start_span)[span_281](end_span)
            text_doc = st.radio("État :", ["Neuf", "Usagé"], horizontal=True, index=0 if donnees_edition and donnees_edition["text_doc"] == "Neuf" else (1 if donnees_edition and donnees_edition["text_doc"] == "Usagé" else 0))[span_282](start_span)[span_282](end_span)

            cocher_autre = st.checkbox("Autre (Matières spécifiques)", value=True if donnees_edition and donnees_edition["option_autre"] != "N/A" else False)[span_283](start_span)[span_283](end_span)
            option_autre = "N/A[span_284](start_span)"[span_284](end_span)
            if cocher_autre:[span_285](start_span)[span_285](end_span)
                idx_opt = ["Cuir", "1/2 cuir", "1/2 toile"].index(donnees_edition["option_autre"]) if donnees_edition and donnees_edition["option_autre"] in ["Cuir", "1/2 cuir", "1/2 toile"] else 0[span_286](start_span)[span_286](end_span)
                option_autre = st.radio("Finition :", ["Cuir", "1/2 cuir", "1/2 toile"], horizontal=True, index=idx_opt)[span_287](start_span)[span_287](end_span)

            st.markdown("**Reprographie :**")[span_288](start_span)[span_288](end_span)
            col_scanne, col_report, _ = st.columns([1, 1, 3])[span_289](start_span)[span_289](end_span)
            with col_scanne:[span_290](start_span)[span_290](end_span)
                repro_scanne = st.checkbox("Scannée", value=bool(donnees_edition["repro_scanne"]) if donnees_edition else False)[span_291](start_span)[span_291](end_span)
            with col_report:[span_292](start_span)[span_292](end_span)
                repro_report = st.checkbox("Report", value=bool(donnees_edition["repro_report"]) if donnees_edition else False)[span_293](start_span)[span_293](end_span)

            st.write("---")[span_294](start_span)[span_294](end_span)
            st.subheader("3. Désignation format")[span_295](start_span)[span_295](end_span)
            col_dim1, col_dim2, col_dim3, col_dim4 = st.columns(4)[span_296](start_span)[span_296](end_span)
            with col_dim1: largeur = st.number_input("Largeur (mm)", min_value=0, value=int(donnees_edition["largeur"]) if donnees_edition else 160, step=1)[span_297](start_span)[span_297](end_span)
            with col_dim2: hauteur = st.number_input("Hauteur (mm)", min_value=0, value=int(donnees_edition["hauteur"]) if donnees_edition else 220, step=1)[span_298](start_span)[span_298](end_span)
            with col_dim3: epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=int(donnees_edition["epaisseur"]) if donnees_edition else 20, step=1)[span_299](start_span)[span_299](end_span)
            with col_dim4: ne_pas_rogner = st.checkbox("Ne pas rogner", value=bool(donnees_edition["ne_pas_rogner"]) if donnees_edition else False)[span_300](start_span)[span_300](end_span)

            format_detecte = determiner_categorie_format(largeur, hauteur)[span_301](start_span)[span_301](end_span)
            st.success(f"📐 **Format détecté** : {format_detecte}")[span_302](start_span)[span_302](end_span)

            st.subheader("4. Traitements & Reliure")[span_303](start_span)[span_303](end_span)
            c_trt1, c_trt2, c_trt3 = st.columns(3)[span_304](start_span)[span_304](end_span)
            list_trt = ["T1", "T2", "T3", "T4", "T5", "T6"][span_305](start_span)[span_305](end_span)
            with c_trt1: traitement = st.selectbox("Traitement", list_trt, index=list_trt.index(donnees_edition["traitement"]) if donnees_edition and donnees_edition["traitement"] in list_trt else 0)[span_306](start_span)[span_306](end_span)
            list_rel = ["Bradel", "Emboîtage", "Passure en carton"][span_307](start_span)[span_307](end_span)
            with c_trt2: type_reliure = st.selectbox("Type de reliure", list_rel, index=list_rel.index(donnees_edition["type_reliure"]) if donnees_edition and donnees_edition["type_reliure"] in list_rel else 0)[span_308](start_span)[span_308](end_span)
            list_cou = ["Cahiers machine", "Surjeté", "Cahier manuel"][span_309](start_span)[span_309](end_span)
            with c_trt3: type_couture = st.selectbox("Type de couture", list_cou, index=list_cou.index(donnees_edition["type_couture"]) if donnees_edition and donnees_edition["type_couture"] in list_cou else 0)[span_310](start_span)[span_310](end_span)

            agraphes = False[span_311](start_span)[span_311](end_span)
            nombre_cahiers = 0[span_312](start_span)[span_312](end_span)
            if type_couture == "Cahier manuel":[span_313](start_span)[span_313](end_span)
                c_cah1, c_cah2 = st.columns(2)[span_314](start_span)[span_314](end_span)
                with c_cah1: agraphes = st.checkbox("Présence d'agraphes", value=bool(donnees_edition["agraphes"]) if donnees_edition else False)[span_315](start_span)[span_315](end_span)
                with c_cah2: nombre_cahiers = st.number_input("Nombre de cahiers", min_value=0, value=int(donnees_edition["nombre_cahiers"]) if donnees_edition else 0, step=1)[span_316](start_span)[span_316](end_span)

            st.write("---")[span_317](start_span)[span_317](end_span)
            st.subheader("5. Spécifications du titrage")[span_318](start_span)[span_318](end_span)
            sans_titrage = st.checkbox("**Pas de titrage**", value=bool(donnees_edition["sans_titrage"]) if donnees_edition else False)[span_319](start_span)[span_319](end_span)
            titrage_sens = "N/A[span_320](start_span)"[span_320](end_span)
            lignes_sup = 0[span_321](start_span)[span_321](end_span)
            titrage_couleur = "N/A[span_322](start_span)"[span_322](end_span)
            police = "N/A[span_323](start_span)"[span_323](end_span)
            police_style = "Simple[span_324](start_span)"[span_324](end_span)
            
            if not sans_titrage:[span_325](start_span)[span_325](end_span)
                c_tit1, c_tit2, c_tit3, c_tit4, c_tit5 = st.columns(5)[span_326](start_span)[span_326](end_span)
                with c_tit1:[span_327](start_span)[span_327](end_span)
                    idx_sens_defaut = 1[span_328](start_span)[span_328](end_span)
                    if donnees_edition and "titrage_sens" in donnees_edition:[span_329](start_span)[span_329](end_span)
                        if donnees_edition["titrage_sens"] == "Long":[span_330](start_span)[span_330](end_span)
                            idx_sens_defaut = 0[span_331](start_span)[span_331](end_span)
                        elif donnees_edition["titrage_sens"] in ["Classique", "Travers"]:[span_332](start_span)[span_332](end_span)
                            idx_sens_defaut = 1[span_333](start_span)[span_333](end_span)

                    titrage_sens = st.radio("Sens", ["Long", "Classique"], horizontal=True, index=idx_sens_defaut)[span_334](start_span)[span_334](end_span)
                with c_tit2: lignes_sup = st.number_input("Lignes sup", min_value=0, value=int(donnees_edition["lignes_sup"]) if donnees_edition else 0, step=1)[span_335](start_span)[span_335](end_span)
                list_marq = ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"][span_336](start_span)[span_336](end_span)
                with c_tit3: titrage_couleur = st.selectbox("Marquage", list_marq, index=list_marq.index(donnees_edition["titrage_couleur"]) if donnees_edition and donnees_edition["titrage_couleur"] in list_marq else 0)[span_337](start_span)[span_337](end_span)
                with c_tit4: police = st.radio("Police", ["Elzévir", "Baton"], horizontal=True, index=0 if donnees_edition and donnees_edition["police"] == "Elzévir" else (1 if donnees_edition and donnees_edition["police"] in ["Baton", "Baskerville"] else 0))[span_338](start_span)[span_338](end_span)
                
                with c_tit5:[span_339](start_span)[span_339](end_span)
                    idx_style = 0 if (not donnees_edition or donnees_edition.get("police_style") != "Double") else 1[span_340](start_span)[span_340](end_span)
                    police_style = st.selectbox("Empreinte", ["Simple", "Double"], index=idx_style, help="Simple = trait fin standard | Double = composteur / frappe double trait")[span_341](start_span)[span_341](end_span)

            st.write("---")[span_342](start_span)[span_342](end_span)
            st.subheader("6. Habillage")[span_343](start_span)[span_343](end_span)
            c_toi1, c_toi2 = st.columns(2)[span_344](start_span)[span_344](end_span)
            
            list_toile = charger_types_toile_supabase()[span_345](start_span)[span_345](end_span)
            
            with c_toi1:[span_346](start_span)[span_346](end_span)
                type_toile = st.selectbox([span_347](start_span)[span_347](end_span)
                    "Type de toile",[span_348](start_span)[span_348](end_span)
                    list_toile,[span_349](start_span)[span_349](end_span)
                    index=list_toile.index(donnees_edition["type_toile"]) if donnees_edition and donnees_edition["type_toile"] in list_toile else 0[span_350](start_span)[span_350](end_span)
                )[span_351](start_span)[span_351](end_span)
            
            couleurs_filtrees = charger_couleurs_par_toile_supabase(type_toile)[span_352](start_span)[span_352](end_span)
            
            with c_toi2:[span_353](start_span)[span_353](end_span)
                if couleurs_filtrees:[span_354](start_span)[span_354](end_span)
                    couleur = st.selectbox([span_355](start_span)[span_355](end_span)
                        "Couleur de la toile",[span_356](start_span)[span_356](end_span)
                        options=couleurs_filtrees,[span_357](start_span)[span_357](end_span)
                        index=couleurs_filtrees.index(donnees_edition["couleur"]) if donnees_edition and donnees_edition["couleur"] in couleurs_filtrees else 0[span_358](start_span)[span_358](end_span)
                    )[span_359](start_span)[span_359](end_span)
                else:
                    st.warning("⚠️ Aucune couleur configurée pour cette toile.")[span_360](start_span)[span_360](end_span)
                    couleur = "N/A[span_361](start_span)"[span_361](end_span)

            st.write("---")[span_362](start_span)[span_362](end_span)
            st.subheader("7. Pièce de titre & Suppléments")[span_363](start_span)[span_363](end_span)
            
            cocher_piece_titre = st.checkbox([span_364](start_span)[span_364](end_span)
                "**Activer une pièce de titre**",[span_365](start_span)[span_365](end_span)
                value=bool(donnees_edition["cocher_piece_titre"]) if donnees_edition else False[span_366](start_span)[span_366](end_span)
            )[span_367](start_span)[span_367](end_span)
            
            couleur_pieces_toile = "N/A[span_368](start_span)"[span_368](end_span)
            marquage_pieces = "N/A[span_369](start_span)"[span_369](end_span)
            valeur_nb_pieces_defaut = int(donnees_edition["nombre_pieces_titre"]) if (donnees_edition and "nombre_pieces_titre" in donnees_edition and donnees_edition["nombre_pieces_titre"] is not None) else 1[span_370](start_span)[span_370](end_span)
            
            if cocher_piece_titre:[span_371](start_span)[span_371](end_span)
                c_p1, c_p2, c_p3 = st.columns(3)[span_372](start_span)[span_372](end_span)
                with c_p1:[span_373](start_span)[span_373](end_span)
                    couleur_pieces_toile = st.selectbox([span_374](start_span)[span_374](end_span)
                        "Couleur de la pièce",[span_375](start_span)[span_375](end_span)
                        options=liste_couleurs_generique,[span_376](start_span)[span_376](end_span)
                        index=liste_couleurs_generique.index(donnees_edition["couleur_pieces_toile"]) if donnees_edition and donnees_edition["couleur_pieces_toile"] in liste_couleurs_generique else 0[span_377](start_span)[span_377](end_span)
                    )[span_378](start_span)[span_378](end_span)
                list_mp = ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"][span_379](start_span)[span_379](end_span)
                with c_p2:[span_380](start_span)[span_380](end_span)
                    marquage_pieces = st.selectbox([span_381](start_span)[span_381](end_span)
                        "Marquage de la pièce",[span_382](start_span)[span_382](end_span)
                        list_mp,[span_383](start_span)[span_383](end_span)
                        index=list_mp.index(donnees_edition["marquage_pieces"]) if donnees_edition and donnees_edition["marquage_pieces"] in list_mp else 0[span_384](start_span)[span_384](end_span)
                    )[span_385](start_span)[span_385](end_span)
                with c_p3:[span_386](start_span)[span_386](end_span)
                    nombre_pieces_titre = st.number_input([span_387](start_span)[span_387](end_span)
                        "Nombre de pièce(s) de titre",[span_388](start_span)[span_388](end_span)
                        min_value=1,[span_389](start_span)[span_389](end_span)
                        value=valeur_nb_pieces_defaut,[span_390](start_span)[span_390](end_span)
                        step=1[span_391](start_span)[span_391](end_span)
                    )[span_392](start_span)[span_392](end_span)
            else: 
                nombre_pieces_titre = valeur_nb_pieces_defaut[span_393](start_span)[span_393](end_span)

            st.write("---")[span_394](start_span)[span_394](end_span)
            st.subheader("8. Suppléments optionnels (Max 4)")[span_395](start_span)[span_395](end_span)

            def afficher_prix_indicatif(nom_supplement):
                if nom_supplement and nom_supplement != "-- Aucun --":[span_396](start_span)[span_396](end_span)
                    prix = PRIX_SUPPLEMENTS.get(nom_supplement, 0.00)[span_397](start_span)[span_397](end_span)
                    st.caption(f"💰 *Prix indicatif : {prix:.2f} €*")[span_398](start_span)[span_398](end_span)
                else:
                    st.caption(" ")[span_399](start_span)[span_399](end_span)

            sup1_def = donnees_edition["supplement_1"] if (donnees_edition and donnees_edition["supplement_1"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --[span_400](start_span)"[span_400](end_span)
            sup2_def = donnees_edition["supplement_2"] if (donnees_edition and donnees_edition["supplement_2"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --[span_401](start_span)"[span_401](end_span)
            sup3_def = donnees_edition["supplement_3"] if (donnees_edition and donnees_edition["supplement_3"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --[span_402](start_span)"[span_402](end_span)
            sup4_def = donnees_edition["supplement_4"] if (donnees_edition and donnees_edition["supplement_4"] in OPTIONS_SUPPLEMENTS) else "-- Aucun --[span_403](start_span)"[span_403](end_span)

            liste_choix_sups = ["-- Aucun --"] + OPTIONS_SUPPLEMENTS[span_404](start_span)[span_404](end_span)
            c_sup1, c_sup2 = st.columns(2)[span_405](start_span)[span_405](end_span)
            with c_sup1:[span_406](start_span)[span_406](end_span)
                supplement_1 = st.selectbox("Supplément 1", options=liste_choix_sups, index=liste_choix_sups.index(sup1_def))[span_407](start_span)[span_407](end_span)
                afficher_prix_indicatif(supplement_1)[span_408](start_span)[span_408](end_span)
                supplement_2 = st.selectbox("Supplément 2", options=liste_choix_sups, index=liste_choix_sups.index(sup2_def))[span_409](start_span)[span_409](end_span)
                afficher_prix_indicatif(supplement_2)[span_410](start_span)[span_410](end_span)
            with c_sup2:[span_411](start_span)[span_411](end_span)
                supplement_3 = st.selectbox("Supplément 3", options=liste_choix_sups, index=liste_choix_sups.index(sup3_def))[span_412](start_span)[span_412](end_span)
                afficher_prix_indicatif(supplement_3)[span_413](start_span)[span_413](end_span)
                supplement_4 = st.selectbox("Supplément 4", options=liste_choix_sups, index=liste_choix_sups.index(sup4_def))[span_414](start_span)[span_414](end_span)
                afficher_prix_indicatif(supplement_4)[span_415](start_span)[span_415](end_span)

            total_sups = sum([PRIX_SUPPLEMENTS.get(s, 0.0) for s in [supplement_1, supplement_2, supplement_3, supplement_4]])[span_416](start_span)[span_416](end_span)
            if total_sups > 0:[span_417](start_span)[span_417](end_span)
                st.info(f"📊 **Sous-total suppléments pour ce livre :** {total_sups:.2f} €")[span_418](start_span)[span_418](end_span)

            st.write("---")[span_419](start_span)[span_419](end_span)
            if st.button("💾 Valider l'enregistrement", type="primary", use_container_width=True):[span_420](start_span)[span_420](end_span)
                donnees_fiche = {[span_421](start_span)[span_421](end_span)
                    "nom_client": nom_client_valide.strip(),[span_422](start_span)[span_422](end_span)
                    "numero_train": numero_train.strip(),[span_423](start_span)[span_423](end_span)
                    "numero_livre": num_livre_en_cours,[span_424](start_span)[span_424](end_span)
                    "nature_doc": nature_doc,[span_425](start_span)[span_425](end_span)
                    "text_doc": text_doc,[span_426](start_span)[span_426](end_span)
                    "option_autre": option_autre,[span_427](start_span)[span_427](end_span)
                    "repro_scanne": repro_scanne,[span_428](start_span)[span_428](end_span)
                    "repro_report": repro_report,[span_429](start_span)[span_429](end_span)
                    "hauteur": hauteur,[span_430](start_span)[span_430](end_span)
                    "hauteur_maquette": hauteur + 5,[span_431](start_span)[span_431](end_span)
                    "largeur": largeur,[span_432](start_span)[span_432](end_span)
                    "epaisseur": epaisseur,[span_433](start_span)[span_433](end_span)
                    "ne_pas_rogner": ne_pas_rogner,[span_434](start_span)[span_434](end_span)
                    "traitement": traitement,[span_435](start_span)[span_435](end_span)
                    "type_reliure": type_reliure,[span_436](start_span)[span_436](end_span)
                    "type_couture": type_couture,[span_437](start_span)[span_437](end_span)
                    "agraphes": agraphes,[span_438](start_span)[span_438](end_span)
                    "nombre_cahiers": nombre_cahiers,[span_439](start_span)[span_439](end_span)
                    "sans_titrage": sans_titrage,[span_440](start_span)[span_440](end_span)
                    "titrage_sens": titrage_sens,[span_441](start_span)[span_441](end_span)
                    "lignes_sup": lignes_sup,[span_442](start_span)[span_442](end_span)
                    "titrage_couleur": titrage_couleur,[span_443](start_span)[span_443](end_span)
                    "police": police,[span_444](start_span)[span_444](end_span)
                    "police_style": police_style,[span_445](start_span)[span_445](end_span)
                    "type_toile": type_toile,[span_446](start_span)[span_446](end_span)
                    "couleur": couleur,[span_447](start_span)[span_447](end_span)
                    "cocher_piece_titre": cocher_piece_titre,[span_448](start_span)[span_448](end_span)
                    "couleur_pieces_toile": couleur_pieces_toile,[span_449](start_span)[span_449](end_span)
                    "marquage_pieces": marquage_pieces,[span_450](start_span)[span_450](end_span)
                    "nombre_pieces_titre": nombre_pieces_titre,[span_451](start_span)[span_451](end_span)
                    "supplement_1": "" if supplement_1 == "-- Aucun --" else supplement_1,[span_452](start_span)[span_452](end_span)
                    "supplement_2": "" if supplement_2 == "-- Aucun --" else supplement_2,[span_453](start_span)[span_453](end_span)
                    "supplement_3": "" if supplement_3 == "-- Aucun --" else supplement_3,[span_454](start_span)[span_454](end_span)
                    "supplement_4": "" if supplement_4 == "-- Aucun --" else supplement_4[span_455](start_span)[span_455](end_span)
                }[span_456](start_span)[span_456](end_span)
                enregistrer_ou_mettre_a_jour_livre(donnees_fiche)[span_457](start_span)[span_457](end_span)
                st.success("Données enregistrées avec succès sur Supabase !")[span_458](start_span)[span_458](end_span)
                if "livre_selectionne" in st.session_state:[span_459](start_span)[span_459](end_span)
                    del st.session_state.livre_selectionne[span_460](start_span)[span_460](end_span)
                st.rerun()[span_461](start_span)[span_461](end_span)

        with col_visualisation:[span_462](start_span)[span_462](end_span)
            st.header("📊 Suivi en direct du Train")[span_463](start_span)[span_463](end_span)
            st.subheader(f"Train : {numero_train}")[span_464](start_span)[span_464](end_span)
            livres_train = recuperer_livres_du_train(nom_client_valide, numero_train)[span_465](start_span)[span_465](end_span)
            
            # --- SECTION DE SUPPRESSION COMPLÈTE DU TRAIN (AVEC DOUBLE CONFIRMATION) ---
            if livres_train and not train_selectionne.startswith("[+]"):
                with st.expander("🗑️ Zone Danger — Supprimer ce train complet", expanded=False):
                    st.error(f"⚠️ Vous vous apprêtez à supprimer le Train **{numero_train}** ({len(livres_train)} livre(s)) et **tous leurs titrages associés**.")
                    cle_conf = f"conf_suppr_train_{nom_client_valide}_{numero_train}"
                    
                    if cle_conf not in st.session_state:
                        st.session_state[cle_conf] = False

                    if not st.session_state[cle_conf]:
                        if st.button(f"Demander la suppression du Train {numero_train}", type="secondary", use_container_width=True):
                            st.session_state[cle_conf] = True
                            st.rerun()
                    else:
                        st.warning("🚨 **Confirmation requise :** Cette action est irréversible !")
                        col_conf1, col_conf2 = st.columns(2)
                        with col_conf1:
                            if st.button("🔥 CONFIRMER LA SUPPRESSION", type="primary", use_container_width=True):
                                if supprimer_train_complet(nom_client_valide, numero_train):
                                    st.success(f"✅ Le Train {numero_train} a été entièrement supprimé.")
                                    del st.session_state[cle_conf]
                                    if "livre_selectionne" in st.session_state:
                                        del st.session_state.livre_selectionne
                                    st.rerun()
                        with col_conf2:
                            if st.button("❌ Annuler", use_container_width=True):
                                st.session_state[cle_conf] = False
                                st.rerun()

            if livres_train:[span_466](start_span)[span_466](end_span)
                df_train = pd.DataFrame(livres_train, columns=["N° Livre", "Nature", "État", "Largeur", "Hauteur", "Reliure", "Couleur Toile", "Pièce Titre active"])[span_467](start_span)[span_467](end_span)
                
                reponse_tableau = st.dataframe([span_468](start_span)[span_468](end_span)
                    df_train,[span_469](start_span)[span_469](end_span)
                    use_container_width=True,[span_470](start_span)[span_470](end_span)
                    hide_index=True,[span_471](start_span)[span_471](end_span)
                    selection_mode="single-row",[span_472](start_span)[span_472](end_span)
                    on_select="rerun[span_473](start_span)"[span_473](end_span)
                )[span_474](start_span)[span_474](end_span)
                
                selection = reponse_tableau.get("selection", {})[span_475](start_span)[span_475](end_span)
                lignes_cochees = selection.get("rows", [])[span_476](start_span)[span_476](end_span)
                
                if lignes_cochees:[span_477](start_span)[span_477](end_span)
                    index_ligne = lignes_cochees[0][span_478](start_span)[span_478](end_span)
                    num_selectionne = int(df_train.iloc[index_ligne]["N° Livre"])[span_479](start_span)[span_479](end_span)
                    
                    st.write("---")[span_480](start_span)[span_480](end_span)
                    st.subheader(f"⚙️ Actions sur le Livre N° {num_selectionne}")[span_481](start_span)[span_481](end_span)
                    
                    c_act1, c_act2 = st.columns(2)[span_482](start_span)[span_482](end_span)
                    
                    with c_act1:[span_483](start_span)[span_483](end_span)
                        if st.button(f"✏️ Modifier le N° {num_selectionne}", use_container_width=True, type="primary"):[span_484](start_span)[span_484](end_span)
                            st.session_state.livre_selectionne = num_selectionne[span_485](start_span)[span_485](end_span)
                            st.rerun()[span_486](start_span)[span_486](end_span)
                            
                    with c_act2:[span_487](start_span)[span_487](end_span)
                        if st.button(f"🗑️ Supprimer le N° {num_selectionne}", type="secondary", use_container_width=True):[span_488](start_span)[span_488](end_span)
                            if supprimer_livre_specifique(nom_client_valide, numero_train, num_selectionne):[span_489](start_span)[span_489](end_span)
                                st.success(f"✅ Livre N° {num_selectionne} supprimé.")[span_490](start_span)[span_490](end_span)
                                if "livre_selectionne" in st.session_state and st.session_state.livre_selectionne == num_selectionne:[span_491](start_span)[span_491](end_span)
                                    del st.session_state.livre_selectionne[span_492](start_span)[span_492](end_span)
                                st.rerun()[span_493](start_span)[span_493](end_span)
                else:
                    st.info("💡 Cochez la case au début d'une ligne du tableau pour **Modifier** ou **Supprimer** un livre.")[span_494](start_span)[span_494](end_span)
            else: 
                st.info("Aucun livre encore enregistré dans ce Train.")[span_495](start_span)[span_495](end_span)
