import json
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client


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
  return sorted(
      list(set([row["numero_train"] for row in reponse.data])), reverse=True
  )


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


def charger_types_toile_supabase():
  supabase = obtenir_client_supabase()
  try:
    reponse = (
        supabase.table("referentiel_toiles").select("type_toile").execute()
    )
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
    return (
        couleurs
        if couleurs
        else [
            "Noir",
            "Rouge",
            "Bleu",
            "Vert",
            "Jaune",
            "Orange",
            "Violet",
            "Marron",
        ]
    )
  except Exception:
    return [
        "Noir",
        "Rouge",
        "Bleu",
        "Vert",
        "Jaune",
        "Orange",
        "Violet",
        "Marron",
    ]


def recuperer_specs_livre(client, train, num_livre):
  supabase = obtenir_client_supabase()
  num_livre_int = int(num_livre)

  try:
    reponse = (
        supabase.table("fiches_livres")
        .select(
            "largeur, hauteur, epaisseur, type_toile, couleur, titrage_couleur,"
            " cocher_piece_titre, couleur_pieces_toile, marquage_pieces,"
            " nombre_pieces_titre, sens_titrage"
        )
        .eq("nom_client", str(client).strip())
        .eq("numero_train", str(train).strip())
        .eq("numero_livre", num_livre_int)
        .execute()
    )

    if reponse.data:
      r = reponse.data[0]
      return (
          r.get("hauteur") or 220,
          r.get("largeur") or 160,
          r.get("epaisseur") or 20,
          r.get("type_toile") or "Buckram",
          r.get("couleur") or "Noir",
          r.get("titrage_couleur") or "OR",
          bool(r.get("cocher_piece_titre", False)),
          r.get("couleur_pieces_toile") or "Rouge",
          r.get("marquage_pieces") or "OR",
          r.get("nombre_pieces_titre") or 1,
          r.get("sens_titrage") or "Classique",
      )
  except Exception:
    try:
      reponse = (
          supabase.table("fiches_livres")
          .select(
              "largeur, hauteur, epaisseur, type_toile, couleur,"
              " titrage_couleur, cocher_piece_titre, couleur_pieces_toile,"
              " marquage_pieces, nombre_pieces_titre"
          )
          .eq("nom_client", str(client).strip())
          .eq("numero_train", str(train).strip())
          .eq("numero_livre", num_livre_int)
          .execute()
      )

      if reponse.data:
        r = reponse.data[0]
        return (
            r.get("hauteur") or 220,
            r.get("largeur") or 160,
            r.get("epaisseur") or 20,
            r.get("type_toile") or "Buckram",
            r.get("couleur") or "Noir",
            r.get("titrage_couleur") or "OR",
            bool(r.get("cocher_piece_titre", False)),
            r.get("couleur_pieces_toile") or "Rouge",
            r.get("marquage_pieces") or "OR",
            r.get("nombre_pieces_titre") or 1,
            "Classique",
        )
    except Exception as e:
      st.warning("Chargement des valeurs par défaut: " + str(e))

  return 220, 160, 20, "Buckram", "Noir", "OR", False, "Rouge", "OR", 1, "Classique"


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
      df_lignes = (
          pd.DataFrame(json.loads(rec["lignes_json"]))
          if rec.get("lignes_json")
          else None
      )
      df_pieces = (
          pd.DataFrame(json.loads(rec["pieces_json"]))
          if rec.get("pieces_json")
          else None
      )
      return df_lignes, df_pieces
  except Exception:
    pass
  return None, None


