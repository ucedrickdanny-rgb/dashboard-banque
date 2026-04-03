import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from etl import run_pipeline, transform, load
from previsions import faire_previsions
from login import verifier_login, peut_voir, hindura_password

st.set_page_config(
    page_title="Dashboard Banque — Burundi",
    page_icon="🏦", layout="wide"
)

if 'user' not in st.session_state:
    st.session_state['user'] = None

def page_login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🏦 Dashboard ya Banque — Burundi")
        st.markdown("*Injira na compte yawe kugira urabe données*")
        st.divider()
        username = st.text_input("👤 Utilisateur",
                     placeholder="ex: admin, gitega, mukozi...")
        password = st.text_input("🔒 Mot de passe",
                     type="password",
                     placeholder="Shira password yawe")
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

st.sidebar.title("🏦 Dashboard Banque")
st.sidebar.success(f"👤 {user['nom']}")
st.sidebar.caption(f"Role: {role}")
st.sidebar.divider()

fichier = None
if peut_voir(role, 'upload'):
    st.sidebar.subheader("📁 Shira données nshasha")
    fichier = st.sidebar.file_uploader(
        "Excel canke CSV y'uyu munsi",
        type=['xlsx','xls','csv']
    )
    st.sidebar.divider()

if agence_user == 'Zose' and role != 'operateur':
    st.sidebar.subheader("🔍 Filtre")

st.sidebar.divider()
if st.sidebar.button("🚪 Sohoka", use_container_width=True):
    st.session_state['user'] = None
    st.rerun()

st.sidebar.divider()
with st.sidebar.expander("🔐 Hindura password yawe"):
    pw_kera    = st.text_input("Password ya kera",
                   type="password", key="pw_kera")
    pw_nshasha = st.text_input("Password nshasha",
                   type="password", key="pw_new")
    pw_ponovya = st.text_input("Ponovya password nshasha",
                   type="password", key="pw_conf")
    st.sidebar.caption("✓ Ntarengeje inyuguti 8 · ✓ Ifise numero")
    if st.button("Hindura →", use_container_width=True):
        if pw_kera and pw_nshasha and pw_ponovya:
            vyakunze, msg = hindura_password(
                user['username'], pw_kera, pw_nshasha, pw_ponovya
            )
            if vyakunze:
                st.success(msg)
                st.toast("✓ Password yahindutse!", icon="🔐")
            else:
                st.error(msg)
        else:
            st.warning("⚠ Uzuza ibibanza vyose")

@st.cache_data
def charger_defaut():
    df, kpis, mensuel, par_agence = run_pipeline()
    prev = faire_previsions(df, 'depot', 90)
    return df, kpis, mensuel, par_agence, prev

if fichier is not None:
    st.sidebar.success(f"✓ {fichier.name} yakuruwe!")
    df_raw = (pd.read_csv(fichier) if fichier.name.endswith('.csv')
              else pd.read_excel(fichier))
    with st.spinner("⏳ ETL ikora — rindira..."):
        df                        = transform(df_raw)
        kpis, mensuel, par_agence = load(df)
        prev                      = faire_previsions(df, 'depot', 90)
    st.toast("✓ Données nshasha zashiwe!", icon="✅")
else:
    df, kpis, mensuel, par_agence, prev = charger_defaut()

if agence_user == 'Zose':
    agences = ["Zose"] + sorted(df['agence'].unique().tolist())
    choix   = (st.sidebar.selectbox("Agence", agences)
               if role != 'operateur' else "Zose")
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

st.title("🏦 Dashboard ya Banque — Burundi")
st.info(f"👤 {user['nom']} | 📍 {choix}")
st.divider()

if peut_voir(role, 'kpis'):
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("💰 Depot moyen",   f"BIF {df_filtre['depot'].mean():,.0f}")
    with c2: st.metric("💸 Retrait moyen", f"BIF {df_filtre['retrait'].mean():,.0f}")
    with c3: st.metric("👥 Clients moyen", f"{df_filtre['clients'].mean():,.0f}")
    with c4: st.metric("📊 Solde net",     f"BIF {df_filtre['solde_net'].iloc[-1]:,.0f}")
    with c5: st.metric(titre_kigega,       f"BIF {kigega_montant:,.0f}")
    st.divider()
else:
    st.warning("📁 Shira Excel uyu munsi — maze ubibwire Chef wawe")
    st.stop()

if peut_voir(role, 'graphiques'):
    st.subheader("📈 Dépôts — Historique + Prévisions z'amezi 3")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_filtre['date'], y=df_filtre['depot'],
        name='Historique', line=dict(color='#1D4E8F', width=1.5)))
    prev_g = prev.tail(90)
    fig1.add_trace(go.Scatter(
        x=prev_g['ds'], y=prev_g['yhat'],
        name='Prévisions', line=dict(color='#BA7517', width=2, dash='dot')))
    fig1.add_trace(go.Scatter(
        x    = prev_g['ds'].tolist() + prev_g['ds'].tolist()[::-1],
        y    = prev_g['yhat_upper'].tolist() + prev_g['yhat_lower'].tolist()[::-1],
        fill='toself', fillcolor='rgba(186,117,23,0.1)',
        line=dict(color='rgba(0,0,0,0)'), name='Intervalle'))
    fig1.update_layout(height=300, margin=dict(t=10))
    st.plotly_chart(fig1, width='stretch')

if peut_voir(role, 'kigega'):
    st.subheader(titre_kigega)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_filtre['date'], y=df_filtre['solde_cumulatif'],
        fill='tozeroy', line=dict(color='#1D9E75', width=2),
        fillcolor='rgba(29,158,117,0.1)', name='Kigega'))
    fig2.add_hline(y=0, line_dash='dot', line_color='red',
                   annotation_text="⚠ Seuil ya akaga")
    fig2.update_layout(height=260, margin=dict(t=10))
    st.plotly_chart(fig2, width='stretch')

if peut_voir(role, 'agences') and choix == "Zose":
    st.subheader("🏪 Performance ya Agences Zose")
    ca, cb = st.columns(2)
    with ca:
        fig3 = px.bar(par_agence, x='agence', y='depot_total',
                      color='agence', title="Dépôts totaux",
                      color_discrete_sequence=['#1D4E8F','#1D9E75','#BA7517','#D4537E'])
        fig3.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig3, width='stretch')
    with cb:
        fig4 = px.bar(par_agence, x='agence', y='clients_total',
                      color='agence', title="Clients totaux",
                      color_discrete_sequence=['#1D4E8F','#1D9E75','#BA7517','#D4537E'])
        fig4.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig4, width='stretch')

if peut_voir(role, 'rapport'):
    st.subheader("📋 Rapport mensuel")
    mensuel['mois'] = mensuel['mois'].astype(str)
    st.dataframe(mensuel, width='stretch', height=260)