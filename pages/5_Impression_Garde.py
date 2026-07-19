import streamlit as st
from supabase import create_client
from datetime import datetime
import io

# Remplacement des imports ReportLab pour éviter l'ImportError
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


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

def generer_pdf_fiches(liste_fiches, date_str):
    """Génère un fichier PDF A4 en mémoire avec sauts de page"""
    tampon = io.BytesIO()
    # Utilisation de A4 (majuscules) ici
    doc = SimpleDocTemplate(
        tampon, 
        pagesize=A4,
        rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    # Définition des styles personnalisés
    style_titre = ParagraphStyle(
        'TitreFiche',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1, # Centré
        spaceAfter=20,
        underline=True
    )
    style_section = ParagraphStyle(
        'SectionFiche',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#222222')
    )
    style_texte = ParagraphStyle(
        'TexteFiche',
        parent=styles['Normal'],
        fontSize=11,
        leading=15
    )
    
    elements = []
    
    for idx, data in enumerate(liste_fiches):
        rogner_str = "OUI" if data.get('ne_pas_rogner') else "NON"
        scanne_str = "OUI" if data.get('repro_scanne') else "NON"
        report_str = "OUI" if data.get('repro_report') else "NON"
        titrage_toile_str = "SANS TITRAGE" if data.get('sans_titrage') else f"{data.get('titrage_couleur')} ({data.get('titrage_sens')})"
        
        # En-tête de la fiche
        elements.append(Paragraph("<b>- Informations sur la page de garde -</b>", style_titre))
        elements.append(Spacer(1, 10))
        
        # Tableau En-tête général
        donnees_entete = [
            [Paragraph(f"<b>Client :</b> {data.get('nom_client')}", style_texte), Paragraph(f"<b>Date :</b> {date_str}", style_texte)],
            [Paragraph(f"<b>N° du Train :</b> {data.get('numero_train')}", style_texte), ""],
            [Paragraph(f"<b>N° du Livre :</b> {data.get('numero_livre')}", style_texte), ""]
        ]
        t_entete = Table(donnees_entete, colWidths=[250, 250])
        t_entete.setStyle(TableStyle([
            ('SPAN', (1, 0), (1, 2)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 2), 'RIGHT')
        ]))
        elements.append(t_entete)
        elements.append(Spacer(1, 15))
        
        # Dimensions
        elements.append(Paragraph("📐 Dimensions & Format", style_section))
        donnees_dim = [
            [Paragraph(f"<b>Hauteur :</b> {data.get('hauteur')} mm", style_texte), Paragraph(f"<b>Hauteur Maquette :</b> {data.get('hauteur_maquette')} mm", style_texte)],
            [Paragraph(f"<b>Largeur :</b> {data.get('largeur')} mm", style_texte), Paragraph(f"<b>Ne pas Rogner :</b> {rogner_str}", style_texte)],
            [Paragraph(f"<b>Épaisseur :</b> {data.get('epaisseur')} mm", style_texte), ""]
        ]
        t_dim = Table(donnees_dim, colWidths=[250, 250])
        t_dim.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        elements.append(t_dim)
        
        # Traitement & Technique
        elements.append(Paragraph("🛠️ Traitement & Technique", style_section))
        txt_couture = f"<b>Type de couture :</b> {data.get('type_couture')}"
        if data.get('type_couture') == "Cahier manuel":
            txt_couture += f"<br/><b>Nombre de cahiers :</b> {data.get('nombre_cahiers')}<br/><b>Agraphes :</b> {'Oui' if data.get('agraphes') else 'Non'}"
            
        donnees_tech = [
            [Paragraph(f"<b>Traitement :</b> {data.get('traitement')}", style_texte), Paragraph(f"<b>Scannée :</b> {scanne_str}", style_texte)],
            [Paragraph(f"<b>Type de reliure :</b> {data.get('type_reliure')}", style_texte), Paragraph(f"<b>Repat (Report) :</b> {report_str}", style_texte)],
            [Paragraph(txt_couture, style_texte), ""]
        ]
        t_tech = Table(donnees_tech, colWidths=[250, 250])
        t_tech.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ccc')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        elements.append(t_tech)
        
        # Matériaux & Finitions
        elements.append(Paragraph("🎨 Matériaux & Finitions", style_section))
        txt_piece = "<b>Pièce de Titre :</b> NON"
        if data.get('cocher_piece_titre'):
            txt_piece = f"<b>Pièce de Titre :</b> OUI | <b>Couleur :</b> {data.get('couleur_pieces_toile')} | <b>Titrage :</b> {data.get('marquage_pieces')}"
            
        donnees_mat = [
            [Paragraph(f"<b>Type de Toile :</b> {data.get('type_toile')} | <b>Couleur :</b> {data.get('couleur')} | <b>Titrage :</b> {titrage_toile_str}", style_texte)],
            [Paragraph(txt_piece, style_texte)]
        ]
        t_mat = Table(donnees_mat, colWidths=[500])
        t_mat.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ccc')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
            ('PADDING', (0, 0), (-1, -1), 10)
        ]))
        elements.append(t_mat)
        
        # Options & Suppléments
        elements.append(Paragraph("📌 Options & Suppléments", style_section))
        sups = [data.get(f'supplement_{i}') for i in range(1, 5) if data.get(f'supplement_{i}')]
        txt_sups = "<br/>".join([f"• {s}" for s in sups]) if sups else "Aucun supplément"
        
        t_sups = Table([[Paragraph(txt_sups, style_texte)]], colWidths=[500])
        t_sups.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ccc')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
            ('PADDING', (0, 0), (-1, -1), 10)
        ]))
        elements.append(t_sups)
        
        # Insertion du saut de page matériel pour le PDF (sauf sur le dernier élément)
        if idx < len(liste_fiches) - 1:
            elements.append(PageBreak())
            
    doc.build(elements)
    tampon.seek(0)
    return tampon.getvalue()

