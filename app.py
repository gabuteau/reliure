import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Saisie Fiche de Fabrication", layout="wide")

st.title("📚 Système de Saisie & Devis — Reliure")
st.write("Saisissez les caractéristiques du livre pour générer la fiche de fabrication et le devis.")

# --- BASE DE DONNÉES DE TARIFS SIMPLIFIÉE ---
# (Exemple basé sur votre grille pour les livres neufs)
def calculer_tarif(hauteur_livre, type_couture, titrage_machine):
    # Détermination de la catégorie de hauteur
    if hauteur_livre <= 245:
        base_prix = 30.00  # Tarif de base indicatif pour petit format
    elif hauteur_livre <= 315:
        base_prix = 38.00  # Tarif moyen
    else:
        base_prix = 48.00  # Grand format
    
    # Ajustement selon le type de couture
    if type_couture == "Cahiers machine (cousus)":
        base_prix += 3.92  # Ajustement exemple pour arriver à vos 33,92 €
    else:
        base_prix += 0.00 # Dos collé par exemple
        
    # Option titrage
    if titrage_machine:
        base_prix += 0.00  # Déjà inclus ou option selon votre grille
        
    return round(base_prix, 2)

# --- MISE EN PAGE : DEUX COLONNES ---
col_saisie, col_resultat = st.columns([1, 1])

with col_saisie:
    st.header("📋 Fiche de Fabrication")
    
    # 1. État du livre
    etat_livre = st.radio("État du livre", ["Neuf", "Ancien / Restauration"], index=0)
    
    # 2. Type de reliure / Spécification
    type_reliure = st.selectbox(
        "Type de reliure", 
        ["Toile entière", "Demi-toile", "Cuir", "Demi-cuir", "Autre"]
    )
    
    # 3. Traitements
    traitement = st.radio("Traitement de structure", ["T1", "T2", "T3"], index=0)
    
    # 4. Couture
    type_couture = st.radio(
        "Type de couture (Cahiers)", 
        ["Cahiers machine (cousus)", "Cahiers surjetés", "Bloc collé"]
    )
    
    # 5. Dimensions
    hauteur_livre = st.number_input("Hauteur réelle du livre (en mm)", min_value=100, max_value=500, value=220, step=5)
    hauteur_maquette = hauteur_livre + 5
    st.caption(f"📏 Hauteur de la maquette calculée : {hauteur_maquette} mm")
    
    # 6. Titrage & Options
    st.subheader("Options")
    titrage_direct = st.checkbox("Titrage machine System 3 direct sur toile ou pièce", value=True)
    
    # 7. Quantité pour le lot
    quantite = st.number_input("Nombre d'exemplaires (Train)", min_value=1, value=150, step=1)

with col_resultat:
    st.header("💰 Devis & Récapitulatif")
    
    # Calculs
    prix_unitaire = calculer_tarif(hauteur_livre, type_couture, titrage_direct)
    total_ht = prix_unitaire * quantite
    total_ttc = total_ht * 1.20 # Exemple avec TVA à 20%
    
    # Affichage du récapitulatif sous forme de carte / reçu épuré
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; color: #212529;">
        <h3 style="margin-top: 0; color: #0f4c81;">Résumé de la commande</h3>
        <p><strong>Type de document :</strong> {etat_livre} ({type_reliure})</p>
        <p><strong>Traitement :</strong> {traitement} — <strong>Couture :</strong> {type_couture}</p>
        <p><strong>Format du livre :</strong> {hauteur_livre} mm (Maquette : {hauteur_maquette} mm)</p>
        <hr style="border-top: 1px solid #ccc;">
        <p style="font-size: 18px;"><strong>Tarif Unitaire :</strong> <span style="color: #2b8a3e; font-weight: bold;">{prix_unitaire:.2f} € HT</span></p>
        <p style="font-size: 18px;"><strong>Quantité :</strong> {quantite} ex.</p>
        <hr style="border-top: 1px dashed #ccc;">
        <h2 style="margin: 10px 0 0 0; color: #0f4c81;">Total HT : {total_ht:,.2f} €</h2>
        <p style="font-size: 14px; color: #6c757d;">Total TTC (TVA 20%) : {total_ttc:,.2f} €</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton pour simuler un enregistrement
    if st.button("💾 Enregistrer la fiche et générer le PDF", type="primary"):
        st.success(f"Fiche de fabrication enregistrée avec succès ! (Simulée)")