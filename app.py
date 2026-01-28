import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(page_title="Système MEAL 360 Intégral", page_icon="🌍", layout="wide")

# Création automatique des dossiers nécessaires
for folder in ["preuves_terrain"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Initialisation de la sécurité
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- 1. FONCTION DE SÉCURITÉ ---
def login():
    st.title("🔐 Unité MEAL - Accès Sécurisé")
    col1, col2 = st.columns(2)
    user = col1.text_input("Identifiant Administrateur")
    password = col2.text_input("Mot de passe", type="password")
    if st.button("Ouvrir la session"):
        if user == "admin" and password == "Burkina2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Accès refusé. Vérifiez vos identifiants.")

# --- VÉRIFICATION D'ACCÈS ---
if not st.session_state['auth']:
    login()
else:
    # --- NAVIGATION LATÉRALE ---
    st.sidebar.title("🌍 MEAL Expert v3.0")
    st.sidebar.success("Connecté : Admin")
    page = st.sidebar.radio("Navigation", [
        "📊 Dashboard de Performance", 
        "📍 Saisie Terrain & Preuves",
        "📂 Bibliothèque d'Audit",
        "🎯 Configuration des Objectifs",
        "💰 Analyse Financière",
        "👂 Redevabilité & Feedback",
        "📚 Capitalisation (Apprentissage)"
    ])

    if st.sidebar.button("Déconnexion"):
        st.session_state['auth'] = False
        st.rerun()

    # Fonction utilitaire pour sauvegarder en CSV
    def sauvegarder_donnees(df_n, fichier):
        df_n.to_csv(fichier, mode='a', index=False, header=not os.path.isfile(fichier))

    # --- 2. DASHBOARD DE PERFORMANCE (Global & Carto) ---
    if page == "📊 Dashboard de Performance":
        st.title("📈 Suivi de Performance Mondiale")
        
        if os.path.isfile("donnees_meal_expert.csv"):
            df = pd.read_csv("donnees_meal_expert.csv")
            
            # Filtres
            st.sidebar.divider()
            f_pays = st.sidebar.multiselect("Filtrer Pays", df["Pays"].unique(), default=df["Pays"].unique())
            df_f = df[df["Pays"].isin(f_pays)]

            # Indicateurs Clés (KPIs)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Bénéficiaires", f"{int(df_f['Bénéficiaires'].sum()):,}")
            c2.metric("Zones d'intervention", len(df_f['Localité'].unique()))
            c3.metric("Preuves d'Audit", len(df_f[df_f['Preuve'] != "Aucun"]))
            c4.metric("Dépenses ($)", f"{int(df_f['Depense'].sum()):,}")

            # Performance Cibles (Progression)
            if os.path.isfile("cibles_projets.csv"):
                st.subheader("🏁 Taux d'atteinte des Objectifs")
                df_cibles = pd.read_csv("cibles_projets.csv")
                df_perf = df_f.groupby("Projet")["Bénéficiaires"].sum().reset_index()
                df_perf = pd.merge(df_perf, df_cibles, on="Projet", how="left")
                
                for _, row in df_perf.iterrows():
                    cible = row['Cible'] if row['Cible'] > 0 else 1
                    taux = (row['Bénéficiaires'] / cible)
                    st.write(f"**{row['Projet']}**")
                    st.progress(min(float(taux), 1.0), text=f"{int(row['Bénéficiaires'])} atteints sur {int(row['Cible'])} ({taux*100:.1f}%)")
            
            # Cartographie
            st.divider()
            st.subheader("🗺️ Cartographie Globale")
            fig_map = px.scatter_geo(df_f, locations="Pays", locationmode='country names', size="Bénéficiaires", color="Projet", projection="natural earth")
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("👋 Aucune donnée. Commencez par enregistrer une activité.")

    # --- 3. SAISIE TERRAIN & PREUVES ---
    elif page == "📍 Saisie Terrain & Preuves":
        st.title("📍 Collecte de Données & Pièces Jointes")
        with st.form("form_expert", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_pays = col1.text_input("Pays (ex: Burkina Faso)")
            p_loc = col1.text_input("Localité (ex: Ouahigouya)")
            p_proj = col2.selectbox("Projet", ["Agroécologie", "Santé", "Eau & Hygiène", "Éducation"])
            p_ben = col2.number_input("Nombre de bénéficiaires", min_value=1)
            
            st.divider()
            st.subheader("💰 Données Financières")
            p_bud = col1.number_input("Budget alloué ($)", min_value=0.0)
            p_dep = col2.number_input("Dépense réelle ($)", min_value=0.0)
            
            st.divider()
            st.subheader("📸 Preuve de Vérification (Audit)")
            p_file = st.file_uploader("Joindre Photo ou PDF (Liste de présence, rapport...)", type=['pdf', 'png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("Enregistrer l'Activité"):
                if p_pays and p_loc:
                    f_name = "Aucun"
                    if p_file:
                        f_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{p_file.name}".replace(" ","_")
                        with open(os.path.join("preuves_terrain", f_name), "wb") as f:
                            f.write(p_file.getbuffer())
                    
                    df_new = pd.DataFrame({
                        "Pays":[p_pays], "Localité":[p_loc], "Projet":[p_proj],
                        "Bénéficiaires":[p_ben], "Budget":[p_bud], "Depense":[p_dep],
                        "Preuve":[f_name], "Date":[datetime.now().strftime("%Y-%m-%d")]
                    })
                    sauvegarder_donnees(df_new, "donnees_meal_expert.csv")
                    st.success("✅ Activité enregistrée avec preuve d'audit !")
                else:
                    st.error("Le pays et la localité sont obligatoires.")

    # --- 4. BIBLIOTHÈQUE D'AUDIT ---
    elif page == "📂 Bibliothèque d'Audit":
        st.title("📂 Justificatifs de Terrain")
        if os.path.isfile("donnees_meal_expert.csv"):
            df = pd.read_csv("donnees_meal_expert.csv")
            for i, row in df.iterrows():
                with st.expander(f"📄 {row['Date']} - {row['Localité']} ({row['Projet']})"):
                    st.write(f"**Bénéficiaires :** {row['Bénéficiaires']} | **Dépense :** {row['Depense']}$")
                    if row['Preuve'] != "Aucun":
                        chemin = os.path.join("preuves_terrain", row['Preuve'])
                        with open(chemin, "rb") as f:
                            st.download_button(f"📥 Télécharger la preuve", data=f, file_name=row['Preuve'], key=f"btn_{i}")
                    else:
                        st.info("Aucune preuve jointe.")

    # --- 5. CONFIGURATION DES OBJECTIFS ---
    elif page == "🎯 Configuration des Objectifs":
        st.title("🎯 Définition des Cibles")
        with st.form("f_cibles"):
            c_p = st.selectbox("Projet", ["Agroécologie", "Santé", "Eau & Hygiène", "Éducation"])
            c_v = st.number_input("Nombre de bénéficiaires visés", min_value=1)
            if st.form_submit_button("Fixer l'Objectif"):
                df_c = pd.DataFrame({"Projet":[c_p], "Cible":[c_v]})
                if os.path.isfile("cibles_projets.csv"):
                    old = pd.read_csv("cibles_projets.csv")
                    df_c = pd.concat([old[old["Projet"] != c_p], df_c])
                df_c.to_csv("cibles_projets.csv", index=False)
                st.success("Objectif enregistré !")

    # --- 6. ANALYSE FINANCIÈRE ---
    elif page == "💰 Analyse Financière":
        st.title("💰 Analyse de l'Efficience Budgétaire")
        if os.path.isfile("donnees_meal_expert.csv"):
            df = pd.read_csv("donnees_meal_expert.csv")
            t_b, t_d = df["Budget"].sum(), df["Depense"].sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Budget Global", f"{t_b:,} $")
            c2.metric("Total Dépenses", f"{t_d:,} $")
            c3.metric("Taux de Consommation", f"{(t_d/t_b*100 if t_b>0 else 0):.1f}%")
            
            fig = px.bar(df.groupby("Projet")[["Budget", "Depense"]].sum().reset_index(), x="Projet", y=["Budget", "Depense"], barmode="group", title="Budget vs Réalisé par Projet")
            st.plotly_chart(fig, use_container_width=True)

    # --- 7. REDEVABILITÉ ---
    elif page == "👂 Redevabilité & Feedback":
        st.title("👂 Gestion des Plaintes et Feedbacks")
        with st.form("f_feedback"):
            obj = st.text_input("Objet du feedback")
            nature = st.selectbox("Nature", ["Félicitation", "Plainte", "Suggestion"])
            if st.form_submit_button("Enregistrer"):
                sauvegarder_donnees(pd.DataFrame({"Sujet":[obj], "Nature":[nature], "Date":[datetime.now().strftime("%Y-%m-%d")]}), "redevabilite.csv")
                st.success("Feedback stocké.")

    # --- 8. APPRENTISSAGE ---
    elif page == "📚 Capitalisation (Apprentissage)":
        st.title("📚 Leçons Apprises & Recommandations")
        with st.form("f_learn"):
            lecon = st.text_area("Leçon apprise")
            recom = st.text_area("Recommandation future")
            if st.form_submit_button("Capitaliser"):
                sauvegarder_donnees(pd.DataFrame({"Leçon":[lecon], "Recom":[recom], "Date":[datetime.now().strftime("%Y-%m-%d")]}), "apprentissage.csv")
                st.success("Savoir sauvegardé.")