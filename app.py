import streamlit as st

pg = st.navigation([
    st.Page("dashboard.py",                    title="Dashboard",     icon="🚌", default=True),
    st.Page("pages/2_📋_Plano_de_Acao.py",    title="Plano de ação", icon="📋"),
])
pg.run()
