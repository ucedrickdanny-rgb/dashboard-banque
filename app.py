
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from etl import run_pipeline, transform, load, MAPPING_COLONNES
from previsions import faire_previsions
from login import verifier_login, peut_voir, hindura_password

st.set_page_config(
    page_title="Dashboard Banque — Burundi",
    page_icon="🏦", layout="wide"
)

st.markdown("""
<style>
    [data-testid="metric-container"] {
        background: white;
        border: 0.5px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        color: #0C2D6B !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        color: #6b7280 !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.72rem !important;
        font-weight: 500 !important;
    }
    hr { border-color: #e5e7eb; margin: 1rem 0; }
    h2 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #0C2D6B !important;
        padding-bottom: 6px;
        border-bottom: 2px solid #185FA5;
        margin-bottom: 12px !important;
        display: inline-block;
    }
    [data-testid="stAlert"] { border-radius: 10px !important; border-left-width: 4px !important; }
    [data-testid="stFileUploader"] { border: 1.5px dashed #185FA5; border-radius: 10px; padding: 8px; background: #f0f7ff; }
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 0.5px solid #e5e7eb; }
    .main .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state['user'] = None

def page_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;margin-bottom:20px;'>"
            "<div style='font-size:48px;'>🏦</div>"
            "<h2 style='color:#0C2D6B;margin:8px 0 4px;'>Dashboard ya Banque</h2>"
            "<p style='color:#6b7280;font-size:0.85rem;'>Injira na compte yawe kugira urabe données</p></div>",
            unsafe_allow_html=True
        )
        st.divider()
        username = st.text_input("👤 Utilisateur", placeholder="ex: admin, gitega...")
        password = st.text_input("🔒 Mot de passe", type="password", placeholder="Shira password yawe")
        if st.button("Injira →", use_container_width=True, type="primary"):
            user = verifier_login(username, password)
            if user:
                st.session_state['user'] = user
                st.rerun()
            else:
                st.error("❌ Username canke password si yo")

if st.session_state['user'] is None:
    page_login()
    st.stop()

user        = st.session_state['user']
role        = user['role']
agence_user = user['agence']

st.sidebar.markdown("## 🏦 Dashboard Banque")
st.sidebar.caption("Burundi — IA Analytics")
st.sidebar.divider()
st.sidebar.success(f"👤 {user['nom']}")
st.sidebar.caption(f"Role: {role}")
st.sidebar.divider()

fichier = None
if peut_voir(role, 'upload'):
    st.sidebar.subheader("📁 Shira données nshasha")
    fichier = st.sidebar.file_uploader(
        "Excel canke CSV y'uyu munsi",
        type=['xlsx', 'xls', 'csv']
    )
    st.sidebar.divider()

if agence_user == 'Zose' and role != 'operateur':
    st.sidebar.subheader("🔍 Filtre agence")

st.sidebar.divider()
if st.sidebar.button("🚪 Sohoka", use_container_width=True):
    st.session_state['user'] = None
    st.rerun()

with st.sidebar.expander("🔐 Hindura password yawe"):
    pw_kera    = st.text_input("Password ya kera",  type="password", key="pk")
    pw_nshasha = st.text_input("Password nshasha",  type="password", key="pn")
    pw_ponovya = st.text_input("Ponovya nshasha",   type="password", key="pp")
    st.sidebar.caption("✓ Ntarengeje 8 · ✓ Ifise numero")
    if st.button("Hindura →", use_container_width=True):
        if pw_kera and pw_nshasha and pw_ponovya:
            ok, msg = hindura_password(user['username'], pw_kera, pw_nshasha, pw_ponovya)
            st.success(msg) if ok else st.error(msg)
        else: st.warning("⚠ Uzuza ibibanza vyose")

@st.cache_data
def charger_defaut():
    df, kpis, mensuel, par_agence = run_pipeline()
    prev = faire_previsions(df, 'depot', 90)
    return df, kpis, mensuel, par_agence, prev

if fichier is not None:
    st.sidebar.success(f"✓ {fichier.name}")
    df_raw = (pd.read_csv(fichier) if fichier.name.endswith('.csv') else pd.read_excel(fichier))
    with st.spinner("⏳ ETL + IA ikora — rindira..."):
        colonnes = {k: v for k, v in MAPPING_COLONNES.items() if k in df_raw.columns}
        df_raw   = df_raw.rename(columns=colonnes)
        if 'date' in df_raw.columns:
            df_raw['date'] = pd.to_datetime(df_raw['date'], errors='coerce')
        df                        = transform(df_raw)
        kpis, mensuel, par_agence = load(df)
        prev                      = faire_previsions(df, 'depot', 90)
    st.toast("✓ Données nshasha zashiwe!", icon="✅")
else:
    df, kpis, mensuel, par_agence, prev = charger_defaut()

if agence_user == 'Zose':
    agences = ["Zose"] + sorted(df['agence'].unique().tolist())
    choix   = (st.sidebar.selectbox("Agence", agences) if role != 'operateur' else "Zose")
else:
    choix = agence_user
    st.sidebar.info(f"📍 Agence: {agence_user}")

if choix == "Zose":
    df_filtre      = df
    titre_kigega   = "🏛️ Kigega ca Banque Yose"
    kigega_montant = kpis['kigega_ubu']
else:
    df_filtre      = df[df['agence'] == choix]
    titre_kigega   = f"🏛️ Kigega ca {choix}"
    kigega_montant = df_filtre['kigega_agence'].iloc[-1]

st.markdown(
    "<h1 style='color:#0C2D6B;font-size:1.5rem;margin-bottom:4px;'>🏦 Dashboard ya Banque — Burundi</h1>",
    unsafe_allow_html=True
)
st.caption(f"👤 {user['nom']} | 📍 {choix} | Système de suivi financier avec IA")
st.divider()

if peut_voir(role, 'kpis'):
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("💰 Depot moyen/jour",   f"BIF {df_filtre['depot'].mean():,.0f}", "+3.2%")
    with c2: st.metric("💸 Retrait moyen/jour", f"BIF {df_filtre['retrait'].mean():,.0f}", "-1.1%")
    with c3: st.metric("👥 Clients/jour",        f"{df_filtre['clients'].mean():,.0f}", "+5")
    with c4: st.metric("📊 Solde net",           f"BIF {df_filtre['solde_net'].iloc[-1]:,.0f}")
    with c5: st.metric(titre_kigega,             f"BIF {kigega_montant:,.0f}")
    st.divider()
else:
    st.warning("📁 Shira Excel kugira urabe données")
    st.stop()

prev_moy = prev.tail(90)['yhat'].mean()
st.info(f"🤖 **Prévision IA (Prophet):** Depot moyen uzotegerezwa muri amezi 3: **BIF {prev_moy:,.0f}** — basé sur l'historique complet")

if peut_voir(role, 'graphiques'):
    st.subheader("📈 Dépôts — Historique + Prévisions IA (amezi 3)")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_filtre['date'], y=df_filtre['depot'],
        name='Historique', line=dict(color='#185FA5', width=1.5),
        fill='tozeroy', fillcolor='rgba(24,95,165,0.05)'))
    pv = prev.tail(90)
    fig1.add_trace(go.Scatter(x=pv['ds'], y=pv['yhat'],
        name='Prévisions IA', line=dict(color='#BA7517', width=2, dash='dot')))
    fig1.add_trace(go.Scatter(
        x=pv['ds'].tolist()+pv['ds'].tolist()[::-1],
        y=pv['yhat_upper'].tolist()+pv['yhat_lower'].tolist()[::-1],
        fill='toself', fillcolor='rgba(186,117,23,0.08)',
        line=dict(color='rgba(0,0,0,0)'), name='Intervalle'))
    fig1.update_layout(height=300, margin=dict(t=10, b=10),
        plot_bgcolor='white', paper_bgcolor='white',
        legend=dict(orientation='h', yanchor='bottom', y=1),
        xaxis=dict(showgrid=False, color='#9ca3af'),
        yaxis=dict(gridcolor='#f3f4f6', color='#9ca3af'))
    st.plotly_chart(fig1, width='stretch')

if peut_voir(role, 'kigega'):
    st.subheader(titre_kigega)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_filtre['date'], y=df_filtre['solde_cumulatif'],
        fill='tozeroy', line=dict(color='#1D9E75', width=2),
        fillcolor='rgba(29,158,117,0.08)', name='Kigega'))
    fig2.add_hline(y=0, line_dash='dot', line_color='#E24B4A',
                   annotation_text="⚠ Seuil critique", annotation_font_color="#E24B4A")
    fig2.update_layout(height=240, margin=dict(t=10, b=10),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=False, color='#9ca3af'),
        yaxis=dict(gridcolor='#f3f4f6', color='#9ca3af'))
    st.plotly_chart(fig2, width='stretch')

if peut_voir(role, 'agences') and choix == "Zose":
    st.subheader("🏪 Performance ya Agences")
    ca, cb = st.columns(2)
    colors = ['#185FA5','#1D9E75','#BA7517','#D4537E']
    with ca:
        fig3 = px.bar(par_agence, x='agence', y='depot_total', color='agence',
                      title="Dépôts totaux (BIF)", color_discrete_sequence=colors)
        fig3.update_layout(height=260, showlegend=False, plot_bgcolor='white',
            paper_bgcolor='white', title_font_color='#0C2D6B', title_font_size=13,
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#f3f4f6'))
        st.plotly_chart(fig3, width='stretch')
    with cb:
        fig4 = px.bar(par_agence, x='agence', y='clients_total', color='agence',
                      title="Clients totaux", color_discrete_sequence=colors)
        fig4.update_layout(height=260, showlegend=False, plot_bgcolor='white',
            paper_bgcolor='white', title_font_color='#0C2D6B', title_font_size=13,
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#f3f4f6'))
        st.plotly_chart(fig4, width='stretch')

if peut_voir(role, 'rapport'):
    st.subheader("📋 Rapport mensuel")
    mensuel['mois'] = mensuel['mois'].astype(str)
    st.dataframe(mensuel, width='stretch', height=260)

st.markdown("""
<div style='text-align:center;padding:20px 0 10px;color:#9ca3af;
     font-size:11px;border-top:0.5px solid #e5e7eb;margin-top:20px;'>
  🏦 Dashboard ya Banque — Burundi &nbsp;|&nbsp;
  Propulsé par Prophet AI &amp; Streamlit &nbsp;|&nbsp;
  Données sécurisées — Accès restreint
</div>
""", unsafe_allow_html=True)