# Configuration de la page Streamlit
st.set_page_config(page_title="Impression Garde", layout="centered")

st.title("🖨️ Génération — Impression Garde (A4 PDF)")

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
            options_livres = ["-- Choisir --", "🖨️ [TOUT LE TRAIN ENTIER]"] + [str(n) for n in liste_livres]
            with c3:
                livre_sel = st.selectbox("Sélection du volume", options=options_livres)

st.write("---")

# --- Rendu et téléchargement ---
if client_sel != "-- Choisir --" and train_sel != "-- Choisir --" and 'livre_sel' in locals() and livre_sel != "-- Choisir --":
    
    date_commune = datetime.now().strftime("%d/%m/%Y")
    fiches_a_traiter = []
    
    if livre_sel == "🖨️ [TOUT LE TRAIN ENTIER]":
        fiches_a_traiter = recuperer_tous_les_livres_du_train(client_sel, train_sel)
        nom_fichier_pdf = f"Garde_Train_{train_sel}.pdf"
    else:
        fiche_unique = recuperer_livre_complet(client_sel, train_sel, int(livre_sel))
        if fiche_unique:
            fiches_a_traiter = [fiche_unique]
        nom_fichier_pdf = f"Garde_{client_sel}_Livre_{livre_sel}.pdf"
        
    if fiches_a_traiter:
        # Génération du fichier binaire PDF via ReportLab
        donnees_pdf = generer_pdf_fiches(fiches_a_traiter, date_commune)
        
        # Bouton natif de téléchargement du PDF A4
        st.download_button(
            label="📥 Télécharger l'état d'impression en PDF (Format A4)",
            data=donnees_pdf,
            file_name=nom_fichier_pdf,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
        st.success(f"✅ Le document PDF A4 contenant {len(fiches_a_traiter)} fiche(s) avec sauts de page est prêt.")
    else:
        st.warning("Aucune donnée disponible pour la sélection demandée.")
