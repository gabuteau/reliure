import streamlit as st
from supabase import create_client
from datetime import datetime
import base64
import os
import io

# Imports ReportLab sécurisés
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
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

def encoder_image_base64(chemin_image):
    if os.path.exists(chemin_image):
        with open(chemin_image, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

def generer_pdf_fiches(liste_fiches, date_str):
    """Génère un fichier PDF A4 en mémoire avec sauts de page et logo à gauche"""
    tampon = io.BytesIO()
    doc = SimpleDocTemplate(
        tampon, 
        pagesize=A4,
        rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42
    )
    
    styles = getSampleStyleSheet()
    
    style_titre = ParagraphStyle(
        'TitreFiche',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1, 
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
    chemin_logo = "logo_reliure.jpg"
    
    for idx, data in enumerate(liste_fiches):
        rogner_str = "OUI" if data.get('ne_pas_rogner') else "NON"
        scanne_str = "OUI" if data.get('repro_scanne') else "NON"
        report_str = "OUI" if data.get('repro_report') else "NON"
        titrage_toile_str = "SANS TITRAGE" if data.get('sans_titrage') else f"{data.get('titrage_couleur')} ({data.get('titrage_sens')})"
        
        # Structure En-tête (Logo à gauche, Date à droite)[span_1](start_span)[span_1](end_span)
        elements_entete_gauche = []
        if os.path.exists(chemin_logo):
            img_logo = Image(chemin_logo, width=95, height=45)
            img_logo.hAlign = 'LEFT'
            elements_entete_gauche.append(img_logo)
            elements_entete_gauche.append(Spacer(1, 10))
        
        elements_entete_gauche.append(Paragraph(f"<b>Client :</b> {data.get('nom_client')}", style_texte))
        elements_entete_gauche.append(Paragraph(f"<b>N° du Train :</b> {data.get('numero_train')}", style_texte))
        elements_entete_gauche.append(Paragraph(f"<b>N° du Livre :</b> {data.get('numero_livre')}", style_texte))
        
        donnees_entete = [
            [elements_entete_gauche, Paragraph(f"<b>Date :</b> {date_str}", style_texte)]
        ]
        
        t_entete = Table(donnees_entete, colWidths=[350, 150])
        t_entete.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT')
        ]))
        
        elements.append(Paragraph("<b>- Informations sur la page de garde -</b>", style_titre))
        elements.append(Spacer(1, 15))
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
        
        # Technique
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
        
        # Finitions
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
        
        # Suppléments
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
        
        if idx < len(liste_fiches) - 1:
            elements.append(PageBreak())
            
    doc.build(elements)
    tampon.seek(0)
    return tampon.getvalue()

# Configuration Streamlit
st.set_page_config(page_title="Impression Garde", layout="centered")

# CSS pour l'affichage écran
st.html("""
    <style>
    .print-container {
        border: 1px solid #333;
        padding: 30px;
        font-family: Arial, sans-serif;
        background-color: #fff;
        color: #000;
        border-radius: 8px;
        margin-top: 20px;
        margin-bottom: 30px;
        position: relative;
    }
    .logo-header {
        position: absolute;
        top: 25px;
        left: 30px;
        max-height: 55px;
        width: auto;
    }
    .print-box {
        border: 1px solid #ccc;
        padding: 15px;
        border-radius: 5px;
        background-color: #fafafa;
        margin-bottom: 20px;
    }
    .print-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .print-col {
        flex: 1;
        margin-right: 20px;
    }
    .print-col:last-child {
        margin-right: 0;
    }
    .field-label { font-weight: bold; color: #444; }
    .field-value { font-size: 1.1em; font-weight: bold; color: #000; }
    </style>
""")

st.title("🖨️ Génération — Impression Garde")

chemin_logo = "logo_reliure.jpg"
logo_b64 = encoder_image_base64(chemin_logo)
balise_logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" class="logo-header">' if logo_b64 else ''

# Sélection
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