def sauvegarder_titrage_sur_base(
    client, train, num_livre, date_saisie, df_lignes, df_pieces, specs_modifiees
):
  supabase = obtenir_client_supabase()

  num_livre_int = int(num_livre)
  json_lignes = json.dumps(
      df_lignes.to_dict(orient="records"), ensure_ascii=False
  )
  json_pieces = (
      json.dumps(df_pieces.to_dict(orient="records"), ensure_ascii=False)
      if df_pieces is not None
      else "[]"
  )

  donnees_titrage = {
      "nom_client": str(client).strip(),
      "numero_train": str(train).strip(),
      "numero_livre": num_livre_int,
      "date_saisie": str(date_saisie),
      "lignes_json": json_lignes,
      "pieces_json": json_pieces,
  }

  try:
    check = (
        supabase.table("titrage_system3")
        .select("numero_livre")
        .eq("nom_client", str(client).strip())
        .eq("numero_train", str(train).strip())
        .eq("numero_livre", num_livre_int)
        .execute()
    )
    if check.data:
      (
          supabase.table("titrage_system3")
          .update(donnees_titrage)
          .eq("nom_client", str(client).strip())
          .eq("numero_train", str(train).strip())
          .eq("numero_livre", num_livre_int)
          .execute()
      )
    else:
      supabase.table("titrage_system3").insert(donnees_titrage).execute()

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
    "Noir": "#1a1a1a",
    "Rouge": "#8b0000",
    "Bleu": "#0f2b5c",
    "Vert": "#1e4620",
    "Jaune": "#d4af37",
    "Orange": "#d96b27",
    "Violet": "#4a235a",
    "Marron": "#5c4033",
}

HEX_COULEURS_MARQUAGE = {
    "OR": "#ffd700",
    "ARGENT": "#e0e0e0",
    "BLANC": "#ffffff",
    "NOIR": "#000000",
    "AUTRE": "#c0c0c0",
}

st.set_page_config(page_title="Titrage Système 3", layout="wide")
st.title("📟 Module de Composition Spécifique — Titrage Système 3")

liste_clients_existants = lister_tous_les_clients()

if not liste_clients_existants:
  st.warning("⚠️ Créez d'abord un client pour utiliser le module de titrage.")
