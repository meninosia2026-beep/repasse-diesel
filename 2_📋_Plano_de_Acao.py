import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Plano de Ação — Diesel", page_icon="📋", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #F7F5F0; }
    .block-container { padding-top: 2rem; max-width: 1000px; }
    h1 { font-size: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("📋 Plano de ação — Repasse do Diesel")
st.caption("Trechos críticos identificados na análise. Atualiza automaticamente quando os CSVs são atualizados.")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
def load(name):
    for folder in ["data", "."]:
        p = os.path.join(folder, name)
        if os.path.exists(p):
            return pd.read_csv(p)
    return None

df_semanas    = load("semanas_anteriores.csv")
df_s16        = load("semana_16_a_22.csv")
df_s23        = load("semana_23_a_29.csv")
df_pascoa     = load("feriado_pascoa.csv")
df_tiradentes = load("feriado_tiradentes.csv")

# ── CALCULA CRÍTICOS ──────────────────────────────────────────────────────────
def get_criticos(*dfs):
    records = []
    for df in dfs:
        if df is None: continue
        d = df.copy()
        d["pct"] = (d["media_preco_atual"] - d["media_preco_referencia"]) / d["media_preco_referencia"] * 100
        records.append(d[["trecho_unico","pct"]])
    if not records: return pd.DataFrame()
    combined = pd.concat(records)
    return (combined[combined["pct"] >= 5]
            .groupby("trecho_unico")["pct"].mean()
            .reset_index()
            .sort_values("pct", ascending=False)
            .head(10))

def fmt(t):
    return " › ".join([p.capitalize() for p in t.split("-") if len(p) > 2])

def cls_label(pct):
    if pct >= 15: return "🔴 Muito relevante"
    if pct >= 10: return "🟡 Moderado"
    return "🟢 Leve"

criticos = get_criticos(df_semanas, df_s16, df_s23, df_pascoa, df_tiradentes)

if criticos.empty:
    st.warning("Nenhum dado encontrado. Verifique se os CSVs estão na pasta `data/`.")
    st.stop()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "plano" not in st.session_state:
    st.session_state.plano = {}

STATUS = ["Aberto", "Em andamento", "Monitorando", "Concluído"]
EMOJI  = {"Aberto": "🔴", "Em andamento": "🟡", "Monitorando": "🔵", "Concluído": "🟢"}

# ── PLANO POR TRECHO ──────────────────────────────────────────────────────────
for _, row in criticos.iterrows():
    t   = row["trecho_unico"]
    pct = row["pct"]
    p   = st.session_state.plano.get(t, {})
    ico = EMOJI.get(p.get("status", "Aberto"), "🔴")

    with st.expander(f"{ico}  {fmt(t)} — {pct:+.1f}% · {cls_label(pct)}", expanded=False):
        c1, c2, c3 = st.columns([2, 1.5, 1.5])
        with c1:
            resp = st.text_input("Responsável", value=p.get("responsavel", ""), key=f"r_{t}")
        with c2:
            prazo_val = None
            if p.get("prazo"):
                try: prazo_val = date.fromisoformat(p["prazo"])
                except: pass
            prazo = st.date_input("Prazo", value=prazo_val, key=f"d_{t}")
        with c3:
            idx = STATUS.index(p.get("status", "Aberto"))
            status = st.selectbox("Status", STATUS, index=idx, key=f"s_{t}")

        acao = st.text_area("Ação / observações", value=p.get("acao", ""), key=f"a_{t}", height=75)

        if st.button("Salvar", key=f"btn_{t}"):
            st.session_state.plano[t] = {
                "responsavel": resp,
                "prazo": prazo.isoformat() if prazo else "",
                "status": status,
                "acao": acao,
            }
            st.success("Salvo!", icon="✅")

# ── RESUMO ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("#### Resumo do plano")

rows = []
for _, row in criticos.iterrows():
    t = row["trecho_unico"]
    p = st.session_state.plano.get(t, {})
    rows.append({
        "Trecho":      fmt(t),
        "Variação":    f"{row['pct']:+.1f}%",
        "Responsável": p.get("responsavel", "—"),
        "Prazo":       p.get("prazo", "—"),
        "Status":      p.get("status", "Aberto"),
        "Ação":        p.get("acao", "—"),
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

csv_bytes = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Exportar CSV", csv_bytes, "plano_acao_diesel.csv", "text/csv")
