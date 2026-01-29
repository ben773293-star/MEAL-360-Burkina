import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64
from PIL import Image
from PIL.ExifTags import TAGS

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Unité MEAL 360 - Burkina", layout="wide")

# --- SYSTÈME DE SÉCURITÉ (LOGIN) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login():
    st.title("🔒 Unité MEAL - Accès Sécurisé")
    user = st.text_input("Identifiant Administrateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Ouvrir la session"):
        if user == "admin" and password == "Burkina2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Accès refusé. Vérifiez vos identifiants.")

if not st.session_state.auth:
    login()
else:
    # --- BARRE LATÉRALE (NAVIGATION) ---
    st.sidebar.title("🛠️ Menu MEAL")
    page = st.sidebar.selectbox(
        "Navigation", 
        ["Tableau de Bord", "Collecte de Données", "Audit Géographique", "Rapports PDF"]
    )
    
    if st.sidebar.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()

    # --- DONNÉES DE SIMULATION (Pour l'exemple) ---
    data = {
        'Projet': ['Forages Sahel', 'Cantines Est', 'Santé Nord', 'Éducation Centre'],
        'Localité': ['Dori', 'Fada', 'Ouahigouya', 'Ouagadougou'],
        'Bénéficiaires': [1200, 850, 2300, 1500],
        'Budget_Prévu': [50000, 30000, 75000, 40000],
        'Dépenses': [42000, 31000, 68000, 35000]
    }
    df = pd.DataFrame(data)

    # --- PAGE 1 : TABLEAU DE BORD ---
    if page == "Tableau de Bord":
        st.title("📊 Tableau de Bord des Performances")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Bénéficiaires", f"{df['Bénéficiaires'].sum():,}")
        col2.metric("Projets Actifs", len(df))
        col3.metric("Taux d'Exécution", "88%")

        fig = px.bar(df, x='Projet', y='Bénéficiaires', color='Localité', title="Impact par Projet")
        st.plotly_chart(fig, use_container_width=True)

    # --- PAGE 2 : COLLECTE DE DONNÉES ---
    elif page == "Collecte de Données":
        st.title("📝 Saisie de Rapport Terrain")
        with st.form("form_collecte"):
            projet = st.selectbox("Projet", df['Projet'])
            localite = st.text_input("Localité exacte")
            nbre = st.number_input("Nombre de bénéficiaires", min_value=0)
            photo = st.file_uploader("Preuve visuelle (Photo)", type=['jpg', 'png'])
            submit = st.form_submit_button("Enregistrer les données")
            if submit:
                st.success(f"Données enregistrées pour {projet} à {localite} !")

    # --- PAGE 3 : AUDIT GÉOGRAPHIQUE ---
    elif page == "Audit Géographique":
        st.title("🔍 Module d'Audit de Terrain")
        st.write("Vérification de l'authenticité des preuves (GPS).")
        img_file = st.file_uploader("Charger une photo de preuve", type=['jpg', 'jpeg'])
        if img_file:
            st.image(img_file, caption="Photo à analyser", width=400)
            st.info("Recherche de coordonnées GPS dans les métadonnées...")

    # --- PAGE 4 : RAPPORTS PDF ---
    elif page == "Rapports PDF":
        st.title("📑 Génération de Rapports Officiels")
        if st.button("Générer le rapport d'audit PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Rapport d'Impact MEAL - Burkina Faso", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.ln(10)
            for i, r in df.iterrows():
                pdf.cell(200, 10, txt=f"- {r['Projet']} ({r['Localité']}): {r['Bénéficiaires']} pers.", ln=True)
            
            pdf_out = pdf.output(dest='S').encode('latin-1')
            b64 = base64.b64encode(pdf_out).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Rapport_MEAL.pdf">📥 Télécharger le Rapport</a>'
            st.markdown(href, unsafe_allow_html=True)