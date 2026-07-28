# 5. Griffe du client avec alignement sur la ligne du bas (remontée vers le haut)
    if griffe_texte:
      x_center = x_dos + (w_dos_px / 2)
      chars_max_par_ligne = max(int((w_dos_px - 8) / 7), 1)

      # Découpage dynamique des mots (auto-wrap)
      mots = griffe_texte.replace("\n", " ").split()
      lignes_g = []
      ligne_courante = []

      for mot in mots:
        test_ligne = " ".join(ligne_courante + [mot])
        if len(test_ligne) <= chars_max_par_ligne:
          ligne_courante.append(mot)
        else:
          if ligne_courante:
            lignes_g.append(" ".join(ligne_courante).upper())
          ligne_courante = [mot]
      if ligne_courante:
        lignes_g.append(" ".join(ligne_courante).upper())

      # Interligne en pixels (environ 14px pour font_griffe 11pt)
      interligne_px = 14
      nb_lignes = len(lignes_g)

      # Position Y de la dernière ligne (ancrée sur la position basse spécifiée)
      y_derniere_ligne_px = y_dos + h_dos_px - (griffe_pos_mm * px_par_mm)

      # On dessine chaque ligne en remontant depuis la dernière
      for idx_ligne, txt_ligne in enumerate(lignes_g):
        # Distance par rapport à la dernière ligne (0 pour la dernière, 1*interligne pour l'avant-dernière, etc.)
        decalage_remontée = (nb_lignes - 1 - idx_ligne) * interligne_px
        y_ligne_px = y_derniere_ligne_px - decalage_remontée

        # Contrôle de débordement en largeur
        bbox_g = draw.textbbox(
            (0, 0), txt_ligne, font=font_griffe, align="center"
        )
        w_g = bbox_g[2] - bbox_g[0]
        c_griffe = "#d9534f" if w_g > (w_dos_px - 4) else c_marq_hex

        draw.text(
            (x_center, y_ligne_px),
            txt_ligne,
            fill=c_griffe,
            font=font_griffe,
            anchor="mm",
            align="center",
        )
