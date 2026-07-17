import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_FILE = "base_reliure_OK.db"
import os; os.remove("base_reliure_finale.db") if os.path.exists("base_reliure_finale.db") else None
# Grille standard de référence (extraite de votre photo) - Ordre des clés adapté en Largeur x Hauteur
TARIFS_STANDARDS = {
    "Pièce de titre": {"185 x 115 (In 12)": 5.05, "200 x 130 (In 8° écu)": 6.56, "245 x 160 (In 8° raisin)": 7.57, "270 x 175 (In 8° jésus)": 9.08, "320 x 245 (In 4° raisin)": 11.61, "350 x 270 (In 4° jésus)": 14.13, "440 x 280 (Folio carré)": 15.84, "490 x 320 (Folio raisin)": 17.76, "540 x 350 (Folio jésus)": 19.17, "600 x 440 (Grand folio)": 21.19, "Plano A": 22.96, "Plano B": 25.23},
    "Sous titre": {"185 x 115 (In 12)": 7.01, "200 x 130 (In 8° écu)": 9.11, "245 x 160 (In 8° raisin)": 10.51, "270 x 175 (In 8° jésus)": 12.62, "320 x 245 (In 4° raisin)": 16.12, "350 x 270 (In 4° jésus)": 19.63, "440 x 280 (Folio carré)": 22.01, "490 x 320 (Folio raisin)": 24.67, "540 x 350 (Folio jésus)": 26.63, "600 x 440 (Grand folio)": 29.44, "Plano A": 31.89, "Plano B": 35.05},
    "Titrage main": {"185 x 115 (In 12)": 9.83, "200 x 130 (In 8° écu)": 12.78, "245 x 160 (In 8° raisin)": 14.75, "270 x 175 (In 8° jésus)": 17.70, "320 x 245 (In 4° raisin)": 22.61, "350 x 270 (In 4° jésus)": 27.53, "440 x 280 (Folio carré)": 30.87, "490 x 320 (Folio raisin)": 34.61, "540 x 350 (Folio jésus)": 37.36, "600 x 440 (Grand folio)": 41.29, "Plano A": 44.73, "Plano B": 49.16},
    "Titre caractère latin": {"185 x 115 (In 12)": 9.83, "200 x 130 (In 8° écu)": 12.78, "245 x 160 (In 8° raisin)": 14.75, "270 x 175 (In 8° jésus)": 17.70, "320 x 245 (In 4° raisin)": 22.61, "350 x 270 (In 4° jésus)": 27.53, "440 x 280 (Folio carré)": 30.87, "490 x 320 (Folio raisin)": 34.61, "540 x 350 (Folio jésus)": 37.36, "600 x 440 (Grand folio)": 41.29, "Plano A": 44.73, "Plano B": 49.16},
    "Titre autre caractère": {"185 x 115 (In 12)": 9.83, "200 x 130 (In 8° écu)": 12.78, "245 x 160 (In 8° raisin)": 14.75, "270 x 175 (In 8° jésus)": 17.70, "320 x 245 (In 4° raisin)": 22.61, "350 x 270 (In 4° jésus)": 27.53, "440 x 280 (Folio carré)": 30.87, "490 x 320 (Folio raisin)": 34.61, "540 x 350 (Folio jésus)": 37.36, "600 x 440 (Grand folio)": 41.29, "Plano A": 44.73, "Plano B": 49.16},
    "Griffe": {"185 x 115 (In 12)": 2.24, "200 x 130 (In 8° écu)": 2.91, "245 x 160 (In 8° raisin)": 3.36, "270 x 175 (In 8° jésus)": 4.03, "320 x 245 (In 4° raisin)": 5.15, "350 x 270 (In 4° jésus)": 6.27, "440 x 280 (Folio carré)": 7.03, "490 x 320 (Folio raisin)": 7.88, "540 x 350 (Folio jésus)": 8.51, "600 x 440 (Grand folio)": 9.40, "Plano A": 10.19, "Plano B": 11.20},
    "Plats conservés": {"185 x 115 (In 12)": 12.52, "200 x 130 (In 8° écu)": 16.27, "245 x 160 (In 8° raisin)": 18.77, "270 x 175 (In 8° jésus)": 22.53, "320 x 245 (In 4° raisin)": 28.78, "350 x 270 (In 4° jésus)": 35.04, "440 x 280 (Folio carré)": 39.30, "490 x 320 (Folio raisin)": 44.05, "540 x 350 (Folio jésus)": 47.56, "600 x 440 (Grand folio)": 52.56, "Plano A": 56.94, "Plano B": 62.58},
    "Onglets": {"185 x 115 (In 12)": 0.92, "200 x 130 (In 8° écu)": 1.20, "245 x 160 (In 8° raisin)": 1.38, "270 x 175 (In 8° jésus)": 1.66, "320 x 245 (In 4° raisin)": 2.12, "350 x 270 (In 4° jésus)": 2.58, "440 x 280 (Folio carré)": 2.89, "490 x 320 (Folio raisin)": 3.24, "540 x 350 (Folio jésus)": 3.50, "600 x 440 (Grand folio)": 3.86, "Plano A": 4.19, "Plano B": 4.60},
    "Doublage japon": {"185 x 115 (In 12)": 6.81, "200 x 130 (In 8° écu)": 8.85, "245 x 160 (In 8° raisin)": 10.21, "270 x 175 (In 8° jésus)": 12.26, "320 x 245 (In 4° raisin)": 15.66, "350 x 270 (In 4° jésus)": 19.07, "440 x 280 (Folio carré)": 21.38, "490 x 320 (Folio raisin)": 23.97, "540 x 350 (Folio jésus)": 25.88, "600 x 440 (Grand folio)": 28.60, "Plano A": 30.98, "Plano B": 34.05},
    "Charnières toile": {"185 x 115 (In 12)": 1.66, "200 x 130 (In 8° écu)": 2.15, "245 x 160 (In 8° raisin)": 2.48, "270 x 175 (In 8° jésus)": 2.98, "320 x 245 (In 4° raisin)": 3.81, "350 x 270 (In 4° jésus)": 4.64, "440 x 280 (Folio carré)": 5.20, "490 x 320 (Folio raisin)": 5.83, "540 x 350 (Folio jésus)": 6.29, "600 x 440 (Grand folio)": 6.96, "Plano A": 7.54, "Plano B": 8.28},
    "Conservation de gardes": {"185 x 115 (In 12)": 12.70, "200 x 130 (In 8° écu)": 16.51, "245 x 160 (In 8° raisin)": 19.05, "270 x 175 (In 8° jésus)": 22.86, "320 x 245 (In 4° raisin)": 29.21, "350 x 270 (In 4° jésus)": 35.56, "440 x 280 (Folio carré)": 39.88, "490 x 320 (Folio raisin)": 44.70, "540 x 350 (Folio jésus)": 48.26, "600 x 440 (Grand folio)": 53.34, "Plano A": 57.78, "Plano B": 63.50},
    "Couture sur nerfs": {"185 x 115 (In 12)": 18.22, "200 x 130 (In 8° écu)": 23.69, "245 x 160 (In 8° raisin)": 27.33, "270 x 175 (In 8° jésus)": 32.80, "320 x 245 (In 4° raisin)": 41.91, "350 x 270 (In 4° jésus)": 51.02, "440 x 280 (Folio carré)": 57.21, "490 x 320 (Folio raisin)": 64.14, "540 x 350 (Folio jésus)": 69.24, "600 x 440 (Grand folio)": 76.53, "Plano A": 82.90, "Plano B": 91.10},
    "Couvrure sur nerf": {"185 x 115 (In 12)": 9.85, "200 x 130 (In 8° écu)": 12.80, "245 x 160 (In 8° raisin)": 14.77, "270 x 175 (In 8° jésus)": 17.72, "320 x 245 (In 4° raisin)": 22.65, "350 x 270 (In 4° jésus)": 27.57, "440 x 280 (Folio carré)": 30.92, "490 x 320 (Folio raisin)": 34.66, "540 x 350 (Folio jésus)": 37.42, "600 x 440 (Grand folio)": 41.36, "Plano A": 44.80, "Plano B": 49.23},
    "Filets fleurons": {"185 x 115 (In 12)": 1.66, "200 x 130 (In 8° écu)": 2.15, "245 x 160 (In 8° raisin)": 2.48, "270 x 175 (In 8° jésus)": 2.98, "320 x 245 (In 4° raisin)": 3.81, "350 x 270 (In 4° jésus)": 4.64, "440 x 280 (Folio carré)": 5.20, "490 x 320 (Folio raisin)": 5.83, "540 x 350 (Folio jésus)": 6.29, "600 x 440 (Grand folio)": 6.96, "Plano A": 7.54, "Plano B": 8.28},
    "Plaçure": {"185 x 115 (In 12)": 1.66, "200 x 130 (In 8° écu)": 2.15, "245 x 160 (In 8° raisin)": 2.48, "270 x 175 (In 8° jésus)": 2.98, "320 x 245 (In 4° raisin)": 3.81, "350 x 270 (In 4° jésus)": 4.64, "440 x 280 (Folio carré)": 5.20, "490 x 320 (Folio raisin)": 5.83, "540 x 350 (Folio jésus)": 6.29, "600 x 440 (Grand folio)": 6.96, "Plano A": 7.54, "Plano B": 8.28},
    "Sup ouvrage déjà relié": {"185 x 115 (In 12)": 12.70, "200 x 130 (In 8° écu)": 16.51, "245 x 160 (In 8° raisin)": 19.05, "270 x 175 (In 8° jésus)": 22.86, "320 x 245 (In 4° raisin)": 29.21, "350 x 270 (In 4° jésus)": 35.56, "440 x 280 (Folio carré)": 39.88, "490 x 320 (Folio raisin)": 44.70, "540 x 350 (Folio jésus)": 48.26, "600 x 440 (Grand folio)": 53.34, "Plano A": 57.78, "Plano B": 63.50},
    "Plaçure intercalaires": {"185 x 115 (In 12)": 1.12, "200 x 130 (In 8° écu)": 1.46, "245 x 160 (In 8° raisin)": 1.68, "270 x 175 (In 8° jésus)": 2.02, "320 x 245 (In 4° raisin)": 2.58, "350 x 270 (In 4° jésus)": 3.13, "440 x 280 (Folio carré)": 3.52, "490 x 320 (Folio raisin)": 3.94, "540 x 350 (Folio jésus)": 4.25, "600 x 440 (Grand folio)": 4.70, "Plano A": 5.09, "Plano B": 5.60},
    "Doublage couverture": {"185 x 115 (In 12)": 3.19, "200 x 130 (In 8° écu)": 4.15, "245 x 160 (In 8° raisin)": 4.79, "270 x 175 (In 8° jésus)": 5.74, "320 x 245 (In 4° raisin)": 7.34, "350 x 270 (In 4° jésus)": 8.93, "440 x 280 (Folio carré)": 10.02, "490 x 320 (Folio raisin)": 11.23, "540 x 350 (Folio jésus)": 12.12, "600 x 440 (Grand folio)": 13.40, "Plano A": 14.52, "Plano B": 15.95},
    "Montage de couverture": {"185 x 115 (In 12)": 2.24, "200 x 130 (In 8° écu)": 2.91, "245 x 160 (In 8° raisin)": 3.36, "270 x 175 (In 8° jésus)": 4.03, "320 x 245 (In 4° raisin)": 5.15, "350 x 270 (In 4° jésus)": 6.27, "440 x 280 (Folio carré)": 7.03, "490 x 320 (Folio raisin)": 7.88, "540 x 350 (Folio jésus)": 8.51, "600 x 440 (Grand folio)": 9.40, "Plano A": 10.19, "Plano B": 11.20},
    "Fonds de cahiers": {"185 x 115 (In 12)": 1.23, "200 x 130 (In 8° écu)": 1.60, "245 x 160 (In 8° raisin)": 1.84, "270 x 175 (In 8° jésus)": 2.21, "320 x 245 (In 4° raisin)": 2.82, "350 x 270 (In 4° jésus)": 3.44, "440 x 280 (Folio carré)": 3.85, "490 x 320 (Folio raisin)": 4.32, "540 x 350 (Folio jésus)": 4.66, "600 x 440 (Grand folio)": 5.15, "Plano A": 5.58, "Plano B": 6.13},
    "Pose antivol": {"185 x 115 (In 12)": 0.43, "200 x 130 (In 8° écu)": 0.56, "245 x 160 (In 8° raisin)": 0.64, "270 x 175 (In 8° jésus)": 0.77, "320 x 245 (In 4° raisin)": 0.99, "350 x 270 (In 4° jésus)": 1.21, "440 x 280 (Folio carré)": 1.35, "490 x 320 (Folio raisin)": 1.51, "540 x 350 (Folio jésus)": 1.63, "600 x 440 (Grand folio)": 1.80, "Plano A": 1.95, "Plano B": 2.15},
    "Désacidification": {"185 x 115 (In 12)": 0.00, "200 x 130 (In 8° écu)": 0.00, "245 x 160 (In 8° raisin)": 0.00, "270 x 175 (In 8° jésus)": 0.00, "320 x 245 (In 4° raisin)": 0.00, "350 x 270 (In 4° jésus)": 0.00, "440 x 280 (Folio carré)": 0.00, "490 x 320 (Folio raisin)": 0.00, "540 x 350 (Folio jésus)": 0.00, "600 x 440 (Grand folio)": 0.00, "Plano A": 40.71, "Plano B": 40.71},
    "Désinfection": {"185 x 115 (In 12)": 0.00, "200 x 130 (In 8° écu)": 0.00, "245 x 160 (In 8° raisin)": 0.00, "270 x 175 (In 8° jésus)": 0.00, "320 x 245 (In 4° raisin)": 0.00, "350 x 270 (In 4° jésus)": 0.00, "440 x 280 (Folio carré)": 0.00, "490 x 320 (Folio raisin)": 0.00, "540 x 350 (Folio jésus)": 0.00, "600 x 440 (Grand folio)": 0.00, "Plano A": 40.71, "Plano B": 40.71},
    "Charnière cuir": {"185 x 115 (In 12)": 0.00, "200 x 130 (In 8° écu)": 0.00, "245 x 160 (In 8° raisin)": 0.00, "270 x 175 (In 8° jésus)": 0.00, "320 x 245 (In 4° raisin)": 0.00, "350 x 270 (In 4° jésus)": 0.00, "440 x 280 (Folio carré)": 0.00, "490 x 320 (Folio raisin)": 0.00, "540 x 350 (Folio jésus)": 0.00, "600 x 440 (Grand folio)": 0.00, "Plano A": 40.71, "Plano B": 40.71},
    "Enlever agrafes": {"185 x 115 (In 12)": 0.00, "200 x 130 (In 8° écu)": 0.00, "245 x 160 (In 8° raisin)": 0.00, "270 x 175 (In 8° jésus)": 0.00, "320 x 245 (In 4° raisin)": 0.00, "350 x 270 (In 4° jésus)": 0.00, "440 x 280 (Folio carré)": 3.85, "490 x 320 (Folio raisin)": 4.32, "540 x 350 (Folio jésus)": 4.66, "600 x 440 (Grand folio)": 5.15, "Plano A": 5.58, "Plano B": 6.13},
    "Couture manuelle sur rubans": {"185 x 115 (In 12)": 0.00, "200 x 130 (In 8° écu)": 0.00, "245 x 160 (In 8° raisin)": 1.84, "270 x 175 (In 8° jésus)": 2.21, "320 x 245 (In 4° raisin)": 2.82, "350 x 270 (In 4° jésus)": 3.44, "440 x 280 (Folio carré)": 3.85, "490 x 320 (Folio raisin)": 4.32, "540 x 350 (Folio jésus)": 4.66, "600 x 440 (Grand folio)": 5.15, "Plano A": 5.58, "Plano B": 6.13}
}