def generer_bloc_html_fiche(data, date_str, logo_html):
    rogner_str = "OUI" if data.get('ne_pas_rogner') else "NON"
    scanne_str = "OUI" if data.get('repro_scanne') else "NON"
    report_str = "OUI" if data.get('repro_report') else "NON"
    titrage_toile_str = "SANS TITRAGE" if data.get('sans_titrage') else f"{data.get('titrage_couleur')} ({data.get('titrage_sens')})"
    
    if data.get('cocher_piece_titre'):
        html_piece_titre = f"""
        <div style='margin-top: 10px;'>
            <span class='field-label'>Pièce de Titre :</span> <span class='field-value'>OUI</span> | 
            <span class='field-label'>Couleur :</span> <span class='field-value'>{data.get('couleur_pieces_toile')}</span> | 
            <span class='field-label'>Titrage :</span> <span class='field-value'>{data.get('marquage_pieces')}</span>
        </div>
        """
    else:
        html_piece_titre = "<div><span class='field-label'>Pièce de Titre :</span> <span class='field-value'>NON</span></div>"
        
    html_couture_details = ""
    if data.get('type_couture') == "Cahier manuel":
        html_couture_details = f"""
        <br>
        <span class='field-label'>Nombre de cahiers :</span> <span class='field-value'>{data.get('nombre_cahiers')}</span><br>
        <span class='field-label'>Agraphes :</span> <span class='field-value'>{'Oui' if data.get('agraphes') else 'Non'}</span>
        """

    sups = [data.get(f'supplement_{i}') for i in range(1, 5) if data.get(f'supplement_{i}')]
    html_sups = "".join([f"<li><span class='field-value'>{s}</span></li>" for s in sups]) if sups else "<div><span class='field-value'>Aucun supplément</span></div>"

    return f"""
    <div class="print-container">
        {logo_html}
        <h2 style="text-align: center; text-decoration: underline; margin-top: 50px; margin-bottom: 30px;">- Informations sur la page de garde -</h2>
        <div class="print-row">
            <div class="print-col" style="margin-left: 10px;">
                <span class="field-label">Client :</span> <span class="field-value">{data.get('nom_client')}</span><br>
                <span class="field-label">N° du Train :</span> <span class="field-value">{data.get('numero_train')}</span><br>
                <span class="field-label">N° du Livre :</span> <span class="field-value">{data.get('numero_livre')}</span>
            </div>
            <div class="print-col" style="text-align: right;">
                <span class="field-label">Date :</span> <span class="field-value">{date_str}</span>
            </div>
        </div>
        <br>
        <h3>📐 Dimensions & Format</h3>
        <div class="print-box">
            <div class="print-row">
                <div class="print-col">
                    <span class="field-label">Hauteur :</span> <span class="field-value">{data.get('hauteur')} mm</span><br>
                    <span class="field-label">Largeur :</span> <span class="field-value">{data.get('largeur')} mm</span><br>
                    <span class="field-label">Épaisseur :</span> <span class="field-value">{data.get('epaisseur')} mm</span>
                </div>
                <div class="print-col">
                    <span class="field-label">Hauteur Maquette :</span> <span class="field-value">{data.get('hauteur_maquette')} mm</span><br>
                    <span class="field-label">Ne pas Rogner :</span> <span class="field-value">{rogner_str}</span>
                </div>
            </div>
        </div>
        <h3>🛠️ Traitement & Technique</h3>
        <div class="print-box">
            <div class="print-row">
                <div class="print-col">
                    <span class="field-label">Traitement :</span> <span class="field-value">{data.get('traitement')}</span><br>
                    <span class="field-label">Type de reliure :</span> <span class="field-value">{data.get('type_reliure')}</span><br>
                    <span class="field-label">Type de couture :</span> <span class="field-value">{data.get('type_couture')}</span>
                    {html_couture_details}
                </div>
                <div class="print-col">
                    <span class="field-label">Scannée :</span> <span class="field-value">{scanne_str}</span><br>
                    <span class="field-label">Repat (Report) :</span> <span class="field-value">{report_str}</span>
                </div>
            </div>
        </div>
        <h3>🎨 Matériaux & Finitions</h3>
        <div class="print-box">
            <div style="margin-bottom: 10px;">
                <span class="field-label">Type de Toile :</span> <span class="field-value">{data.get('type_toile')}</span> | 
                <span class="field-label">Couleur :</span> <span class="field-value">{data.get('couleur')}</span> | 
                <span class="field-label">Titrage :</span> <span class="field-value">{titrage_toile_str}</span>
            </div>
            {html_piece_titre}
        </div>
        <h3>📌 Options & Suppléments</h3>
        <div class="print-box"><ul style="margin: 0; padding-left: 20px;">{html_sups}</ul></div>
    </div>
    """

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
        donnees_pdf = generer_pdf_fiches(fiches_a_traiter, date_commune)
        
        st.download_button(
            label="📥 Télécharger l'état d'impression en PDF (Format A4)",
            data=donnees_pdf,
            file_name=nom_fichier_pdf,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
        # Aperçu visuel à l'écran
        html_aperçu = ""
        for idx, fiche in enumerate(fiches_a_traiter):
            html_aperçu += generer_bloc_html_fiche(fiche, date_commune, balise_logo_html)
            if idx < len(fiches_a_traiter) - 1:
                html_aperçu += '<hr style="border: 1px dashed #999; margin: 40px 0;">'
        st.html(html_aperçu)
