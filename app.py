"""
Dashboard des résultats des élections municipales 2026
Usage : streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import hmac

# --- Config ---
st.set_page_config(
    page_title="Municipales 2026 — Résultats",
    page_icon="https://www.gouvernement.fr/sites/default/files/favicon/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Auth (optionnel, activé si password dans st.secrets) ---
def check_password():
    """Vérifie le mot de passe si configuré dans .streamlit/secrets.toml"""
    try:
        has_secrets = "password" in st.secrets
    except Exception:
        return True  # Pas de fichier secrets = accès libre
    if not has_secrets:
        return True

    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("Municipales 2026")
    st.text_input("Mot de passe", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Mot de passe incorrect")
    return False


if not check_password():
    st.stop()

# --- Style DSFR (Design System de l'État) ---
st.markdown("""
<style>
    /* ============================================================
       DSFR — Design System de l'État français
       Palette : bleu #000091, fond blanc, texte #161616
    ============================================================ */

    /* ---- En-tête République française ---- */
    .rf-header {
        border-bottom: 3px solid #000091;
        padding: 1.25rem 0 1rem 0;
        margin-bottom: 2rem;
    }
    .rf-header h1 {
        color: #000091;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .rf-header .rf-subtitle {
        color: #555;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    .rf-marianne {
        font-size: 0.8rem;
        color: #000091;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }

    /* ---- KPI cards style DSFR ---- */
    /* 1. Labels des KPI : plus lisibles, pas de coupure */
    [data-testid="stMetric"] {
        background: #F5F5FE;
        border: 1px solid #D4D4F7;
        border-left: 4px solid #000091;
        padding: 1.1rem 1rem;
        border-radius: 4px;
        min-width: 0;
    }
    [data-testid="stMetricLabel"] > div {
        color: #444444 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: none !important;
        letter-spacing: 0.01em;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        line-height: 1.3 !important;
    }
    [data-testid="stMetricValue"] {
        color: #000091 !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
        line-height: 1.1 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
    }

    /* ---- Sidebar élégante style RF ---- */
    [data-testid="stSidebar"] {
        background: #F5F5FE;
        border-right: 2px solid #D4D4F7;
    }
    /* Titre sidebar */
    [data-testid="stSidebar"] h1 {
        color: #000091 !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        margin-top: 0.5rem !important;
    }
    /* Logo RF sidebar */
    .rf-logo-sidebar {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 0 0.75rem 0;
        border-bottom: 2px solid #000091;
        margin-bottom: 0.75rem;
    }
    .rf-logo-sidebar .rf-badge {
        background: #000091;
        color: #FFFFFF;
        font-size: 0.85rem;
        font-weight: 900;
        letter-spacing: 0.05em;
        padding: 0.25rem 0.5rem;
        border-radius: 2px;
        line-height: 1;
        font-family: Georgia, serif;
        flex-shrink: 0;
    }
    .rf-logo-sidebar .rf-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #000091;
        font-weight: 700;
        line-height: 1.2;
    }

    /* ---- Tabs style ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #D4D4F7;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        padding: 0.75rem 1.5rem;
        color: #555;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #000091 !important;
        color: #000091 !important;
        font-weight: 700;
    }

    /* ---- Titres ---- */
    h1, h2, h3 {
        color: #161616;
    }
    /* 2. h2 : bordure bleue bottom */
    h2 {
        border-bottom: 2px solid #000091;
        padding-bottom: 0.5rem;
        margin-top: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    /* 2. Harmoniser les st.subheader (h3) avec une bordure fine */
    h3 {
        border-bottom: 1px solid #D4D4F7;
        padding-bottom: 0.35rem;
        margin-top: 2rem !important;
        margin-bottom: 0.75rem !important;
        font-size: 1.1rem;
        font-weight: 600;
        color: #000091;
    }

    /* ---- Séparateurs ---- */
    hr {
        border: none;
        border-top: 1px solid #E8E8F0;
        margin: 2rem 0;
    }

    /* ---- 4. Tableaux : alternance de couleurs, header visible ---- */
    [data-testid="stDataFrame"] {
        border: 1px solid #D4D4F7;
        border-radius: 4px;
        overflow: hidden;
    }
    /* Header du dataframe */
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] [data-testid="glideDataEditor"] .header-row {
        background-color: #000091 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    /* Alternance de lignes */
    [data-testid="stDataFrame"] tr:nth-child(even) td {
        background-color: #F5F5FE !important;
    }
    [data-testid="stDataFrame"] tr:hover td {
        background-color: #E8E8F7 !important;
    }

    /* ---- 6. Alertes/warnings : remplacer jaune par bandeau DSFR bleu clair ---- */
    /* Warning -> bleu DSFR info */
    div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
    div[data-baseweb="notification"] {
        border-radius: 0 !important;
    }
    .stAlert[data-baseweb="notification"] {
        border-radius: 0;
    }
    /* Override toutes les alertes warning en info-style DSFR */
    div[data-testid="stAlert"] {
        border-radius: 0 !important;
        border-left-width: 4px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.88rem !important;
        margin: 0.75rem 0 !important;
    }
    /* Warning : remplacer jaune par bleu info DSFR */
    div[data-testid="stAlert"][kind="warning"],
    div[data-testid="stNotification"] {
        background-color: #E8F0FF !important;
        border-left-color: #000091 !important;
        color: #161616 !important;
    }
    /* Cibler le warning Streamlit (fond jaune -> bleu clair) */
    .stAlert > div[data-baseweb="notification"] {
        background-color: #E8F0FF !important;
        border: 1px solid #B3C3F0 !important;
        border-left: 4px solid #000091 !important;
        color: #161616 !important;
    }
    /* Icône du warning */
    .stAlert svg {
        fill: #000091 !important;
    }
    /* Forcer remplacement couleurs warning (yellow) par bleu DSFR */
    [data-testid="stAlert"][data-baseweb="notification"] {
        background: #E8F0FF !important;
        border-left: 4px solid #000091 !important;
    }

    /* ---- 7. Footer officiel ---- */
    .rf-footer {
        border-top: 3px solid #000091;
        background: #F5F5FE;
        padding: 1.25rem 1.5rem;
        margin-top: 3.5rem;
        border-radius: 0 0 4px 4px;
    }
    .rf-footer-title {
        color: #000091;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }
    .rf-footer-body {
        color: #444;
        font-size: 0.82rem;
        line-height: 1.6;
    }
    .rf-footer-body a {
        color: #000091;
        text-decoration: underline;
    }

    /* ---- 8. Espacement général entre sections ---- */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem !important;
    }

    /* ---- 9. Bouton télécharger CSV style DSFR ---- */
    [data-testid="stDownloadButton"] > button {
        background-color: #000091 !important;
        color: #FFFFFF !important;
        border: 2px solid #000091 !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1.25rem !important;
        letter-spacing: 0.02em;
        transition: background-color 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #1212FF !important;
        border-color: #1212FF !important;
    }
    [data-testid="stDownloadButton"] > button:active {
        background-color: #000070 !important;
        border-color: #000070 !important;
    }

    /* ---- 10. Responsive mobile ---- */
    @media (max-width: 768px) {
        .rf-header h1 {
            font-size: 1.25rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        [data-testid="stMetricLabel"] > div {
            font-size: 0.72rem !important;
        }
        h2 {
            font-size: 1.1rem;
        }
        h3 {
            font-size: 0.95rem;
        }
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        [data-testid="stDownloadButton"] > button {
            width: 100% !important;
        }
    }

    /* ---- Branding Streamlit masqué ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- En-tête officiel ---
st.markdown("""
<div class="rf-header">
    <p class="rf-marianne">Republique Francaise</p>
    <h1>Elections municipales 2026</h1>
    <p class="rf-subtitle">Resultats du 1er tour — 15 mars 2026 | Source : Ministere de l'Interieur</p>
</div>
""", unsafe_allow_html=True)

# --- Couleurs par nuance (style Ministère de l'Intérieur) ---
COULEURS = {
    "Extrême gauche": "#BB0000",
    "Parti communiste": "#DD0000",
    "La France insoumise": "#CC2443",
    "Parti socialiste": "#E75480",
    "Écologistes": "#00A86B",
    "Union de la gauche": "#FF6B6B",
    "Divers gauche": "#F4A4A4",
    "Divers centre": "#F2994A",
    "Union au centre": "#F2C94C",
    "MoDem": "#F2994A",
    "Renaissance": "#F2C94C",
    "Divers": "#BDBDBD",
    "Les Républicains": "#0066CC",
    "Union de la droite": "#2D5FA0",
    "Divers droite": "#6C9BD2",
    "Rassemblement National": "#0D378A",
    "Reconquête": "#152555",
    "Extrême droite": "#333333",
    "Autres / Sans étiquette": "#9E9E9E",
}

ORDRE_GAUCHE_DROITE = [
    "Extrême gauche", "Parti communiste", "La France insoumise",
    "Parti socialiste", "Écologistes", "Union de la gauche", "Divers gauche",
    "Divers centre", "Union au centre", "MoDem", "Renaissance",
    "Divers", "Autres / Sans étiquette",
    "Les Républicains", "Union de la droite", "Divers droite",
    "Rassemblement National", "Reconquête", "Extrême droite",
]

BLOCS = {
    "Gauche": ["Extrême gauche", "Parti communiste", "La France insoumise",
               "Parti socialiste", "Écologistes", "Union de la gauche", "Divers gauche"],
    "Centre": ["Divers centre", "Union au centre", "MoDem", "Renaissance"],
    "Droite": ["Les Républicains", "Union de la droite", "Divers droite"],
    "Extrême droite": ["Rassemblement National", "Reconquête", "Extrême droite"],
    "Autres": ["Divers", "Autres / Sans étiquette"],
}

COULEURS_BLOCS = {
    "Gauche": "#E74C3C",
    "Centre": "#F2994A",
    "Droite": "#2D5FA0",
    "Extrême droite": "#0D378A",
    "Autres": "#BDBDBD",
}

# Template Plotly style officiel DSFR
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Marianne, Arial, sans-serif", size=12, color="#161616"),
    margin=dict(l=24, r=24, t=48, b=32),
    xaxis=dict(
        gridcolor="#EEEEEE",
        linecolor="#CCCCCC",
        tickfont=dict(size=11, color="#444444"),
        title_font=dict(size=12, color="#161616"),
        showgrid=True,
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#EEEEEE",
        linecolor="#CCCCCC",
        tickfont=dict(size=11, color="#444444"),
        title_font=dict(size=12, color="#161616"),
        showgrid=True,
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#DDDDDD",
        borderwidth=1,
        font=dict(size=11),
    ),
    title_font=dict(size=14, color="#000091", family="Marianne, Arial, sans-serif"),
    hoverlabel=dict(
        bgcolor="#FFFFFF",
        bordercolor="#000091",
        font_size=12,
        font_family="Marianne, Arial, sans-serif",
    ),
)


def style_fig(fig):
    """Applique le style officiel DSFR a un graphique Plotly."""
    fig.update_layout(**PLOTLY_LAYOUT)
    # S'assurer que le fond est bien blanc sur tous les axes
    fig.update_xaxes(showgrid=True, gridcolor="#EEEEEE", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE", zeroline=False)
    return fig


@st.cache_data(ttl=60)
def load_data():
    """Charge les données CSV."""
    path = "data/resultats_municipales_2026.csv"
    if not os.path.exists(path):
        st.error("Fichier de données introuvable. Lancez d'abord `python scrape_municipales.py`.")
        st.stop()

    df = pd.read_csv(path, dtype={"department": str})

    # Nettoyage
    df["dept_code"] = df["department"].str.split("-").str[0]
    df["dept_nom"] = df["department"].str.split("-", n=1).str[1].str.replace("-", " ").str.title()

    # Remplir les nuances manquantes
    df["nuance_label"] = df["nuance_label"].fillna("Autres / Sans étiquette")
    df["nuance_code"] = df["nuance_code"].fillna("AUT")
    df["candidat_voix"] = pd.to_numeric(df["candidat_voix"], errors="coerce").fillna(0).astype(int)
    df["candidat_pourcentage"] = pd.to_numeric(df["candidat_pourcentage"], errors="coerce")
    df["inscrits"] = pd.to_numeric(df["inscrits"], errors="coerce")
    df["votants"] = pd.to_numeric(df["votants"], errors="coerce")
    df["participation_pct"] = pd.to_numeric(df["participation_pct"], errors="coerce")

    # Bloc politique
    nuance_to_bloc = {}
    for bloc, nuances in BLOCS.items():
        for n in nuances:
            nuance_to_bloc[n] = bloc
    df["bloc"] = df["nuance_label"].map(nuance_to_bloc).fillna("Autres")

    # Flag : nuance fiable = communes > 1000 hab (nuances officielles du Ministère)
    # Les petites communes n'ont pas de nuance obligatoire → "Autres" non significatif
    df["nuance_fiable"] = df["nuance_label"] != "Autres / Sans étiquette"

    return df


def filter_nuances_fiables(df_src):
    """Filtre pour ne garder que les candidats avec nuance politique officielle.
    Utilisé pour les graphiques politiques (exclut les petites communes sans étiquette)."""
    return df_src[df_src["nuance_fiable"]]


def get_commune_stats(df):
    """Agrège les stats par commune (déduplique les lignes candidats)."""
    cols = ["commune", "slug", "department", "dept_code", "dept_nom",
            "inscrits", "votants", "participation_pct", "abstentions",
            "abstentions_pct", "blancs_nuls", "maire_sortant", "nb_candidats"]
    existing = [c for c in cols if c in df.columns]
    return df.drop_duplicates(subset=["slug"])[existing]


def get_dept_list(df):
    """Liste des départements triés."""
    depts = df[["dept_code", "dept_nom", "department"]].drop_duplicates()
    return depts.sort_values("dept_code")


# --- Chargement ---
df = load_data()
communes = get_commune_stats(df)
depts = get_dept_list(df)

# ===========================
# SIDEBAR
# ===========================

# 3. Logo RF élégant en haut de la sidebar
st.sidebar.markdown("""
<div class="rf-logo-sidebar">
    <span class="rf-badge">RF</span>
    <span class="rf-label">République<br>Française</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Municipales 2026")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", [
    "Vue nationale",
    "Carte de France",
    "Grandes villes",
    "Communes disputees",
    "Maires sortants battus",
    "Par département",
    "Recherche commune",
    "Comparateur",
    "Données brutes",
])

st.sidebar.markdown("---")
st.sidebar.caption("Source : data.gouv.fr — Ministère de l'Intérieur")
st.sidebar.caption(f"{len(communes):,} communes · {df['candidat_voix'].sum():,} voix")


# ===========================
# VUE NATIONALE
# ===========================
if page == "Vue nationale":
    st.header("Vue nationale")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    total_inscrits = communes["inscrits"].sum()
    total_votants = communes["votants"].sum()
    participation_moy = (total_votants / total_inscrits * 100) if total_inscrits > 0 else 0

    col1.metric("Communes", f"{len(communes):,}")
    col2.metric("Inscrits", f"{total_inscrits:,.0f}")
    col3.metric("Votants", f"{total_votants:,.0f}")
    col4.metric("Participation moyenne", f"{participation_moy:.1f}%")

    st.markdown("---")

    # --- Répartition des voix par famille politique ---
    st.subheader("Répartition des voix par famille politique")

    df_pol = filter_nuances_fiables(df)
    nb_communes_pol = df_pol.drop_duplicates(subset=["slug"]).shape[0]
    voix_pol = df_pol["candidat_voix"].sum()
    voix_total = df["candidat_voix"].sum()
    nb_depts = df["department"].nunique()
    if nb_depts < 90:
        st.warning(
            f"Scraping en cours : seulement {nb_depts} departements sur 95 charges. "
            f"Les resultats nationaux ne sont pas encore representatifs."
        )
    st.caption(
        f"Communes avec nuance officielle uniquement ({nb_communes_pol:,} communes, "
        f"{voix_pol:,} voix sur {voix_total:,} total). "
        f"Les petites communes sans etiquette partisane sont exclues de ce graphique."
    )

    tab_detail, tab_blocs = st.tabs(["Par nuance", "Par bloc"])

    with tab_detail:
        voix_par_nuance = (
            df_pol.groupby("nuance_label")["candidat_voix"]
            .sum()
            .reset_index()
            .rename(columns={"candidat_voix": "voix"})
        )
        voix_par_nuance["pct"] = voix_par_nuance["voix"] / voix_par_nuance["voix"].sum() * 100
        # Trier gauche → droite
        ordre = {v: i for i, v in enumerate(ORDRE_GAUCHE_DROITE)}
        voix_par_nuance["ordre"] = voix_par_nuance["nuance_label"].map(ordre).fillna(99)
        voix_par_nuance = voix_par_nuance.sort_values("ordre")

        fig = px.bar(
            voix_par_nuance,
            x="nuance_label", y="voix",
            color="nuance_label",
            color_discrete_map=COULEURS,
            text=voix_par_nuance["pct"].apply(lambda x: f"{x:.1f}%"),
            labels={"nuance_label": "", "voix": "Voix"},
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=500)
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with tab_blocs:
        voix_par_bloc = (
            df_pol.groupby("bloc")["candidat_voix"]
            .sum()
            .reset_index()
            .rename(columns={"candidat_voix": "voix"})
        )
        voix_par_bloc["pct"] = voix_par_bloc["voix"] / voix_par_bloc["voix"].sum() * 100
        bloc_ordre = {"Gauche": 0, "Centre": 1, "Droite": 2, "Extrême droite": 3, "Autres": 4}
        voix_par_bloc["ordre"] = voix_par_bloc["bloc"].map(bloc_ordre)
        voix_par_bloc = voix_par_bloc.sort_values("ordre")

        fig2 = px.pie(
            voix_par_bloc, values="voix", names="bloc",
            color="bloc", color_discrete_map=COULEURS_BLOCS,
            hole=0.4,
        )
        fig2.update_traces(textinfo="label+percent", textposition="outside")
        fig2.update_layout(height=500)
        st.plotly_chart(style_fig(fig2), use_container_width=True)

    st.markdown("---")

    # --- Participation par département ---
    st.subheader("Participation par département")

    dept_stats = (
        communes.groupby(["dept_code", "dept_nom"])
        .agg(inscrits=("inscrits", "sum"), votants=("votants", "sum"), nb_communes=("commune", "count"))
        .reset_index()
    )
    dept_stats["participation"] = dept_stats["votants"] / dept_stats["inscrits"] * 100

    fig3 = px.bar(
        dept_stats.sort_values("participation", ascending=True),
        x="participation", y="dept_nom",
        orientation="h",
        color="participation",
        color_continuous_scale="RdYlGn",
        labels={"participation": "Participation (%)", "dept_nom": ""},
        height=max(600, len(dept_stats) * 20),
    )
    fig3.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(style_fig(fig3), use_container_width=True)

    # --- Top candidats nationaux ---
    st.markdown("---")
    st.subheader("Top 20 des candidats par nombre de voix")

    top_candidats = (
        df.nlargest(20, "candidat_voix")[
            ["candidat_nom", "commune", "dept_nom", "nuance_label",
             "candidat_voix", "candidat_pourcentage", "candidat_elu"]
        ]
    )
    st.dataframe(
        top_candidats.rename(columns={
            "candidat_nom": "Candidat", "commune": "Commune", "dept_nom": "Département",
            "nuance_label": "Nuance", "candidat_voix": "Voix",
            "candidat_pourcentage": "% Exprimés", "candidat_elu": "Élu",
        }),
        use_container_width=True,
        hide_index=True,
    )


# ===========================
# CARTE DE FRANCE
# ===========================
elif page == "Carte de France":
    st.header("Carte de France par bloc politique")

    carte_mode = st.radio(
        "Afficher",
        ["Bloc dominant", "Participation"],
        horizontal=True,
    )

    # Charger le GeoJSON
    geojson_path = "data/departements.geojson"
    if not os.path.exists(geojson_path):
        st.error("Fichier departements.geojson manquant.")
        st.stop()
    with open(geojson_path, encoding="utf-8") as f:
        geojson = json.load(f)

    # Stats par département
    dept_stats = (
        communes.groupby(["dept_code", "dept_nom"])
        .agg(inscrits=("inscrits", "sum"), votants=("votants", "sum"))
        .reset_index()
    )
    dept_stats["participation"] = dept_stats["votants"] / dept_stats["inscrits"] * 100

    if carte_mode == "Bloc dominant":
        df_pol = filter_nuances_fiables(df)
        bloc_dept = (
            df_pol.groupby(["dept_code", "dept_nom", "bloc"])["candidat_voix"]
            .sum().reset_index()
        )
        idx = bloc_dept.groupby("dept_code")["candidat_voix"].idxmax()
        dominant = bloc_dept.loc[idx][["dept_code", "dept_nom", "bloc", "candidat_voix"]].copy()
        dominant = dominant.merge(dept_stats[["dept_code", "participation"]], on="dept_code", how="left")

        # Mapper bloc -> numérique pour le choropleth
        bloc_to_num = {"Gauche": 0, "Centre": 1, "Droite": 2, "Extrême droite": 3, "Autres": 4}
        dominant["bloc_num"] = dominant["bloc"].map(bloc_to_num)

        fig = px.choropleth_mapbox(
            dominant,
            geojson=geojson,
            locations="dept_code",
            featureidkey="properties.code",
            color="bloc",
            color_discrete_map=COULEURS_BLOCS,
            hover_name="dept_nom",
            hover_data={"participation": ":.1f", "candidat_voix": ":,.0f", "dept_code": False, "bloc": True},
            labels={"bloc": "Bloc dominant", "participation": "Participation %", "candidat_voix": "Voix"},
            mapbox_style="white-bg",
            center={"lat": 46.6, "lon": 2.5},
            zoom=4.5,
            opacity=0.8,
        )
        fig.update_layout(height=650, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(style_fig(fig), use_container_width=True)

        st.subheader("Detail par departement")
        display = dominant.sort_values("dept_code")[["dept_code", "dept_nom", "bloc", "candidat_voix", "participation"]]
        display.columns = ["Code", "Departement", "Bloc dominant", "Voix", "Participation %"]
        st.dataframe(display, use_container_width=True, hide_index=True)

    else:
        fig = px.choropleth_mapbox(
            dept_stats,
            geojson=geojson,
            locations="dept_code",
            featureidkey="properties.code",
            color="participation",
            color_continuous_scale=["#E74C3C", "#F2994A", "#27AE60"],
            hover_name="dept_nom",
            hover_data={"participation": ":.1f", "dept_code": False},
            labels={"participation": "Participation %"},
            mapbox_style="white-bg",
            center={"lat": 46.6, "lon": 2.5},
            zoom=4.5,
            opacity=0.8,
        )
        fig.update_layout(height=650, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(style_fig(fig), use_container_width=True)


# ===========================
# GRANDES VILLES
# ===========================
elif page == "Grandes villes":
    st.header("Resultats des grandes villes")

    # Seuil d'inscrits pour "grande ville"
    seuil = st.select_slider(
        "Taille minimum (inscrits)",
        options=[5000, 10000, 20000, 50000, 100000],
        value=20000,
    )

    # Filtrer les communes (inclure les secteurs PLM)
    grandes = communes[communes["inscrits"] >= seuil].sort_values("inscrits", ascending=False).copy()

    st.caption(f"{len(grandes)} communes de {seuil:,}+ inscrits")

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Communes", f"{len(grandes):,}")
    col2.metric("Inscrits", f"{grandes['inscrits'].sum():,.0f}")
    part_gv = grandes["votants"].sum() / grandes["inscrits"].sum() * 100 if grandes["inscrits"].sum() > 0 else 0
    col3.metric("Participation moyenne", f"{part_gv:.1f}%")

    st.markdown("---")

    # Répartition par bloc dans les grandes villes
    df_gv = df[df["slug"].isin(grandes["slug"])]
    df_gv_pol = filter_nuances_fiables(df_gv)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Voix par nuance")
        voix_gv = (
            df_gv_pol.groupby("nuance_label")["candidat_voix"]
            .sum().reset_index()
            .rename(columns={"candidat_voix": "voix"})
            .sort_values("voix", ascending=True)
        )
        if not voix_gv.empty:
            fig = px.bar(
                voix_gv, x="voix", y="nuance_label",
                orientation="h", color="nuance_label",
                color_discrete_map=COULEURS,
                labels={"nuance_label": "", "voix": "Voix"},
            )
            fig.update_layout(showlegend=False, height=450)
            st.plotly_chart(style_fig(fig), use_container_width=True)

    with col_right:
        st.subheader("Repartition par bloc")
        voix_bloc = (
            df_gv_pol.groupby("bloc")["candidat_voix"]
            .sum().reset_index()
            .rename(columns={"candidat_voix": "voix"})
        )
        if not voix_bloc.empty:
            fig2 = px.pie(
                voix_bloc, values="voix", names="bloc",
                color="bloc", color_discrete_map=COULEURS_BLOCS, hole=0.4,
            )
            fig2.update_traces(textinfo="label+percent")
            fig2.update_layout(height=450)
            st.plotly_chart(style_fig(fig2), use_container_width=True)

    # Classement des grandes villes par participation
    st.markdown("---")
    st.subheader("Participation par ville")

    fig3 = px.bar(
        grandes.head(40),
        x="commune", y="participation_pct",
        color="participation_pct",
        color_continuous_scale=["#E74C3C", "#F2994A", "#27AE60"],
        labels={"participation_pct": "Participation (%)", "commune": ""},
    )
    fig3.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(style_fig(fig3), use_container_width=True)

    # Tableau : résultats ville par ville
    st.markdown("---")
    st.subheader("Resultats ville par ville")

    ville_choice = st.selectbox(
        "Choisir une ville",
        options=grandes["slug"].tolist(),
        format_func=lambda s: f"{grandes[grandes['slug']==s]['commune'].values[0]} "
                              f"({grandes[grandes['slug']==s]['inscrits'].values[0]:,.0f} inscrits)",
    )

    if ville_choice:
        ville_row = grandes[grandes["slug"] == ville_choice].iloc[0]
        df_ville = df[df["slug"] == ville_choice]

        col1, col2, col3 = st.columns(3)
        col1.metric("Inscrits", f"{ville_row['inscrits']:,.0f}")
        col2.metric("Participation", f"{ville_row['participation_pct']:.1f}%")
        col3.metric("Maire sortant", ville_row.get("maire_sortant", "—") or "—")

        cands = df_ville[df_ville["candidat_nom"].notna()].sort_values("candidat_pourcentage", ascending=False)
        if not cands.empty:
            fig4 = px.bar(
                cands,
                x="candidat_pourcentage", y="candidat_nom",
                orientation="h",
                color="nuance_label",
                color_discrete_map=COULEURS,
                text=cands.apply(
                    lambda r: f"{r['candidat_pourcentage']:.1f}% ({int(r['candidat_voix']):,} voix)"
                    if pd.notna(r["candidat_pourcentage"]) else "", axis=1
                ),
                labels={"candidat_pourcentage": "% des exprimes", "candidat_nom": "", "nuance_label": "Nuance"},
            )
            fig4.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=max(300, len(cands) * 45),
            )
            fig4.update_traces(textposition="outside")
            st.plotly_chart(style_fig(fig4), use_container_width=True)

            st.dataframe(
                cands[["candidat_nom", "candidat_etiquette", "nuance_label",
                       "candidat_voix", "candidat_pourcentage", "candidat_elu"]].rename(columns={
                    "candidat_nom": "Candidat", "candidat_etiquette": "Etiquette",
                    "nuance_label": "Nuance", "candidat_voix": "Voix",
                    "candidat_pourcentage": "%", "candidat_elu": "Elu",
                }),
                use_container_width=True, hide_index=True,
            )


# ===========================
# COMMUNES DISPUTÉES
# ===========================
elif page == "Communes disputees":
    st.header("Communes les plus disputees")
    st.caption("Communes ou l'ecart entre le 1er et le 2e candidat est le plus faible.")

    @st.cache_data
    def compute_disputes(df_src):
        """Calcul vectorisé des écarts 1er-2e (pas de boucle Python)."""
        cands = df_src[df_src["candidat_nom"].notna() & (df_src["candidat_voix"] > 0)].copy()
        # Rang par commune (1er, 2e, etc.)
        cands["rang"] = cands.groupby("slug")["candidat_pourcentage"].rank(ascending=False, method="first")
        # Garder 1er et 2e
        top1 = cands[cands["rang"] == 1].set_index("slug")
        top2 = cands[cands["rang"] == 2].set_index("slug")
        # Joindre
        both = top1[["commune", "dept_nom", "inscrits", "participation_pct",
                      "candidat_nom", "nuance_label", "candidat_pourcentage", "candidat_voix"]].join(
            top2[["candidat_nom", "nuance_label", "candidat_pourcentage", "candidat_voix"]],
            lsuffix="_1", rsuffix="_2", how="inner"
        )
        both["ecart_pct"] = both["candidat_pourcentage_1"] - both["candidat_pourcentage_2"]
        both["ecart_voix"] = both["candidat_voix_1"] - both["candidat_voix_2"]
        both = both.reset_index()
        both.columns = ["slug", "commune", "departement", "inscrits", "participation",
                         "1er", "1er_nuance", "1er_pct", "1er_voix",
                         "2e", "2e_nuance", "2e_pct", "2e_voix",
                         "ecart_pct", "ecart_voix"]
        return both

    df_disputes = compute_disputes(df)

    if not df_disputes.empty:
        # Filtre par écart max
        max_ecart = st.slider("Ecart maximum (%)", 0.0, 20.0, 5.0, step=0.5)
        min_inscrits = st.slider("Inscrits minimum", 0, 20000, 1000, step=500)

        filtered = df_disputes[
            (df_disputes["ecart_pct"] <= max_ecart) &
            (df_disputes["inscrits"] >= min_inscrits)
        ].sort_values("ecart_pct")

        col1, col2 = st.columns(2)
        col1.metric("Communes disputees", f"{len(filtered):,}")
        col2.metric("Ecart moyen", f"{filtered['ecart_pct'].mean():.1f}%" if len(filtered) > 0 else "—")

        st.markdown("---")

        # Graphique : top 30 plus serrées
        top = filtered.head(30)
        if not top.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top["commune"] + " (" + top["departement"] + ")",
                x=top["1er_pct"],
                orientation="h",
                name="1er",
                marker_color="#000091",
                text=top["1er"].str.split().str[-1] + " " + top["1er_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="inside",
                textfont=dict(color="white", size=10),
            ))
            fig.add_trace(go.Bar(
                y=top["commune"] + " (" + top["departement"] + ")",
                x=top["2e_pct"],
                orientation="h",
                name="2e",
                marker_color="#6C9BD2",
                text=top["2e"].str.split().str[-1] + " " + top["2e_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="inside",
                textfont=dict(color="white", size=10),
            ))
            fig.update_layout(
                barmode="group",
                height=max(400, len(top) * 35),
                yaxis=dict(categoryorder="total ascending"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(style_fig(fig), use_container_width=True)

        # Tableau complet
        st.subheader("Detail")
        st.dataframe(
            filtered[["commune", "departement", "inscrits", "1er", "1er_nuance", "1er_pct",
                       "2e", "2e_nuance", "2e_pct", "ecart_pct", "ecart_voix"]].rename(columns={
                "commune": "Commune", "departement": "Dept", "inscrits": "Inscrits",
                "1er": "1er candidat", "1er_nuance": "Nuance 1er", "1er_pct": "% 1er",
                "2e": "2e candidat", "2e_nuance": "Nuance 2e", "2e_pct": "% 2e",
                "ecart_pct": "Ecart %", "ecart_voix": "Ecart voix",
            }),
            use_container_width=True, hide_index=True, height=500,
        )
    else:
        st.info("Pas de donnees pour calculer les ecarts.")


# ===========================
# MAIRES SORTANTS BATTUS
# ===========================
elif page == "Maires sortants battus":
    st.header("Maires sortants battus ou absents")

    @st.cache_data
    def compute_maires_battus(df_src, _communes_src):
        """Calcul vectorisé des maires sortants battus/absents."""
        # Extraire nom de famille du maire sortant
        cm = _communes_src[_communes_src["maire_sortant"].notna()][
            ["slug", "commune", "dept_nom", "inscrits", "maire_sortant"]
        ].copy()
        cm["maire_nom_famille"] = cm["maire_sortant"].str.upper().str.strip().str.split().str[-1]

        # Extraire nom de famille de chaque candidat
        cands = df_src[df_src["candidat_nom"].notna()].copy()
        cands["cand_nom_famille"] = cands["candidat_nom"].str.upper().str.strip().str.split().str[-1]

        # Joindre : chercher le maire parmi les candidats de sa commune
        merged = cm.merge(cands, on="slug", how="left", suffixes=("", "_cand"))
        maire_match = merged[merged["maire_nom_famille"] == merged["cand_nom_famille"]]

        # Dédupliquer (garder 1 match par commune)
        maire_match = maire_match.drop_duplicates(subset=["slug"], keep="first")
        slugs_avec_maire = set(maire_match["slug"])

        # Maires battus = se représente mais pas élu
        battus = maire_match[maire_match["candidat_elu"] != True][
            ["slug", "commune", "dept_nom", "inscrits", "maire_sortant",
             "candidat_pourcentage", "candidat_voix"]
        ].copy()
        battus.columns = ["slug", "commune", "departement", "inscrits", "maire_sortant", "maire_pct", "maire_voix"]
        battus["statut"] = "Battu au 1er tour"

        # Maires absents = pas trouvé parmi les candidats
        absents = cm[~cm["slug"].isin(slugs_avec_maire)][
            ["slug", "commune", "dept_nom", "inscrits", "maire_sortant"]
        ].copy()
        absents.columns = ["slug", "commune", "departement", "inscrits", "maire_sortant"]
        absents["statut"] = "Ne se represente pas"
        absents["maire_pct"] = None
        absents["maire_voix"] = None

        result = pd.concat([battus, absents], ignore_index=True)

        # Ajouter le gagnant (élu) de chaque commune
        elus = cands[cands["candidat_elu"] == True].drop_duplicates(subset=["slug"], keep="first")[
            ["slug", "candidat_nom", "nuance_label", "candidat_pourcentage"]
        ]
        elus.columns = ["slug", "gagnant", "gagnant_nuance", "gagnant_pct"]
        result = result.merge(elus, on="slug", how="left")
        result["gagnant"] = result["gagnant"].fillna("2e tour")

        return result

    df_maires = compute_maires_battus(df, communes)

    if not df_maires.empty:
        tab_battus, tab_absents = st.tabs(["Battus", "Ne se representent pas"])

        with tab_battus:
            battus = df_maires[df_maires["statut"] == "Battu au 1er tour"].sort_values("inscrits", ascending=False)
            st.metric("Maires battus au 1er tour", f"{len(battus):,}")

            min_ins = st.slider("Inscrits minimum", 0, 20000, 0, step=500, key="battus_ins")
            if min_ins > 0:
                battus = battus[battus["inscrits"] >= min_ins]

            st.dataframe(
                battus[["commune", "departement", "inscrits", "maire_sortant", "maire_pct",
                         "gagnant", "gagnant_nuance", "gagnant_pct"]].rename(columns={
                    "commune": "Commune", "departement": "Dept", "inscrits": "Inscrits",
                    "maire_sortant": "Maire sortant", "maire_pct": "% maire",
                    "gagnant": "Elu", "gagnant_nuance": "Nuance elu", "gagnant_pct": "% elu",
                }),
                use_container_width=True, hide_index=True, height=500,
            )

        with tab_absents:
            absents = df_maires[df_maires["statut"] == "Ne se represente pas"].sort_values("inscrits", ascending=False)
            st.metric("Maires ne se representant pas", f"{len(absents):,}")

            min_ins2 = st.slider("Inscrits minimum", 0, 20000, 0, step=500, key="absents_ins")
            if min_ins2 > 0:
                absents = absents[absents["inscrits"] >= min_ins2]

            st.dataframe(
                absents[["commune", "departement", "inscrits", "maire_sortant",
                          "gagnant", "gagnant_nuance", "gagnant_pct"]].rename(columns={
                    "commune": "Commune", "departement": "Dept", "inscrits": "Inscrits",
                    "maire_sortant": "Maire sortant",
                    "gagnant": "Elu", "gagnant_nuance": "Nuance elu", "gagnant_pct": "% elu",
                }),
                use_container_width=True, hide_index=True, height=500,
            )
    else:
        st.info("Pas de donnees sur les maires sortants.")


# ===========================
# PAR DÉPARTEMENT
# ===========================
elif page == "Par département":
    st.header("Resultats par departement")

    dept_choice = st.selectbox(
        "Choisir un département",
        options=depts["department"].tolist(),
        format_func=lambda x: f"{x.split('-')[0]} — {x.split('-', 1)[1].replace('-', ' ').title()}",
    )

    df_dept = df[df["department"] == dept_choice]
    communes_dept = get_commune_stats(df_dept)

    # KPIs département
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Communes", f"{len(communes_dept):,}")
    col2.metric("Inscrits", f"{communes_dept['inscrits'].sum():,.0f}")
    col3.metric("Votants", f"{communes_dept['votants'].sum():,.0f}")
    part = communes_dept["votants"].sum() / communes_dept["inscrits"].sum() * 100 if communes_dept["inscrits"].sum() > 0 else 0
    col4.metric("Participation", f"{part:.1f}%")

    st.markdown("---")

    df_dept_pol = filter_nuances_fiables(df_dept)
    nb_pol = df_dept_pol.drop_duplicates(subset=["slug"]).shape[0]
    pct_couvert = nb_pol / len(communes_dept) * 100 if len(communes_dept) > 0 else 0

    if nb_pol == 0:
        st.info(
            "Aucune commune de ce département n'a de nuance politique officielle "
            "(communes de moins de 1 000 habitants). Les graphiques politiques ne sont pas disponibles."
        )
    else:
        if pct_couvert < 20:
            st.warning(
                f"Seules {nb_pol} communes sur {len(communes_dept)} ({pct_couvert:.0f}%) ont une nuance "
                f"officielle dans ce département (communes de 1 000+ habitants). "
                f"Les graphiques ci-dessous ne sont pas représentatifs de l'ensemble du département."
            )
        else:
            st.caption(
                f"Graphiques politiques : {nb_pol} communes sur {len(communes_dept)} "
                f"({pct_couvert:.0f}%) avec nuance officielle."
            )

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Voix par nuance politique")
            voix_dept = (
                df_dept_pol.groupby("nuance_label")["candidat_voix"]
                .sum().reset_index()
                .rename(columns={"candidat_voix": "voix"})
                .sort_values("voix", ascending=True)
            )
            fig = px.bar(
                voix_dept, x="voix", y="nuance_label",
                orientation="h", color="nuance_label",
                color_discrete_map=COULEURS,
                labels={"nuance_label": "", "voix": "Voix"},
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(style_fig(fig), use_container_width=True)

        with col_right:
            st.subheader("Répartition par bloc")
            voix_bloc = (
                df_dept_pol.groupby("bloc")["candidat_voix"]
                .sum().reset_index()
                .rename(columns={"candidat_voix": "voix"})
            )
            fig2 = px.pie(
                voix_bloc, values="voix", names="bloc",
                color="bloc", color_discrete_map=COULEURS_BLOCS, hole=0.4,
            )
            fig2.update_traces(textinfo="label+percent")
            fig2.update_layout(height=400)
            st.plotly_chart(style_fig(fig2), use_container_width=True)

    # Participation par commune
    st.markdown("---")
    st.subheader("Participation par commune")

    sort_col = st.selectbox("Trier par", ["participation_pct", "inscrits", "commune"], index=0)
    ascending = st.checkbox("Ordre croissant", value=True)

    communes_sorted = communes_dept.dropna(subset=["participation_pct"]).sort_values(sort_col, ascending=ascending)

    fig3 = px.bar(
        communes_sorted.head(50),
        x="commune", y="participation_pct",
        color="participation_pct",
        color_continuous_scale="RdYlGn",
        labels={"participation_pct": "Participation (%)", "commune": ""},
    )
    fig3.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(style_fig(fig3), use_container_width=True)

    # Tableau détaillé
    st.markdown("---")
    st.subheader("Résultats détaillés")

    filter_nuance = st.multiselect(
        "Filtrer par nuance politique",
        options=sorted(df_dept["nuance_label"].dropna().unique()),
        default=[],
    )

    df_display = df_dept.copy()
    if filter_nuance:
        df_display = df_display[df_display["nuance_label"].isin(filter_nuance)]

    st.dataframe(
        df_display[["commune", "candidat_nom", "nuance_label", "candidat_voix",
                     "candidat_pourcentage", "candidat_elu"]].rename(columns={
            "commune": "Commune", "candidat_nom": "Candidat", "nuance_label": "Nuance",
            "candidat_voix": "Voix", "candidat_pourcentage": "%", "candidat_elu": "Élu",
        }),
        use_container_width=True, hide_index=True, height=400,
    )


# ===========================
# RECHERCHE COMMUNE
# ===========================
elif page == "Recherche commune":
    st.header("Recherche par commune")

    search = st.text_input("Nom de commune", placeholder="Ex: Toulouse, Bordeaux, Mende...")

    if search:
        matches = communes[communes["commune"].str.contains(search, case=False, na=False)]

        if matches.empty:
            st.warning("Aucune commune trouvée.")
        else:
            if len(matches) > 1:
                slug_labels = {
                    row["slug"]: f"{row['commune']} ({row['dept_nom']})"
                    for _, row in matches.head(100).iterrows()
                }
                selected_slug = st.selectbox(
                    f"{len(matches)} résultats — choisir :",
                    options=list(slug_labels.keys()),
                    format_func=lambda s: slug_labels.get(s, s),
                )
            else:
                selected_slug = matches.iloc[0]["slug"]

            commune_row = communes[communes["slug"] == selected_slug].iloc[0]
            df_commune = df[df["slug"] == selected_slug]

            # Fiche commune
            st.markdown("---")
            st.subheader(f"{commune_row['commune']} ({commune_row['dept_nom']})")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Inscrits", f"{commune_row.get('inscrits', 0):,.0f}")
            col2.metric("Votants", f"{commune_row.get('votants', 0):,.0f}")
            col3.metric("Participation", f"{commune_row.get('participation_pct', 0):.1f}%")
            col4.metric("Maire sortant", commune_row.get("maire_sortant", "—"))

            # Résultats candidats
            st.markdown("---")
            cands = df_commune[df_commune["candidat_nom"].notna()].sort_values(
                "candidat_pourcentage", ascending=False
            )

            if not cands.empty:
                fig = px.bar(
                    cands,
                    x="candidat_pourcentage", y="candidat_nom",
                    orientation="h",
                    color="nuance_label",
                    color_discrete_map=COULEURS,
                    text=cands.apply(
                        lambda r: f"{r['candidat_pourcentage']:.1f}% ({int(r['candidat_voix']):,} voix)"
                        if pd.notna(r["candidat_pourcentage"]) else "", axis=1
                    ),
                    labels={"candidat_pourcentage": "% des exprimés", "candidat_nom": "", "nuance_label": "Nuance"},
                )
                fig.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=max(300, len(cands) * 50),
                )
                fig.update_traces(textposition="outside")
                st.plotly_chart(style_fig(fig), use_container_width=True)

                # Tableau
                st.dataframe(
                    cands[["candidat_nom", "candidat_etiquette", "nuance_label",
                           "candidat_voix", "candidat_pourcentage", "candidat_elu", "candidat_sieges"]].rename(columns={
                        "candidat_nom": "Candidat", "candidat_etiquette": "Étiquette",
                        "nuance_label": "Nuance", "candidat_voix": "Voix",
                        "candidat_pourcentage": "%", "candidat_elu": "Élu", "candidat_sieges": "Sièges",
                    }),
                    use_container_width=True, hide_index=True,
                )
            else:
                st.info("Pas de résultats disponibles pour cette commune.")


# ===========================
# COMPARATEUR
# ===========================
elif page == "Comparateur":
    st.header("Comparateur")

    compare_mode = st.radio("Comparer", ["Communes", "Départements"], horizontal=True)

    if compare_mode == "Communes":
        # Recherche textuelle pour trouver les communes
        search_comp = st.text_input("Rechercher des communes", placeholder="Tapez un nom...")
        if search_comp:
            matches_comp = communes[communes["commune"].str.contains(search_comp, case=False, na=False)].head(50)
            slug_to_label = {
                row["slug"]: f"{row['commune']} ({row['dept_nom']})"
                for _, row in matches_comp.iterrows()
            }
        else:
            slug_to_label = {}

        selected = st.multiselect(
            "Communes à comparer",
            options=list(slug_to_label.keys()),
            format_func=lambda s: slug_to_label.get(s, s),
            max_selections=6,
        )

        if selected:
            # Participation comparée
            comp_data = communes[communes["slug"].isin(selected)]
            st.subheader("Participation")
            fig = px.bar(
                comp_data, x="commune", y="participation_pct",
                color="commune", text="participation_pct",
                labels={"participation_pct": "Participation (%)", "commune": ""},
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(style_fig(fig), use_container_width=True)

            # Répartition par bloc pour chaque commune
            df_comp = filter_nuances_fiables(df[df["slug"].isin(selected)])
            if df_comp.empty:
                st.info("Aucune des communes sélectionnées n'a de nuance politique officielle.")
            else:
                st.subheader("Répartition par bloc politique")
                bloc_comp = (
                    df_comp.groupby(["commune", "bloc"])["candidat_voix"]
                    .sum().reset_index()
                )
                totaux = bloc_comp.groupby("commune")["candidat_voix"].transform("sum")
                bloc_comp["pct"] = bloc_comp["candidat_voix"] / totaux * 100

                fig2 = px.bar(
                    bloc_comp, x="commune", y="pct", color="bloc",
                    color_discrete_map=COULEURS_BLOCS,
                    barmode="stack",
                    labels={"pct": "% des voix", "commune": "", "bloc": "Bloc"},
                )
                fig2.update_layout(height=400)
                st.plotly_chart(style_fig(fig2), use_container_width=True)

    else:  # Départements
        selected_depts = st.multiselect(
            "Choisir des départements",
            options=depts["department"].tolist(),
            format_func=lambda x: f"{x.split('-')[0]} — {x.split('-', 1)[1].replace('-', ' ').title()}",
            max_selections=8,
        )

        if selected_depts:
            df_comp = df[df["department"].isin(selected_depts)]

            # Participation comparée
            st.subheader("Participation")
            part_comp = (
                df_comp.drop_duplicates(subset=["slug"])
                .groupby("dept_nom")
                .agg(inscrits=("inscrits", "sum"), votants=("votants", "sum"))
                .reset_index()
            )
            part_comp["participation"] = part_comp["votants"] / part_comp["inscrits"] * 100

            fig = px.bar(
                part_comp, x="dept_nom", y="participation",
                color="dept_nom", text="participation",
                labels={"participation": "Participation (%)", "dept_nom": ""},
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(style_fig(fig), use_container_width=True)

            # Blocs politiques (nuances fiables uniquement)
            df_comp_pol = filter_nuances_fiables(df_comp)
            if df_comp_pol.empty:
                st.info("Aucune commune avec nuance officielle dans les départements sélectionnés.")
            else:
                st.subheader("Répartition par bloc politique")
                st.caption("Communes avec nuance officielle uniquement.")
                bloc_dept = (
                    df_comp_pol.groupby(["dept_nom", "bloc"])["candidat_voix"]
                    .sum().reset_index()
                )
                totaux = bloc_dept.groupby("dept_nom")["candidat_voix"].transform("sum")
                bloc_dept["pct"] = bloc_dept["candidat_voix"] / totaux * 100

                fig2 = px.bar(
                    bloc_dept, x="dept_nom", y="pct", color="bloc",
                    color_discrete_map=COULEURS_BLOCS,
                    barmode="stack",
                    labels={"pct": "% des voix", "dept_nom": "", "bloc": "Bloc"},
                )
                fig2.update_layout(height=400)
                st.plotly_chart(style_fig(fig2), use_container_width=True)

                # Détail par nuance
                st.subheader("Détail par nuance")
                nuance_dept = (
                    df_comp_pol.groupby(["dept_nom", "nuance_label"])["candidat_voix"]
                    .sum().reset_index()
                )
                totaux2 = nuance_dept.groupby("dept_nom")["candidat_voix"].transform("sum")
                nuance_dept["pct"] = nuance_dept["candidat_voix"] / totaux2 * 100

                fig3 = px.bar(
                    nuance_dept, x="dept_nom", y="pct", color="nuance_label",
                    color_discrete_map=COULEURS,
                    barmode="stack",
                    labels={"pct": "% des voix", "dept_nom": "", "nuance_label": "Nuance"},
                )
                fig3.update_layout(height=500)
                st.plotly_chart(style_fig(fig3), use_container_width=True)


# ===========================
# DONNÉES BRUTES
# ===========================
elif page == "Données brutes":
    st.header("Explorer et exporter les donnees")

    # Filtres
    col1, col2, col3 = st.columns(3)

    with col1:
        dept_filter = st.multiselect("Départements", options=depts["department"].tolist(),
            format_func=lambda x: f"{x.split('-')[0]} — {x.split('-', 1)[1].replace('-', ' ').title()}")
    with col2:
        nuance_filter = st.multiselect("Nuances politiques",
            options=sorted(df["nuance_label"].dropna().unique()))
    with col3:
        elu_filter = st.selectbox("Statut", ["Tous", "Élus uniquement", "Non élus"])

    min_pop = st.slider("Inscrits minimum", 0, 50000, 0, step=500)

    # Appliquer filtres
    df_filtered = df.copy()
    if dept_filter:
        df_filtered = df_filtered[df_filtered["department"].isin(dept_filter)]
    if nuance_filter:
        df_filtered = df_filtered[df_filtered["nuance_label"].isin(nuance_filter)]
    if elu_filter == "Élus uniquement":
        df_filtered = df_filtered[df_filtered["candidat_elu"] == True]
    elif elu_filter == "Non élus":
        df_filtered = df_filtered[df_filtered["candidat_elu"] != True]
    if min_pop > 0:
        df_filtered = df_filtered[df_filtered["inscrits"] >= min_pop]

    st.markdown(f"**{len(df_filtered):,} lignes** après filtrage")

    # Affichage
    display_cols = ["commune", "dept_nom", "candidat_nom", "nuance_label", "bloc",
                    "candidat_voix", "candidat_pourcentage", "candidat_elu",
                    "inscrits", "participation_pct"]
    existing_cols = [c for c in display_cols if c in df_filtered.columns]

    st.dataframe(df_filtered[existing_cols], use_container_width=True, hide_index=True, height=500)

    # Export
    csv_data = df_filtered.to_csv(index=False, encoding="utf-8")
    st.download_button(
        label="Telecharger en CSV",
        data=csv_data,
        file_name="municipales_2026_export.csv",
        mime="text/csv",
    )

# --- Footer officiel ---
st.markdown("""
<div class="rf-footer">
    <div class="rf-footer-title">Republique Francaise — Ministere de l'Interieur et des Outre-mer</div>
    <div class="rf-footer-body">
        Donnees issues de <a href="https://www.data.gouv.fr" target="_blank">data.gouv.fr</a>
        sous <strong>Licence Ouverte 2.0</strong>.<br>
        Resultats officiels du 1<sup>er</sup> tour des elections municipales — 15 mars 2026.<br>
        Ce tableau de bord est un outil de visualisation. Se referer au site du Ministere pour les resultats officiels.
    </div>
</div>
""", unsafe_allow_html=True)
