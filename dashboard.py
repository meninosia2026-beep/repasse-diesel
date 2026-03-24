import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from zoneinfo import ZoneInfo
import plotly.graph_objects as go

st.set_page_config(
    page_title="Repasse do Diesel",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #F7F5F0 !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* NAV */
.nav-bar {
    background: white;
    border-bottom: 1px solid rgba(0,0,0,0.07);
    padding: 0 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-title {
    font-family: 'DM Serif Display', serif;
    font-size: 17px;
    color: #1A1A18;
    letter-spacing: -0.2px;
}
.nav-badge {
    font-size: 11px;
    color: #2E6B40;
    background: #E3F2E9;
    border: 1px solid rgba(46,107,64,.2);
    border-radius: 20px;
    padding: 4px 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.nav-dot { width:7px; height:7px; border-radius:50%; background:#2E6B40; display:inline-block; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-bottom: 1px solid rgba(0,0,0,0.07);
    padding: 0 32px;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #6B6963;
    padding: 14px 18px;
    border-radius: 0;
    background: transparent;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #1A1A18 !important;
    border-bottom: 2px solid #C8402A !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] {
    padding: 28px 40px !important;
    background: #F7F5F0;
}

/* CARDS */
.metric-card {
    background: white;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 10px;
    padding: 16px 18px;
}
.verdict-card {
    background: white;
    border: 1px solid rgba(0,0,0,0.07);
    border-left: 4px solid #C8402A;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.verdict-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #C8402A;
    margin-bottom: 8px;
}
.verdict-title {
    font-family: 'DM Serif Display', serif;
    font-size: 18px;
    line-height: 1.35;
    color: #1A1A18;
    margin-bottom: 8px;
}
.verdict-body { font-size: 13px; color: #6B6963; line-height: 1.7; }

/* TABLES */
.stDataFrame { border-radius: 12px; overflow: hidden; }
thead tr th {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
    color: #9C9A93 !important;
    background: #F0EDE6 !important;
}

/* BADGE */
.badge-alto  { background:#FAE8E4; color:#C8402A; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-mod   { background:#FDF3DC; color:#B07A10; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-leve  { background:#E3F2E9; color:#2E6B40; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-neg   { background:#EDECE9; color:#4A4A46; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }

/* SECTION TITLE */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 17px;
    font-weight: 400;
    color: #1A1A18;
    margin-bottom: 4px;
}
.section-desc { font-size: 13px; color: #6B6963; margin-bottom: 16px; }

/* PLANO */
.stExpander {
    background: white !important;
    border: 1px solid rgba(0,0,0,0.07) !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
.stExpander summary {
    font-size: 13px !important;
    font-weight: 500 !important;
}
div[data-testid="stFileUploader"] {
    background: white;
    border-radius: 10px;
    padding: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────────────────
def load_file(upload, default_name):
    if upload:
        return pd.read_csv(upload)
    for folder in ["data", "."]:
        path = os.path.join(folder, default_name)
        if os.path.exists(path):
            return pd.read_csv(path)
    return None

def variation(atual, ref):
    if not ref or ref == 0: return None
    return ((atual - ref) / ref) * 100

def classify(pct):
    if pct is None: return None
    if pct >= 15: return "alto"
    if pct >= 10: return "mod"
    if pct >= 5:  return "leve"
    if pct > 0:   return "pos"
    return "neg"

def badge_html(cls):
    labels = {"alto":"Muito relevante","mod":"Moderado","leve":"Leve","pos":"Leve positivo","neg":"Sem repasse"}
    css    = {"alto":"badge-alto","mod":"badge-mod","leve":"badge-leve","pos":"badge-leve","neg":"badge-neg"}
    return f'<span class="{css.get(cls,"badge-neg")}">{labels.get(cls,"–")}</span>'

def fmt_var(pct):
    if pct is None: return "–"
    return f"{'+' if pct>0 else ''}{pct:.1f}%"

def fmt_trecho(t):
    return " › ".join([p.capitalize() for p in t.split("-") if len(p) > 2])

def enrich(df):
    d = df.copy()
    d["pct"] = d.apply(lambda r: variation(r.media_preco_atual, r.media_preco_referencia), axis=1)
    d["cls"] = d["pct"].apply(classify)
    d["trecho_fmt"] = d["trecho_unico"].apply(fmt_trecho)
    return d

def color_for(cls):
    return {"alto":"#C8402A","mod":"#B07A10","leve":"#2E6B40","pos":"#2E6B40","neg":"#9C9A93"}.get(cls,"#9C9A93")

def plotly_bar(df_sorted, x_col="pct", y_col="trecho_fmt", height=None):
    h = height or max(300, len(df_sorted) * 38)
    colors = [color_for(c) for c in df_sorted["cls"]]
    fig = go.Figure(go.Bar(
        x=df_sorted[x_col].round(1), y=df_sorted[y_col],
        orientation="h", marker_color=colors,
        text=[f"{v:+.1f}%" for v in df_sorted[x_col]],
        textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(
        height=h, margin=dict(l=0,r=60,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)",
                   ticksuffix="%", zeroline=True, zerolinecolor="rgba(0,0,0,0.15)"),
        yaxis=dict(showgrid=False),
        font=dict(family="DM Sans, sans-serif", size=12),
        showlegend=False,
    )
    return fig

def filter_df(df, f):
    if f == "Todos":           return df
    if f == "Com repasse":     return df[df["pct"] >= 5]
    if f == "Muito relevante": return df[df["cls"] == "alto"]
    if f == "Moderado":        return df[df["cls"] == "mod"]
    if f == "Leve":            return df[df["cls"].isin(["leve","pos"])]
    return df

def render_table(df, cols):
    show = df[list(cols.keys())].copy()
    show.columns = list(cols.values())
    st.dataframe(show, use_container_width=True, hide_index=True)

def filter_chips(key):
    opts = ["Todos","Com repasse","Muito relevante","Moderado","Leve"]
    return st.radio("Filtrar:", opts, horizontal=True, key=f"f_{key}", label_visibility="collapsed")

# ── UPLOAD ─────────────────────────────────────────────────────────────────────
with st.expander("📂 Atualizar arquivos CSV", expanded=False):
    st.caption("Substitua qualquer arquivo para atualizar a análise instantaneamente.")
    c1, c2, c3 = st.columns(3)
    with c1:
        up_sem = st.file_uploader("Semanas anteriores", type="csv", key="up_sem")
        up_s16 = st.file_uploader("Semana 16–22/03",   type="csv", key="up_s16")
    with c2:
        up_s23 = st.file_uploader("Semana 23–29/03",   type="csv", key="up_s23")
        up_pas = st.file_uploader("Feriado Páscoa",    type="csv", key="up_pas")
    with c3:
        up_tir = st.file_uploader("Feriado Tiradentes",type="csv", key="up_tir")

# ── LOAD ───────────────────────────────────────────────────────────────────────
df_sem = load_file(up_sem, "semanas_anteriores.csv")
df_s16 = load_file(up_s16, "semana_16_a_22.csv")
df_s23 = load_file(up_s23, "semana_23_a_29.csv")
df_pas = load_file(up_pas, "feriado_pascoa.csv")
df_tir = load_file(up_tir, "feriado_tiradentes.csv")

# ── TIMESTAMP ──────────────────────────────────────────────────────────────────
any_upload = any([up_sem, up_s16, up_s23, up_pas, up_tir])
if any_upload:
    now_sp = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
    update_label = f"Importado em {now_sp} · via upload manual"
else:
    try:
        import subprocess
        r = subprocess.run(["git","log","-1","--format=%ci","--","semanas_anteriores.csv","data/semanas_anteriores.csv"],
                           capture_output=True, text=True, cwd=".")
        if r.stdout.strip():
            gd = datetime.fromisoformat(r.stdout.strip()).astimezone(ZoneInfo("America/Sao_Paulo"))
            update_label = f"Atualizado em {gd.strftime('%d/%m/%Y %H:%M')} · via Databricks"
        else:
            update_label = "via Databricks"
    except:
        update_label = "via Databricks"

# ── NAV BAR ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nav-bar">
  <span class="nav-title">Monitoramento de Repasse do Diesel</span>
  <span class="nav-badge">
    <span class="nav-dot"></span>
    {update_label}
  </span>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(["Resumo executivo","Semanas anteriores","16–22/03","23–29/03","Páscoa","Tiradentes","📋 Plano de ação"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — RESUMO EXECUTIVO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    loaded = {k:v for k,v in {"Sem. ant.":df_sem,"16–22/03":df_s16,"23–29/03":df_s23,"Páscoa":df_pas,"Tiradentes":df_tir}.items() if v is not None}
    if not loaded:
        st.info("Carregue os arquivos CSV para gerar a análise.")
    else:
        all_records = []
        period_stats = []
        for name, df in loaded.items():
            e = enrich(df)
            all_records.append(e)
            avg = e["pct"].mean()
            period_stats.append({"Período": name, "avg": avg, "cls": classify(avg)})
        all_df = pd.concat(all_records, ignore_index=True)

        wr = all_df[all_df["pct"] >= 5]
        ac = (all_df["cls"] == "alto").sum()
        mc = (all_df["cls"] == "mod").sum()
        ag = all_df["pct"].mean()
        pr = len(wr) / len(all_df) * 100

        verdict = ("Sinais expressivos de repasse identificados — múltiplos trechos com variações acima de 15%." if ac > 3
                   else "Repasse parcial em andamento — parte significativa dos trechos já apresenta elevações tarifárias." if pr > 40
                   else "Repasse limitado até o momento — maioria dos trechos ainda sem variação significativa.")

        st.markdown(f"""
        <div class="verdict-card">
          <div class="verdict-label">Diagnóstico — {datetime.now().strftime('%d/%m/%Y')}</div>
          <div class="verdict-title">{verdict}</div>
          <div class="verdict-body">De {len(all_df)} observações em {len(loaded)} período(s), {len(wr)} ({pr:.0f}%) apresentam variação ≥5%. Variação média geral: {ag:+.1f}%.</div>
        </div>
        """, unsafe_allow_html=True)

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Variação média geral", f"{ag:+.1f}%", "sobre a semana-base")
        k2.metric("Com repasse ≥5%", f"{pr:.0f}%", f"{len(wr)} de {len(all_df)}")
        k3.metric("Muito relevante ≥15%", str(ac), "registros")
        k4.metric("Moderado 10–15%", str(mc), "registros")

        st.markdown("---")
        st.markdown('<p class="section-title">Variação média por período</p>', unsafe_allow_html=True)

        ps_df = pd.DataFrame(period_stats)
        fig = go.Figure(go.Bar(
            x=ps_df["Período"], y=ps_df["avg"].round(1),
            marker_color=[color_for(c) for c in ps_df["cls"]],
            text=[f"{v:+.1f}%" for v in ps_df["avg"]], textposition="outside",
        ))
        fig.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          yaxis=dict(ticksuffix="%", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                          xaxis=dict(showgrid=False), showlegend=False,
                          font=dict(family="DM Sans, sans-serif", size=12))
        st.plotly_chart(fig, use_container_width=True)

        top = (all_df[all_df["pct"] >= 5].groupby("trecho_unico")
               .agg(pct=("pct","mean"), trecho_fmt=("trecho_fmt","first"))
               .reset_index().sort_values("pct", ascending=False).head(8))
        if not top.empty:
            st.markdown("---")
            st.markdown('<p class="section-title">Trechos com maior sinal de repasse</p>', unsafe_allow_html=True)
            top["cls"] = top["pct"].apply(classify)
            top["Variação"] = top["pct"].apply(lambda v: f"{v:+.1f}%")
            top["Classificação"] = top["cls"].apply(lambda c: {"alto":"Muito relevante","mod":"Moderado","leve":"Leve"}.get(c,"–"))
            st.dataframe(top[["trecho_fmt","Variação","Classificação"]].rename(columns={"trecho_fmt":"Trecho"}),
                        use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SEMANAS ANTERIORES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    if df_sem is None:
        st.info("Carregue o arquivo 'Semanas anteriores'.")
    else:
        e = enrich(df_sem)
        st.markdown('<p class="section-title">Variação percentual por trecho</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Comparação com a semana-base de 23/02–01/03/2026.</p>', unsafe_allow_html=True)
        st.plotly_chart(plotly_bar(e.sort_values("pct", ascending=True)), use_container_width=True)
        st.markdown("---")
        f = filter_chips("sem")
        show = filter_df(e, f).sort_values("pct", ascending=False)
        show["Variação"] = show["pct"].apply(fmt_var)
        show["Preço ref."]  = show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        show["Preço atual"] = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
        show["Classificação"] = show["cls"].apply(lambda c: {"alto":"Muito relevante","mod":"Moderado","leve":"Leve","pos":"Leve positivo","neg":"Sem repasse"}.get(c,"–"))
        st.dataframe(show[["trecho_fmt","Preço ref.","Preço atual","Variação","Classificação"]].rename(columns={"trecho_fmt":"Trecho"}),
                    use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER — SEMANA DETALHE
# ══════════════════════════════════════════════════════════════════════════════
def render_semana_detalhe(df, title, tab_key):
    if df is None:
        st.info(f"Carregue o arquivo '{title}'.")
        return
    e = enrich(df)
    summary = (e.groupby("trecho_unico")
                .agg(pct=("pct","mean"), trecho_fmt=("trecho_fmt","first"),
                     media_preco_atual=("media_preco_atual","mean"),
                     media_preco_referencia=("media_preco_referencia","mean"))
                .reset_index())
    summary["cls"] = summary["pct"].apply(classify)

    st.markdown(f'<p class="section-title">Semana {title}</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Preços por dia e antecedência vs. semana-base.</p>', unsafe_allow_html=True)
    st.plotly_chart(plotly_bar(summary.sort_values("pct", ascending=True)), use_container_width=True)
    st.markdown("---")
    f = filter_chips(tab_key)
    show = filter_df(summary, f).sort_values("pct", ascending=False)
    show["Variação"]  = show["pct"].apply(fmt_var)
    show["Preço ref."]  = show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
    show["Preço médio"] = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
    show["Classificação"] = show["cls"].apply(lambda c: {"alto":"Muito relevante","mod":"Moderado","leve":"Leve","pos":"Leve positivo","neg":"Sem repasse"}.get(c,"–"))
    st.dataframe(show[["trecho_fmt","Preço ref.","Preço médio","Variação","Classificação"]].rename(columns={"trecho_fmt":"Trecho"}),
                use_container_width=True, hide_index=True)
    with st.expander("Ver detalhamento por dia e antecedência"):
        det = filter_df(e, f).sort_values(["trecho_unico","data"])
        det["Variação"]  = det["pct"].apply(fmt_var)
        det["Preço ref."]  = det["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        det["Preço atual"] = det["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
        det["Antec."] = det["antecedencia"].apply(lambda v: f"D{int(v)}" if pd.notna(v) else "–")
        det["Classificação"] = det["cls"].apply(lambda c: {"alto":"Muito relevante","mod":"Moderado","leve":"Leve","pos":"Leve positivo","neg":"Sem repasse"}.get(c,"–"))
        st.dataframe(det[["trecho_fmt","data","Antec.","Preço ref.","Preço atual","Variação","Classificação"]]
                    .rename(columns={"trecho_fmt":"Trecho","data":"Data"}),
                    use_container_width=True, hide_index=True)

with tabs[2]: render_semana_detalhe(df_s16, "16 a 22 de março", "s16")
with tabs[3]: render_semana_detalhe(df_s23, "23 a 29 de março", "s23")

# ══════════════════════════════════════════════════════════════════════════════
# HELPER — FERIADO
# ══════════════════════════════════════════════════════════════════════════════
def render_feriado(df, nome, dias, ref_nome, tab_key):
    if df is None:
        st.info(f"Carregue o arquivo '{nome}'.")
        return
    e = enrich(df)
    e["Sentido"] = e["data"].apply(lambda d: "Ida" if ("02" in str(d) or "17" in str(d)) else "Volta")

    st.markdown(f'<p class="section-title">Feriado de {nome}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">Dias de maior movimento: {dias}. Referência: {ref_nome}.</p>', unsafe_allow_html=True)

    e["trecho_sentido"] = e["trecho_fmt"] + " (" + e["Sentido"] + ")"
    st.plotly_chart(plotly_bar(e.sort_values("pct", ascending=True), y_col="trecho_sentido"), use_container_width=True)
    st.markdown("---")
    f = filter_chips(tab_key)
    show = filter_df(e, f).sort_values("pct", ascending=False)
    show["Variação"]       = show["pct"].apply(fmt_var)
    show["Ref. (Carnaval)"]= show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
    show["Preço atual"]    = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
    show["Antec."]         = show["antecedencia"].apply(lambda v: f"D{int(v)}" if pd.notna(v) else "–")
    show["Classificação"]  = show["cls"].apply(lambda c: {"alto":"Muito relevante","mod":"Moderado","leve":"Leve","pos":"Leve positivo","neg":"Sem repasse"}.get(c,"–"))
    st.dataframe(show[["trecho_fmt","data","Sentido","Antec.","Ref. (Carnaval)","Preço atual","Variação","Classificação"]]
                .rename(columns={"trecho_fmt":"Trecho","data":"Data"}),
                use_container_width=True, hide_index=True)

with tabs[4]: render_feriado(df_pas, "Páscoa",     "02/04 (ida) e 05/04 (volta)", "Carnaval", "pas")
with tabs[5]: render_feriado(df_tir, "Tiradentes", "17/04 (ida) e 21/04 (volta)", "Carnaval", "tir")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PLANO DE AÇÃO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
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

    criticos = get_criticos(df_sem, df_s16, df_s23, df_pas, df_tir)

    st.markdown('<p class="section-title">Plano de ação — trechos críticos</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Top 10 trechos com maior sinal de repasse (variação média ≥5%). Preencha e salve cada linha.</p>', unsafe_allow_html=True)

    if criticos.empty:
        st.info("Carregue os arquivos CSV para gerar o plano.")
    else:
        if "plano" not in st.session_state:
            st.session_state.plano = {}

        STATUS = ["Aberto", "Em andamento", "Monitorando", "Concluído"]
        EMOJI  = {"Aberto":"🔴","Em andamento":"🟡","Monitorando":"🔵","Concluído":"🟢"}

        for _, row in criticos.iterrows():
            t   = row["trecho_unico"]
            pct = row["pct"]
            p   = st.session_state.plano.get(t, {})
            lbl = "Muito relevante" if pct >= 15 else "Moderado" if pct >= 10 else "Leve"
            ico = EMOJI.get(p.get("status","Aberto"), "🔴")

            with st.expander(f"{ico}  {fmt_trecho(t)}  ·  {pct:+.1f}%  ·  {lbl}", expanded=False):
                c1, c2, c3 = st.columns([2, 1.5, 1.5])
                with c1:
                    resp = st.text_input("Responsável", value=p.get("responsavel",""), key=f"r_{t}")
                with c2:
                    prazo_val = None
                    if p.get("prazo"):
                        try: prazo_val = date.fromisoformat(p["prazo"])
                        except: pass
                    prazo = st.date_input("Prazo", value=prazo_val, key=f"d_{t}")
                with c3:
                    idx = STATUS.index(p.get("status","Aberto"))
                    status = st.selectbox("Status", STATUS, index=idx, key=f"s_{t}")
                acao = st.text_area("Ação / observações", value=p.get("acao",""), key=f"a_{t}", height=75)
                if st.button("Salvar", key=f"btn_{t}", type="primary"):
                    st.session_state.plano[t] = {
                        "responsavel": resp,
                        "prazo": prazo.isoformat() if prazo else "",
                        "status": status,
                        "acao": acao,
                    }
                    st.success("Salvo!", icon="✅")

        st.markdown("---")
        st.markdown("#### Resumo do plano")
        rows = []
        for _, row in criticos.iterrows():
            t = row["trecho_unico"]
            p = st.session_state.plano.get(t, {})
            rows.append({
                "Trecho":      fmt_trecho(t),
                "Variação":    f"{row['pct']:+.1f}%",
                "Responsável": p.get("responsavel","—"),
                "Prazo":       p.get("prazo","—"),
                "Status":      p.get("status","Aberto"),
                "Ação":        p.get("acao","—"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        csv_bytes = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar plano como CSV", csv_bytes, "plano_acao_diesel.csv", "text/csv")

# ── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:20px;font-size:12px;color:#9C9A93;border-top:1px solid rgba(0,0,0,0.07);background:white;margin-top:32px">
  Referência base: semana 23/02–01/03/2026 · Reajuste do diesel analisado pós-16/03/2026
</div>
""", unsafe_allow_html=True)