FORMATS_COLONNES = ["185 x 115 (In 12)", "200 x 130 (In 8° écu)", "245 x 160 (In 8° raisin)", "270 x 175 (In 8° jésus)", "320 x 245 (In 4° raisin)", "350 x 270 (In 4° jésus)", "440 x 280 (Folio carré)", "490 x 320 (Folio raisin)", "540 x 350 (Folio jésus)", "600 x 440 (Grand folio)", "Plano A", "Plano B"]

def initialiser_bdd():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_livres (
            nom_client TEXT NOT NULL, numero_train TEXT NOT NULL, numero_livre INTEGER NOT NULL,
            nature_doc TEXT, text_doc TEXT, option_autre TEXT, repro_scanne BOOLEAN, repro_report BOOLEAN,
            hauteur INTEGER, largeur INTEGER, epaisseur INTEGER, ne_pas_rogner BOOLEAN, traitement TEXT,
            type_reliure TEXT, type_couture TEXT, agraphes BOOLEAN, nombre_cahiers INTEGER, sans_titrage BOOLEAN,
            titrage_sens TEXT, lignes_sup INTEGER, titrage_couleur TEXT, police TEXT, type_toile TEXT, couleur TEXT,
            cocher_piece_titre BOOLEAN, couleur_pieces_toile TEXT, marquage_pieces TEXT, hauteur_maquette INTEGER,
            supplement_1 TEXT, supplement_2 TEXT, supplement_3 TEXT, supplement_4 TEXT,
            PRIMARY KEY (nom_client, numero_train, numero_livre) ON CONFLICT REPLACE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            nom TEXT PRIMARY KEY, adresse TEXT, telephone TEXT, email TEXT, contact_nom TEXT, notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarifs_clients (
            nom_client TEXT NOT NULL, designation TEXT NOT NULL, format_nom TEXT NOT NULL, montant REAL NOT NULL,
            PRIMARY KEY (nom_client, designation, format_nom)
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS couleurs_toile (nom_couleur TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

def dupliquer_grille_standard_pour_client(nom_client):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM tarifs_clients WHERE nom_client = ? LIMIT 1", (nom_client,))
    if not cursor.fetchone():
        for designation, formats in TARIFS_STANDARDS.items():
            for format_nom, montant in formats.items():
                cursor.execute("""
                    INSERT INTO tarifs_clients (nom_client, designation, format_nom, montant)
                    VALUES (?, ?, ?, ?)
                """, (nom_client, designation, format_nom, montant))
        conn.commit()
    conn.close()

def recuperer_tarif_option(nom_client, designation, format_nom):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT montant FROM tarifs_clients 
        WHERE nom_client = ? AND designation = ? AND format_nom = ?
    """, (nom_client, designation, format_nom))
    result = cursor.fetchone()
    conn.close()
    if result is not None:
        return result[0]
    return TARIFS_STANDARDS.get(designation, {}).get(format_nom, 0.00)

def determiner_categorie_format(l, h):
    """Détermine la catégorie en vérifiant d'abord la Largeur (l) puis la Hauteur (h)."""
    if l <= 185 and h <= 115: return "185 x 115 (In 12)"
    elif l <= 200 and h <= 130: return "200 x 130 (In 8° écu)"
    elif l <= 245 and h <= 160: return "245 x 160 (In 8° raisin)"
    elif l <= 270 and h <= 175: return "270 x 175 (In 8° jésus)"
    elif l <= 320 and h <= 245: return "320 x 245 (In 4° raisin)"
    elif l <= 350 and h <= 270: return "350 x 270 (In 4° jésus)"
    elif l <= 440 and h <= 280: return "440 x 280 (Folio carré)"
    elif l <= 490 and h <= 320: return "490 x 320 (Folio raisin)"
    elif l <= 540 and h <= 350: return "540 x 350 (Folio jésus)"
    elif l <= 600 and h <= 440: return "600 x 440 (Grand folio)"
    elif l <= 700: return "Plano A"
    else: return "Plano B"

def lister_tous_les_clients():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM clients ORDER BY nom ASC")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients

def recuperer_fiche_client(nom_client):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE nom = ?", (nom_client,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def enregistrer_client(nom, adresse, telephone, email, contact, notes):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (nom, adresse, telephone, email, contact_nom, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(nom) DO UPDATE SET
            adresse=excluded.adresse, telephone=excluded.telephone,
            email=excluded.email, contact_nom=excluded.contact_nom, notes=excluded.notes
    """, (nom, adresse, telephone, email, contact, notes))
    conn.commit()
    conn.close()
    dupliquer_grille_standard_pour_client(nom)

def supprimer_client_bdd(nom_client):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE nom = ?", (nom_client,))
    cursor.execute("DELETE FROM fiches_livres WHERE nom_client = ?", (nom_client,))
    cursor.execute("DELETE FROM tarifs_clients WHERE nom_client = ?", (nom_client,))
    conn.commit()
    conn.close()

def lister_les_trains_du_client(client):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT numero_train FROM fiches_livres WHERE nom_client = ? ORDER BY numero_train DESC", (client,))
    trains = [row[0] for row in cursor.fetchall()]
    conn.close()
    return trains

def generer_automatiquement_numero_train(client):
    annee_courante = datetime.now().year
    prefixe_recherche = f"T{annee_courante}%"
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT numero_train FROM fiches_livres 
        WHERE nom_client = ? AND numero_train LIKE ?
        ORDER BY numero_train DESC LIMIT 1
    """, (client, prefixe_recherche))
    dernier_train = cursor.fetchone()
    conn.close()
    if dernier_train:
        str_num = dernier_train[0][5:]
        try: prochain_ordre = int(str_num) + 1
        except ValueError: prochain_ordre = 1
    else: prochain_ordre = 1
    return f"T{annee_courante}{prochain_ordre:03d}"

def determiner_prochain_numero_livre(client, train):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero_livre) FROM fiches_livres WHERE nom_client = ? AND numero_train = ?", (client, train))
    max_num = cursor.fetchone()[0]
    conn.close()
    return (max_num + 1) if max_num is not None else 1

def enregistrer_ou_mettre_a_jour_livre(donnees):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    champs = ", ".join(donnees.keys())
    placeholders = ", ".join(["?"] * len(donnees))
    valeurs = tuple(donnees.values())
    cursor.execute(f"INSERT INTO fiches_livres ({champs}) VALUES ({placeholders})", valeurs)
    conn.commit()
    conn.close()

def recuperer_livre_specifique(client, train, num_livre):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fiches_livres WHERE nom_client = ? AND numero_train = ? AND numero_livre = ?", (client, train, num_livre))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def recuperer_livres_du_train(client, train):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT numero_livre, nature_doc, text_doc, largeur, hauteur, type_reliure, couleur,
               CASE WHEN cocher_piece_titre THEN 'Oui (' || couleur_pieces_toile || ')' ELSE 'Non' END as piece_titre
        FROM fiches_livres WHERE nom_client = ? AND numero_train = ? ORDER BY numero_livre ASC
    """, (client, train))
    donnees = cursor.fetchall()
    conn.close()
    return donnees

def charger_couleurs():
    couleurs_base = ["Noir", "Rouge", "Bleu", "Vert", "Jaune", "Orange", "Violet", "Marron"]
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nom_couleur FROM couleurs_toile ORDER BY nom_couleur ASC")
    couleurs_perso = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sorted(list(set(couleurs_base + couleurs_perso)))

initialiser_bdd()

# --- CONFIGURATION INTERFACE TABS ---
st.set_page_config(page_title="Gestion Atelier Reliure", layout="wide")
tabs = st.tabs(["📚 Saisie & Suivi des Livres", "🏢 Fiches Clients", "🏷️ Grilles Tarifaires Clients"])
liste_couleurs = charger_couleurs()
liste_clients_existants = lister_tous_les_clients()

# --- TAB 3 : MANAGEMENT DE LA GRILLE DU CLIENT (ORDRE METIER CORRIGE) ---
with tabs[2]:
    st.header("🏷️ Personnalisation des tarifs par Client")
    if not liste_clients_existants:
        st.info("Créez d'abord un client pour modifier sa grille tarifaire.")
    else:
        client_tarif_sel = st.selectbox("Sélectionner un client pour ajuster ses prix :", options=liste_clients_existants, key="sb_client_tarifs")
        conn = sqlite3.connect(DB_FILE)
        df_tarifs = pd.read_sql_query("""
            SELECT designation as "Désignation", format_nom, montant 
            FROM tarifs_clients WHERE nom_client = ?
        """, conn, params=(client_tarif_sel,))
        conn.close()
        
        if not df_tarifs.empty:
            df_pivot = df_tarifs.pivot(index="Désignation", columns="format_nom", values="montant")
            df_pivot = df_pivot.reindex(columns=FORMATS_COLONNES)
            st.markdown("💡 *Modifiez directement les montants dans les cases du tableau ci-dessous, puis validez.*")
            df_edite = st.data_editor(df_pivot, use_container_width=True, num_rows="fixed")
            
            if st.button("💾 Enregistrer la nouvelle grille de " + client_tarif_sel):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                for designation, row in df_edite.iterrows():
                    for format_nom, montant in row.items():
                        cursor.execute("""
                            UPDATE tarifs_clients SET montant = ? 
                            WHERE nom_client = ? AND designation = ? AND format_nom = ?
                        """, (float(montant), client_tarif_sel, designation, format_nom))
                conn.commit()
                conn.close()
                st.success("Grille tarifaire mise à jour avec succès !")
        else:
            st.warning("Aucune donnée tarifaire trouvée.")

# --- TAB 2 : GESTION DES FICHES CLIENTS ---
with tabs[1]:
    st.header("🏢 Gestion de l'Annuaire des Clients")
    action_client = st.radio("Action :", ["Sélectionner / Modifier un client", "➕ Créer un nouveau client"], horizontal=True)
    st.write("---")
    
    if action_client == "➕ Créer un nouveau client":
        with st.form("form_creer_client"):
            nc_nom = st.text_input("Nom de l'établissement / Client *").strip()
            nc_contact = st.text_input("Nom du contact référent")
            nc_adresse = st.text_area("Adresse complète")
            nc_notes = st.text_area("Notes d'atelier spécifiques")
            if st.form_submit_button("💾 Enregistrer le nouveau client") and nc_nom:
                enregistrer_client(nc_nom, nc_adresse, "", "", nc_contact, nc_notes)
                st.success(f"Client '{nc_nom}' ajouté et grille tarifaire standard initialisée.")
                st.rerun()
    else:
        if liste_clients_existants:
            client_sel = st.selectbox("Choisir le client à gérer :", options=liste_clients_existants)
            fiche = recuperer_fiche_client(client_sel)
            if fiche:
                with st.form("form_modif_client"):
                    mod_contact = st.text_input("Nom du contact référent", value=fiche["contact_nom"])
                    mod_adresse = st.text_area("Adresse complète", value=fiche["adresse"])
                    mod_notes = st.text_area("Notes d'atelier", value=fiche["notes"])
                    if st.form_submit_button("💾 Sauvegarder les modifications"):
                        enregistrer_client(fiche["nom"], mod_adresse, "", "", mod_contact, mod_notes)
                        st.success("Fiche client mise à jour.")
                        st.rerun()
                with st.expander("🚨 Zone de danger"):
                    if st.button("❌ Supprimer définitivement") and st.checkbox(f"Confirmer la suppression de {fiche['nom']}"):
                        supprimer_client_bdd(fiche["nom"])
                        st.rerun()

# --- TAB 1 : SAISIE & SUIVI DES LIVRES ---
with tabs[0]:
    st.title("📚 Saisie de Fiche — Devis + Traitements")
    if not liste_clients_existants:
        st.warning("⚠️ Créez d'abord un client dans l'onglet 'Fiches Clients'.")
    else:
        col_saisie, col_visualisation = st.columns([1.2, 0.8])
        with col_saisie:
            st.header("📋 Saisie de la fiche")
            st.subheader("1. Clés d'enregistrement")
            nom_client_valide = st.selectbox("Client", options=liste_clients_existants, key="livre_client_selectbox")
            liste_trains_existants = lister_les_trains_du_client(nom_client_valide)
            
            c_tr1, c_tr2 = st.columns([1.2, 0.8])
            with c_tr1:
                options_train = ["-- Nouveau train automatique --"] + liste_trains_existants
                train_selectionne = st.selectbox("Sélectionner le train", options=options_train)
            numero_train = generer_automatiquement_numero_train(nom_client_valide) if train_selectionne == "-- Nouveau train automatique --" else train_selectionne
            with c_tr2: st.info(f"📂 Train : **{numero_train}**")

            num_livre_en_cours = 1
            donnees_edition = None
            if "livre_selectionne" in st.session_state and nom_client_valide and numero_train:
                num_livre_en_cours = st.session_state.livre_selectionne
                donnees_edition = recuperer_livre_specifique(nom_client_valide, numero_train, num_livre_en_cours)
                st.warning(f"🔄 Modification du Livre N° {num_livre_en_cours}")
                if st.button("❌ Annuler la modification"):
                    del st.session_state.livre_selectionne
                    st.rerun()
            elif nom_client_valide and numero_train:
                num_livre_en_cours = determiner_prochain_numero_livre(nom_client_valide, numero_train)
                st.info(f"✨ Livre suivant automatique : **{num_livre_en_cours}**")

            # --- FORMULAIRE ---
            st.write("---")
            st.subheader("2. Nature et Finition du document")
            nature_doc = st.radio("Nature :", ["Monographie (Mono)", "Périodique (Pério)"], horizontal=True, index=0 if donnees_edition and donnees_edition["nature_doc"] == "Monographie (Mono)" else (1 if donnees_edition and donnees_edition["nature_doc"] == "Périodique (Pério)" else 0))
            text_doc = st.radio("État :", ["Neuf", "Usagé"], horizontal=True, index=0 if donnees_edition and donnees_edition["text_doc"] == "Neuf" else (1 if donnees_edition and donnees_edition["text_doc"] == "Usagé" else 0))

            cocher_autre = st.checkbox("Autre (Matières spécifiques)", value=True if donnees_edition and donnees_edition["option_autre"] != "N/A" else False)
            option_autre = "N/A"
            if cocher_autre:
                idx_opt = ["Cuir", "1/2 cuir", "1/2 toile"].index(donnees_edition["option_autre"]) if donnees_edition and donnees_edition["option_autre"] in ["Cuir", "1/2 cuir", "1/2 toile"] else 0
                option_autre = st.radio("Finition :", ["Cuir", "1/2 cuir", "1/2 toile"], horizontal=True, index=idx_opt)

            st.markdown("**Reprographie :**")
            col_scanne, col_report, _ = st.columns([1, 1, 3])
            with col_scanne: repro_scanne = st.checkbox("Scannée", value=bool(donnees_edition["repro_scanne"]) if donnees_edition else False)
            with col_report: repro_report = st.checkbox("Report", value=bool(donnees_edition["repro_report"]) if donnees_edition else False)

            # --- SECTION 3 : DIMENSIONS ---
            st.write("---")
            st.subheader("3. Désignation format")
            c_dim1, c_dim2, c_dim3, c_dim4 = st.columns(4)
            with c_dim1: largeur = st.number_input("Largeur (mm)", min_value=0, value=int(donnees_edition["largeur"]) if donnees_edition else 160, step=1)
            with c_dim2: hauteur = st.number_input("Hauteur (mm)", min_value=0, value=int(donnees_edition["hauteur"]) if donnees_edition else 220, step=1)
            with c_dim3: epaisseur = st.number_input("Épaisseur (mm)", min_value=0, value=int(donnees_edition["epaisseur"]) if donnees_edition else 20, step=1)
            with c_dim4: ne_pas_rogner = st.checkbox("Ne pas rogner", value=bool(donnees_edition["ne_pas_rogner"]) if donnees_edition else False)

            format_detecte = determiner_categorie_format(largeur, hauteur)
            st.success(f"📐 **Format détecté pour la tarification** : {format_detecte}")

            # --- SECTION 4 : TRAITEMENTS ---
            st.subheader("4. Traitements & Reliure")
            c_trt1, c_trt2, c_trt3 = st.columns(3)
            list_trt = ["T1", "T2", "T3", "T4", "T5", "T6"]
            with c_trt1: traitement = st.selectbox("Traitement", list_trt, index=list_trt.index(donnees_edition["traitement"]) if donnees_edition and donnees_edition["traitement"] in list_trt else 0)
            list_rel = ["Bradel", "Emboîtage", "Passure en carton"]
            with c_trt2: type_reliure = st.selectbox("Type de reliure", list_rel, index=list_rel.index(donnees_edition["type_reliure"]) if donnees_edition and donnees_edition["type_reliure"] in list_rel else 0)
            list_cou = ["Cahiers machine", "Surjeté", "Cahier manuel"]
            with c_trt3: type_couture = st.selectbox("Type de couture", list_cou, index=list_cou.index(donnees_edition["type_couture"]) if donnees_edition and donnees_edition["type_couture"] in list_cou else 0)

            agraphes = False; nombre_cahiers = 0
            if type_couture == "Cahier manuel":
                c_cah1, c_cah2 = st.columns(2)
                with c_cah1: agraphes = st.checkbox("Présence d'agraphes", value=bool(donnees_edition["agraphes"]) if donnees_edition else False)
                with c_cah2: nombre_cahiers = st.number_input("Nombre de cahiers", min_value=0, value=int(donnees_edition["nombre_cahiers"]) if donnees_edition else 0, step=1)

            # --- SECTION 5 : TITRAGE ---
            st.write("---")
            st.subheader("5. Spécifications du titrage")
            sans_titrage = st.checkbox("**Pas de titrage**", value=bool(donnees_edition["sans_titrage"]) if donnees_edition else False)
            titrage_sens = "N/A"; lignes_sup = 0; titrage_couleur = "N/A"; police = "N/A"
            if not sans_titrage:
                c_tit1, c_tit2, c_tit3, c_tit4 = st.columns(4)
                with c_tit1: titrage_sens = st.radio("Sens", ["Long", "Travers"], horizontal=True, index=0 if donnees_edition and donnees_edition["titrage_sens"] == "Long" else (1 if donnees_edition and donnees_edition["titrage_sens"] == "Travers" else 0))
                with c_tit2: lignes_sup = st.number_input("Lignes sup", min_value=0, value=int(donnees_edition["lignes_sup"]) if donnees_edition else 0, step=1)
                list_marq = ["OR", "ARGENT", "BLANC", "NOIR"]
                with c_tit3: titrage_couleur = st.selectbox("Marquage", list_marq, index=list_marq.index(donnees_edition["titrage_couleur"]) if donnees_edition and donnees_edition["titrage_couleur"] in list_marq else 0)
                with c_tit4: police = st.radio("Police", ["Elzévir", "Baskerville"], horizontal=True, index=0 if donnees_edition and donnees_edition["police"] == "Elzévir" else (1 if donnees_edition and donnees_edition["police"] == "Baskerville" else 0))

            # --- SECTION 6 : HABILLAGE ---
            st.write("---")
            st.subheader("6. Habillage")
            c_toi1, c_toi2 = st.columns(2)
            list_toile = ["Buckram", "Fantaisie", "Autre"]
            with c_toi1: type_toile = st.selectbox("Type de toile", list_toile, index=list_toile.index(donnees_edition["type_toile"]) if donnees_edition and donnees_edition["type_toile"] in list_toile else 0)
            with c_toi2: couleur = st.selectbox("Couleur de la toile", options=liste_couleurs, index=liste_couleurs.index(donnees_edition["couleur"]) if donnees_edition and donnees_edition["couleur"] in liste_couleurs else 0)

            # --- SECTION 7 : OPTION PIÈCE DE TITRE & SUPPLÉMENTS ---
            st.write("---")
            st.subheader("7. Pièce de titre & Suppléments")
            cocher_piece_titre = st.checkbox("**Activer une pièce de titre**", value=bool(donnees_edition["cocher_piece_titre"]) if donnees_edition else False)
            couleur_pieces_toile = "N/A"; marquage_pieces = "N/A"
            valeur_maquette_defaut = int(donnees_edition["hauteur_maquette"]) if donnees_edition else (hauteur + 5)

            if cocher_piece_titre:
                c_p1, c_p2, c_p3 = st.columns(3)
                with c_p1: couleur_pieces_toile = st.selectbox("Couleur de la pièce", options=liste_couleurs, index=liste_couleurs.index(donnees_edition["couleur_pieces_toile"]) if donnees_edition and donnees_edition["couleur_pieces_toile"] in liste_couleurs else 0)
                list_mp = ["OR", "ARGENT", "BLANC", "NOIR"]
                with c_p2: marquage_pieces = st.selectbox("Marquage de la pièce", list_mp, index=list_mp.index(donnees_edition["marquage_pieces"]) if donnees_edition and donnees_edition["marquage_pieces"] in list_mp else 0)
                with c_p3: hauteur_maquette = st.number_input("Hauteur maquette (mm)", min_value=0, value=valeur_maquette_defaut, step=1)
            else: hauteur_maquette = valeur_maquette_defaut

            st.write("")
            st.markdown("**Sélection des options de suppléments :**")
            
            choix_precedents = []
            if donnees_edition:
                for col_sup in ["supplement_1", "supplement_2", "supplement_3", "supplement_4"]:
                    val = donnees_edition[col_sup]
                    if val and " - " in val:
                        nom_sup_brut = val.split(" - ")[0]
                        if nom_sup_brut in TARIFS_STANDARDS: choix_precedents.append(nom_sup_brut)

            supplements_choisis = st.multiselect(
                "Cochez les suppléments à appliquer (Maximum 4) :",
                options=list(TARIFS_STANDARDS.keys()), default=choix_precedents, max_selections=4
            )

            supplements_sauvegarde = ["", "", "", ""]
            if supplements_choisis:
                st.markdown("##### Détail des montants appliqués pour ce client :")
                for i, sup in enumerate(supplements_choisis):
                    tarif_unitaire = recuperer_tarif_option(nom_client_valide, sup, format_detecte)
                    if tarif_unitaire == 0.00:
                        if "heure" in sup or "temps" in sup: label_complet = f"{sup} - au temps passé"
                        else: label_complet = f"{sup} - sur devis"
                    else:
                        label_complet = f"{sup} - {tarif_unitaire:.2f} €"
                    supplements_sauvegarde[i] = label_complet
                    st.info(f"🔹 **{label_complet}** (Format: {format_detecte})")

            # Validation
            st.write("---")
            label_bouton = f"💾 Enregistrer les modifications du Livre N° {num_livre_en_cours}" if donnees_edition else f"💾 Valider l'enregistrement [Livre N° {num_livre_en_cours}]"
            
            if st.button(label_bouton):
                donnees_fiche = {
                    "nom_client": nom_client_valide, "numero_train": numero_train, "numero_livre": num_livre_en_cours,
                    "nature_doc": nature_doc, "text_doc": text_doc, "option_autre": option_autre,
                    "repro_scanne": repro_scanne, "repro_report": repro_report,
                    "hauteur": hauteur, "largeur": largeur, "epaisseur": epaisseur, "ne_pas_rogner": ne_pas_rogner,
                    "traitement": traitement, "type_reliure": type_reliure, "type_couture": type_couture,
                    "agraphes": agraphes, "nombre_cahiers": nombre_cahiers,
                    "sans_titrage": sans_titrage, "titrage_sens": titrage_sens, "lignes_sup": lignes_sup, 
                    "titrage_couleur": titrage_couleur, "police": police, "type_toile": type_toile, "couleur": couleur,
                    "cocher_piece_titre": cocher_piece_titre, "couleur_pieces_toile": couleur_pieces_toile, 
                    "marquage_pieces": marquage_pieces, "hauteur_maquette": hauteur_maquette,
                    "supplement_1": supplements_sauvegarde[0], "supplement_2": supplements_sauvegarde[1], 
                    "supplement_3": supplements_sauvegarde[2], "supplement_4": supplements_sauvegarde[3]
                }
                enregistrer_ou_mettre_a_jour_livre(donnees_fiche)
                st.success("Données enregistrées avec succès !")
                if "livre_selectionne" in st.session_state: del st.session_state.livre_selectionne
                st.rerun()

        # --- COLONNE DE DROITE (VISUALISATION METIER CORRIGEE) ---
        with col_visualisation:
            st.header("📊 Suivi en direct du Train")
            if nom_client_valide and numero_train:
                st.subheader(f"Client : {nom_client_valide} | Train : {numero_train}")
                livres_train = recuperer_livres_du_train(nom_client_valide, numero_train)
                if livres_train:
                    df_train = pd.DataFrame(livres_train, columns=["N° Livre", "Nature", "État", "Largeur", "Hauteur", "Reliure", "Couleur Toile", "Pièce Titre active"])
                    reponse_selection = st.dataframe(df_train, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun")
                    if reponse_selection and "rows" in reponse_selection.get("selection", {}):
                        lignes_selectionnees = reponse_selection["selection"]["rows"]
                        if lignes_selectionnees:
                            st.session_state.livre_selectionne = int(df_train.iloc[lignes_selectionnees[0]]["N° Livre"])
                            st.rerun()
                else: st.info("Aucun livre dans ce Train.")