else:
  col_form_saisie, col_gabarit_visualisation = st.columns([1.2, 0.8])

  with col_form_saisie:
    st.subheader("Clé de sélection du Livre")
    c_meta1, c_meta2 = st.columns(2)
    with c_meta1:
      t3_client = st.selectbox(
          "1. Client référent", options=liste_clients_existants
      )
      t3_trains = lister_les_trains_du_client(t3_client)
      t3_train_sel = st.selectbox(
          "2. N° de train", options=["-- Choisir --"] + t3_trains
      )

    livre_charge_valide = False
    with c_meta2:
      t3_date = st.date_input("Date d'atelier", value=datetime.now())
      if t3_train_sel != "-- Choisir --":
        liste_livres = ["-- Choisir un livre --"] + lister_les_livres_du_train(
            t3_client, t3_train_sel
        )
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
          ) = recuperer_specs_livre(t3_client, t3_train_sel, t3_livre_num)
          livre_charge_valide = True
      else:
        t3_livre_num = None

  if not livre_charge_valide:
    st.write("---")
    st.info(
        "💡 **En attente d'instructions :** Veuillez sélectionner un **N° de"
        " train** et un **N° de livre** existants."
    )
  else:
    with col_form_saisie:
      st.write("---")
      st.subheader("📐 Caractéristiques modifiables du livre & du dos")

      c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)
      with c_dim1:
        t3_haut_titre = st.number_input(
            "Hauteur du titre (mm)",
            min_value=10,
            max_value=1000,
            value=int(init_haut),
            step=1,
        )

      with c_dim2:
        t3_haut_maquette = st.number_input(
            "Hauteur maquette (mm)",
            min_value=10,
            max_value=1000,
            value=int(init_haut + 5),
            step=1,
        )

      with c_dim3:
        t3_larg_dos_utile = st.number_input(
            "Largeur utile du dos (mm)",
            min_value=5,
            max_value=500,
            value=int(init_ep + 10),
            step=1,
        )

      with c_dim4:
        idx_m = (
            ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"].index(init_marquage)
            if init_marquage in ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"]
            else 0
        )
        t3_marquage_nom = st.selectbox(
            "Marquage général",
            ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"],
            index=idx_m,
        )

      c_toi1, c_toi2, c_toi3 = st.columns(3)
      types_toiles_dispos = charger_types_toile_supabase()
      with c_toi1:
        idx_t = (
            types_toiles_dispos.index(init_type_toile)
            if init_type_toile in types_toiles_dispos
            else 0
        )
        t3_type_toile = st.selectbox(
            "Type de toile", types_toiles_dispos, index=idx_t
        )

      couleurs_toile_dispos = charger_couleurs_par_toile_supabase(t3_type_toile)
      with c_toi2:
        idx_c = (
            couleurs_toile_dispos.index(init_couleur_toile)
            if init_couleur_toile in couleurs_toile_dispos
            else 0
        )
        t3_couleur_nom = st.selectbox(
            "Couleur de la toile", couleurs_toile_dispos, index=idx_c
        )

      with c_toi3:
        idx_s = 1 if init_sens_titrage == "Long" else 0
        t3_sens_titrage = st.selectbox(
            "Sens du titrage",
            ["Classique", "Long"],
            index=idx_s,
            help="Classique = horizontal | Long = texte couché (de bas en haut)",
        )

      st.write("---")
      st.subheader("🧩 Gestion des Pièces de titre")

      has_pieces = st.checkbox(
          "Activer la/les pièce(s) de titre", value=init_has_piece
      )

      df_lignes_existant, df_pieces_existant = recuperer_titrage_enregistre(
          t3_client, t3_train_sel, t3_livre_num
      )

      df_pieces_edite = None
      if has_pieces:
        if df_pieces_existant is not None and not df_pieces_existant.empty:
          df_pieces_initial = df_pieces_existant
        else:
          df_pieces_initial = pd.DataFrame([{
              "Position (mm depuis le bas)": int(t3_haut_maquette * 0.75),
              "Hauteur pièce (mm)": 35,
              "Couleur pièce": init_piece_couleur,
              "Couleur marquage": init_piece_marquage,
              "Titre sur pièce": "TITRE LIGNE 1\nSOUS-TITRE LIGNE 2",
          }])

        list_couleurs_gen = [
            "Noir",
            "Rouge",
            "Bleu",
            "Vert",
            "Jaune",
            "Orange",
            "Violet",
            "Marron",
        ]
        list_marquages_gen = ["OR", "ARGENT", "BLANC", "NOIR", "AUTRE"]

        editor_key_p = (
            "editor_pieces_"
            + str(t3_client)
            + "_"
            + str(t3_train_sel)
            + "_"
            + str(t3_livre_num)
        )
        df_pieces_edite = st.data_editor(
            df_pieces_initial,
            column_config={
                "Position (mm depuis le bas)": st.column_config.NumberColumn(
                    "Position bas (mm)",
                    min_value=0,
                    max_value=t3_haut_maquette,
                    step=1,
                    required=True,
                ),
                "Hauteur pièce (mm)": st.column_config.NumberColumn(
                    "Hauteur (mm)",
                    min_value=5,
                    max_value=t3_haut_maquette,
                    step=1,
                    required=True,
                ),
                "Couleur pièce": st.column_config.SelectboxColumn(
                    "Couleur pièce", options=list_couleurs_gen, required=True
                ),
                "Couleur marquage": st.column_config.SelectboxColumn(
                    "Marquage", options=list_marquages_gen, required=True
                ),
                "Titre sur pièce": st.column_config.TextColumn(
                    "Titre / Texte (Multiligne)", required=False
                ),
            },
            num_rows="dynamic",
            use_container_width=True,
            key=editor_key_p,
        )

      st.write("---")
      st.subheader(
          "✍️ Composition des lignes directes sur le dos (Position en mm)"
      )

      if df_lignes_existant is not None:
        df_lignes_initial = df_lignes_existant
      else:
        df_lignes_initial = pd.DataFrame([{
            "Hauteur du titre (mm)": int(t3_haut_maquette * 0.20),
            "Titrage": "COTE",
        }])

      editor_key_l = (
          "editor_lignes_"
          + str(t3_client)
          + "_"
          + str(t3_train_sel)
          + "_"
          + str(t3_livre_num)
      )
      df_edite_lignes = st.data_editor(
          df_lignes_initial,
          column_config={
              "Hauteur du titre (mm)": st.column_config.NumberColumn(
                  "Position (mm depuis le bas)",
                  min_value=0,
                  max_value=t3_haut_maquette,
                  step=1,
                  required=True,
              ),
              "Titrage": st.column_config.TextColumn(
                  "Texte à imprimer", required=True
              ),
          },
          num_rows="dynamic",
          use_container_width=True,
          key=editor_key_l,
      )

      st.write("---")
      if st.button(
          "💾 Sauvegarder les modifications et le titrage",
          type="primary",
          use_container_width=True,
      ):
        c_piece = (
            df_pieces_edite.iloc[0]["Couleur pièce"]
            if (df_pieces_edite is not None and not df_pieces_edite.empty)
            else init_piece_couleur
        )
        m_piece = (
            df_pieces_edite.iloc[0]["Couleur marquage"]
            if (df_pieces_edite is not None and not df_pieces_edite.empty)
            else init_piece_marquage
        )

        specs_mises_a_jour = {
            "hauteur": t3_haut_titre,
            "largeur": init_larg,
            "epaisseur": max(t3_larg_dos_utile - 10, 0),
            "type_toile": t3_type_toile,
            "couleur": t3_couleur_nom,
            "titrage_couleur": t3_marquage_nom,
            "cocher_piece_titre": has_pieces,
            "couleur_pieces_toile": c_piece,
            "marquage_pieces": m_piece,
            "nombre_pieces_titre": (
                len(df_pieces_edite) if df_pieces_edite is not None else 0
            ),
            "sens_titrage": t3_sens_titrage,
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
          st.success(
              "✅ Fiche & Composition enregistrées (Livre N°"
              + str(t3_livre_num)
              + " — Train "
              + str(t3_train_sel)
              + ")"
          )

    # --- RENDU VISUEL DYNAMIQUE ---
    with col_gabarit_visualisation:
      st.subheader("📐 Gabarit dynamique du dos à dorer")

      couleur_fond_html = HEX_COULEURS_TOILE.get(t3_couleur_nom, "#1a1a1a")
      couleur_texte_html = HEX_COULEURS_MARQUAGE.get(t3_marquage_nom, "#ffd700")

      facteur_px = 2.5
      hauteur_visuelle_px = max(min(int(t3_haut_maquette * facteur_px), 600), 350)
      largeur_visuelle_px = max(
          min(int(t3_larg_dos_utile * facteur_px), 250), 60
      )

      px_par_mm = hauteur_visuelle_px / t3_haut_maquette

      paliers_mm = list(range(0, int(t3_haut_maquette) + 1, 10))
      if paliers_mm[-1] != int(t3_haut_maquette):
        paliers_mm.append(int(t3_haut_maquette))

      is_long = t3_sens_titrage == "Long"

      html_str = (
          '<div style="display: flex; font-family: monospace; background-color:'
          " #f8f9fa; padding: 20px; border-radius: 5px; min-height: "
          + str(hauteur_visuelle_px + 60)
          + 'px;">'
      )
      html_str += (
          '<div style="position: relative; height: '
          + str(hauteur_visuelle_px)
          + "px; width: 60px; border-right: 2px solid #ccc; text-align: right;"
          ' padding-right: 8px;">'
      )

      for mm in paliers_mm:
        pos_depuis_bas = mm * px_par_mm
        correction_top = hauteur_visuelle_px - pos_depuis_bas - 6
        html_str += (
            '<div style="position: absolute; top: '
            + str(correction_top)
            + 'px; right: 8px; font-size: 11px; color: #555;">'
            + str(mm)
            + " mm —</div>"
        )

      html_str += "</div>"
      html_str += (
          '<div style="position: relative; width: '
          + str(largeur_visuelle_px)
          + "px; height: "
          + str(hauteur_visuelle_px)
          + "px; background-color: "
          + couleur_fond_html
          + "; border: 2px solid #111; margin-left: 20px; box-shadow: inset 0"
          ' 0 10px rgba(0,0,0,0.3); overflow: hidden;">'
      )

      # 1. Pièces de titre
      if (
          has_pieces
          and df_pieces_edite is not None
          and not df_pieces_edite.empty
      ):
        for _, row_p in df_pieces_edite.iterrows():
          pos_p_mm = row_p["Position (mm depuis le bas)"]
          haut_p_mm = row_p["Hauteur pièce (mm)"]
          c_p_nom = row_p["Couleur pièce"]
          m_p_nom = row_p["Couleur marquage"]
          txt_p = str(row_p.get("Titre sur pièce", "")).strip()

          if pd.notna(pos_p_mm) and pd.notna(haut_p_mm):
            bg_piece_html = HEX_COULEURS_TOILE.get(c_p_nom, "#8b0000")
            txt_piece_html = HEX_COULEURS_MARQUAGE.get(m_p_nom, "#ffd700")

            haut_p_px = haut_p_mm * px_par_mm
            bottom_p_px = pos_p_mm * px_par_mm
            top_p_px = hauteur_visuelle_px - bottom_p_px - haut_p_px

            if txt_p and txt_p != "None":
              lignes_p = [l.strip() for l in txt_p.split("\n") if l.strip()]
              texte_piece_html = "<br>".join(
                  ["<span>" + str(l) + "</span>" for l in lignes_p]
              )
            else:
              texte_piece_html = ""

            style_orient_p = (
                "writing-mode: vertical-rl; transform: rotate(180deg);"
                " white-space: nowrap;"
                if is_long
                else ""
            )

            html_str += (
                '<div style="position: absolute; top: '
                + str(top_p_px)
                + "px; width: 100%; height: "
                + str(haut_p_px)
                + "px; background-color: "
                + bg_piece_html
                + "; border: 1.5px dashed #fff; display: flex; align-items:"
                " center; justify-content: center; text-align: center;"
                ' overflow: hidden;">'
            )
            html_str += (
                '<div style="color: '
                + txt_piece_html
                + "; font-size: 11px; font-weight: bold; text-transform:"
                " uppercase; line-height: 1.2; padding: 0 2px; "
                + style_orient_p
                + '">'
                + texte_piece_html
                + "</div>"
            )
            html_str += "</div>"

      # 2. Lignes directes sur le dos
      for _, row_data in df_edite_lignes.iterrows():
        mm_pos = row_data["Hauteur du titre (mm)"]
        txt = str(row_data["Titrage"]).strip()

        if pd.notna(mm_pos) and txt and txt != "None" and txt != "":
          taille_estimee_texte_px = len(txt) * 8.5

          if not is_long and taille_estimee_texte_px > (
              largeur_visuelle_px - 6
          ):
            coloration_ligne = "#d9534f"
            fond_alerte = (
                "background-color: rgba(217, 83, 79, 0.2); border: 1px dashed"
                " #d9534f;"
            )
          else:
            coloration_ligne = couleur_texte_html
            fond_alerte = ""

          bottom_offset = float(mm_pos) * px_par_mm
          top_offset_px = hauteur_visuelle_px - bottom_offset - 10

          if is_long:
            # Rendu vertical de bas en haut (écriture couchée) :
            # writing-mode: vertical-rl + transform: rotate(180deg) sur un inline-block centré
            html_str += (
                '<div style="position: absolute; top: '
                + str(top_offset_px)
                + "px; left: 0; width: 100%; display: flex; justify-content:"
                ' center; align-items: center;">'
            )
            html_str += (
                '<span style="color: '
                + coloration_ligne
                + "; font-size: 13px; font-weight: bold; "
                + fond_alerte
                + " text-transform: uppercase; writing-mode: vertical-rl;"
                " transform: rotate(180deg); display: inline-block; white-space:"
                ' nowrap;">'
                + txt
                + "</span>"
            )
            html_str += "</div>"
          else:
            html_str += (
                '<div style="position: absolute; top: '
                + str(top_offset_px)
                + "px; left: 0; width: 100%; text-align: center; color: "
                + coloration_ligne
                + "; font-size: 13px; font-weight: bold; "
                + fond_alerte
                + " text-transform: uppercase; white-space: nowrap; overflow:"
                ' visible;">'
            )
            html_str += "<span>" + txt + "</span>"
            html_str += "</div>"

      html_str += "</div></div>"
      st.components.v1.html(html_str, height=hauteur_visuelle_px + 80)
