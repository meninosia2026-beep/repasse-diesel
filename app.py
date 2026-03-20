import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Repasse do Diesel",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── ESTILOS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #F7F5F0; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }
    h1 { font-size: 1.7rem !important; font-weight: 600 !important; }
    h2 { font-size: 1.2rem !important; font-weight: 600 !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; }
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 10px;
        padding: 16px 18px;
    }
    .badge-alto  { background:#FAE8E4; color:#C8402A; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-mod   { background:#FDF3DC; color:#B07A10; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-leve  { background:#E3F2E9; color:#2E6B40; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-neg   { background:#EDECE9; color:#4A4A46; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .verdict-box {
        background: white;
        border-left: 4px solid #C8402A;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def variation(atual, ref):
    if ref and ref != 0:
        return ((atual - ref) / ref) * 100
    return None

def classify(pct):
    if pct is None:
        return None
    if pct >= 15: return "alto"
    if pct >= 10: return "mod"
    if pct >= 5:  return "leve"
    if pct > 0:   return "pos"
    return "neg"

CLASS_LABELS = {
    "alto": "Muito relevante",
    "mod":  "Moderado",
    "leve": "Leve",
    "pos":  "Leve positivo",
    "neg":  "Sem repasse",
    None:   "–",
}
CLASS_COLORS = {
    "alto": "#C8402A",
    "mod":  "#B07A10",
    "leve": "#2E6B40",
    "pos":  "#2E6B40",
    "neg":  "#9C9A93",
}

def badge_html(cls):
    label = CLASS_LABELS.get(cls, "–")
    css   = {"alto":"badge-alto","mod":"badge-mod","leve":"badge-leve","pos":"badge-leve","neg":"badge-neg"}.get(cls,"badge-neg")
    return f'<span class="{css}">{label}</span>'

def trecho_short(t):
    parts = t.split("-")
    cities = [p.capitalize() for p in parts if len(p) > 2]
    return " › ".join(cities)

def enrich(df):
    df = df.copy()
    df["pct"] = df.apply(lambda r: variation(r["media_preco_atual"], r["media_preco_referencia"]), axis=1)
    df["cls"] = df["pct"].apply(classify)
    df["cls_label"] = df["cls"].map(CLASS_LABELS)
    df["trecho_fmt"] = df["trecho_unico"].apply(trecho_short)
    return df

def bar_chart(df_sorted, x_col="pct", y_col="trecho_fmt", height=None):
    colors = [CLASS_COLORS.get(c, "#9C9A93") for c in df_sorted["cls"]]
    h = height or max(300, len(df_sorted) * 38)
    fig = go.Figure(go.Bar(
        x=df_sorted[x_col].round(1),
        y=df_sorted[y_col],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in df_sorted[x_col]],
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(
        height=h,
        margin=dict(l=0, r=60, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)",
                   ticksuffix="%", zeroline=True, zerolinecolor="rgba(0,0,0,0.15)"),
        yaxis=dict(showgrid=False),
        font=dict(family="sans-serif", size=12),
        showlegend=False,
    )
    return fig

def filter_df(df, f):
    if f == "Todos":          return df
    if f == "Com repasse":    return df[df["pct"] >= 5]
    if f == "Muito relevante": return df[df["cls"] == "alto"]
    if f == "Moderado":       return df[df["cls"] == "mod"]
    if f == "Leve":           return df[df["cls"].isin(["leve", "pos"])]
    return df

def render_table(df, cols_map):
    """cols_map: {col_name: display_name}"""
    show = df[list(cols_map.keys())].copy()
    show.columns = list(cols_map.values())
    st.dataframe(show, use_container_width=True, hide_index=True)

# ── SIDEBAR — UPLOAD ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Carregar arquivos CSV")
    st.caption("Substitua qualquer arquivo para atualizar a análise automaticamente.")

    up_semanas     = st.file_uploader("Semanas anteriores",  type="csv", key="up_sem")
    up_s16         = st.file_uploader("Semana 16–22/03",     type="csv", key="up_s16")
    up_s23         = st.file_uploader("Semana 23–29/03",     type="csv", key="up_s23")
    up_pascoa      = st.file_uploader("Feriado Páscoa",      type="csv", key="up_pas")
    up_tiradentes  = st.file_uploader("Feriado Tiradentes",  type="csv", key="up_tir")

    st.divider()
    st.caption("**Referência base:** semana 23/02–01/03/2026")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_default(name):
    import os
    path = os.path.join("data", name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def load_file(upload, default_name):
    if upload:
        return pd.read_csv(upload)
    return load_default(default_name)

df_semanas    = load_file(up_semanas,    "semanas_anteriores.csv")
df_s16        = load_file(up_s16,        "semana_16_a_22.csv")
df_s23        = load_file(up_s23,        "semana_23_a_29.csv")
df_pascoa     = load_file(up_pascoa,     "feriado_pascoa.csv")
df_tiradentes = load_file(up_tiradentes, "feriado_tiradentes.csv")

loaded = {k: v for k, v in {
    "Sem. anteriores": df_semanas,
    "16–22/03": df_s16,
    "23–29/03": df_s23,
    "Páscoa": df_pascoa,
    "Tiradentes": df_tiradentes,
}.items() if v is not None}

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🚌 Monitoramento de Repasse do Diesel")
st.caption("Transporte rodoviário de passageiros — Comparativo pós-reajuste | Ref. base: 23/02–01/03/2026")
st.divider()

if not loaded:
    st.info("⬅️ Use a barra lateral para carregar os arquivos CSV e gerar a análise.")
    st.stop()

# ── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📋 Resumo executivo", "📅 Sem. anteriores", "📅 16–22/03", "📅 23–29/03", "🐣 Páscoa", "🏛️ Tiradentes"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 0 — RESUMO EXECUTIVO
# ════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    all_records = []
    period_stats = []

    for period_name, df in loaded.items():
        e = enrich(df)
        all_records.append(e)
        avg = e["pct"].mean()
        period_stats.append({"Período": period_name, "Variação média": avg, "cls": classify(avg)})

    all_df = pd.concat(all_records, ignore_index=True)

    with_repasse  = all_df[all_df["pct"] >= 5]
    alto_count    = (all_df["cls"] == "alto").sum()
    mod_count     = (all_df["cls"] == "mod").sum()
    avg_geral     = all_df["pct"].mean()
    pct_repasse   = len(with_repasse) / len(all_df) * 100

    # Verdict
    if alto_count > 3:
        verdict = "Sinais expressivos de repasse identificados — múltiplos trechos com variações acima de 15%."
    elif pct_repasse > 40:
        verdict = "Repasse parcial em andamento — parte significativa dos trechos já apresenta elevações tarifárias."
    else:
        verdict = "Repasse limitado até o momento — maioria dos trechos ainda sem variação significativa."

    st.markdown(f"""
    <div class="verdict-box">
        <div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#C8402A;margin-bottom:8px">
            Diagnóstico
        </div>
        <div style="font-size:18px;font-weight:600;margin-bottom:10px">{verdict}</div>
        <div style="font-size:13px;color:#6B6963">
            De {len(all_df)} observações em {len(loaded)} período(s), {len(with_repasse)} ({pct_repasse:.0f}%)
            apresentam variação positiva acima de 5%. Variação média geral: {avg_geral:+.1f}%.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Variação média geral",  f"{avg_geral:+.1f}%",  "sobre a semana-base")
    c2.metric("Obs. com repasse ≥5%",  f"{pct_repasse:.0f}%", f"{len(with_repasse)} de {len(all_df)}")
    c3.metric("Muito relevante ≥15%",  f"{alto_count}",       "registros")
    c4.metric("Moderado 10–15%",       f"{mod_count}",        "registros")

    st.markdown("---")

    # Gráfico por período
    st.markdown("#### Variação média por período")
    ps_df = pd.DataFrame(period_stats)
    ps_df["cor"] = ps_df["cls"].map(CLASS_COLORS).fillna("#9C9A93")
    fig_period = go.Figure(go.Bar(
        x=ps_df["Período"],
        y=ps_df["Variação média"].round(1),
        marker_color=ps_df["cor"].tolist(),
        text=[f"{v:+.1f}%" for v in ps_df["Variação média"]],
        textposition="outside",
    ))
    fig_period.update_layout(
        height=280, margin=dict(l=0,r=0,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(ticksuffix="%", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        xaxis=dict(showgrid=False),
        showlegend=False,
        font=dict(size=12),
    )
    st.plotly_chart(fig_period, use_container_width=True)

    st.markdown("---")

    # Top trechos com repasse
    st.markdown("#### Trechos com maior sinal de repasse")
    top = (all_df[all_df["pct"] >= 5]
           .groupby("trecho_unico")
           .agg(pct=("pct","mean"), trecho_fmt=("trecho_fmt","first"))
           .reset_index()
           .sort_values("pct", ascending=False)
           .head(8))

    if top.empty:
        st.info("Nenhum trecho com variação ≥ 5% identificado.")
    else:
        top["cls"] = top["pct"].apply(classify)
        top["Classificação"] = top["cls"].map(CLASS_LABELS)
        top["Variação média"] = top["pct"].apply(lambda v: f"{v:+.1f}%")
        st.dataframe(
            top[["trecho_fmt","Variação média","Classificação"]].rename(columns={"trecho_fmt":"Trecho"}),
            use_container_width=True, hide_index=True
        )

    # Legenda
    st.markdown("---")
    st.caption(
        "**Legenda:** "
        "🔴 Muito relevante ≥15%  &nbsp;|&nbsp;  "
        "🟡 Moderado 10–15%  &nbsp;|&nbsp;  "
        "🟢 Leve 5–10%  &nbsp;|&nbsp;  "
        "⚪ Sem repasse <5%"
    )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — SEMANAS ANTERIORES
# ════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    if df_semanas is None:
        st.info("⬅️ Carregue o arquivo 'Semanas anteriores' na barra lateral.")
    else:
        e = enrich(df_semanas)
        st.markdown("#### Variação percentual por trecho")
        st.caption("Comparação com a semana-base de 23/02–01/03/2026")

        sorted_e = e.sort_values("pct", ascending=True)
        st.plotly_chart(bar_chart(sorted_e), use_container_width=True)

        st.markdown("#### Tabela detalhada")
        filtro = st.radio("Filtrar por classificação:", ["Todos","Com repasse","Muito relevante","Moderado","Leve"],
                          horizontal=True, key="f_sem")
        show = filter_df(e, filtro).sort_values("pct", ascending=False)
        show["Variação"] = show["pct"].apply(lambda v: f"{v:+.1f}%" if v is not None else "–")
        show["Preço ref."] = show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        show["Preço atual"] = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
        st.dataframe(
            show[["trecho_fmt","Preço ref.","Preço atual","Variação","cls_label"]]
                .rename(columns={"trecho_fmt":"Trecho","cls_label":"Classificação"}),
            use_container_width=True, hide_index=True
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — SEMANA 16-22
# ════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    if df_s16 is None:
        st.info("⬅️ Carregue o arquivo 'Semana 16–22/03' na barra lateral.")
    else:
        e = enrich(df_s16)
        st.markdown("#### Variação média por trecho — semana 16 a 22/03")
        st.caption("Comparação com a mesma antecedência na semana-base")

        summary = (e.groupby("trecho_unico")
                    .agg(pct=("pct","mean"), trecho_fmt=("trecho_fmt","first"),
                         media_preco_atual=("media_preco_atual","mean"),
                         media_preco_referencia=("media_preco_referencia","mean"))
                    .reset_index())
        summary["cls"] = summary["pct"].apply(classify)
        summary["cls_label"] = summary["cls"].map(CLASS_LABELS)

        sorted_s = summary.sort_values("pct", ascending=True)
        st.plotly_chart(bar_chart(sorted_s), use_container_width=True)

        filtro = st.radio("Filtrar:", ["Todos","Com repasse","Muito relevante","Moderado","Leve"],
                          horizontal=True, key="f_s16")
        show = filter_df(summary, filtro).sort_values("pct", ascending=False)
        show["Variação"] = show["pct"].apply(lambda v: f"{v:+.1f}%")
        show["Preço ref."] = show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        show["Preço médio"] = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")

        st.markdown("**Resumo por trecho (média semanal)**")
        st.dataframe(
            show[["trecho_fmt","Preço ref.","Preço médio","Variação","cls_label"]]
                .rename(columns={"trecho_fmt":"Trecho","cls_label":"Classificação"}),
            use_container_width=True, hide_index=True
        )

        st.markdown("**Detalhamento por dia e antecedência**")
        det = filter_df(e, filtro).sort_values(["trecho_unico","data"])
        det["Variação"] = det["pct"].apply(lambda v: f"{v:+.1f}%")
        det["Preço ref."] = det["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        det["Preço atual"] = det["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
        det["Antec."] = det["antecedencia"].apply(lambda v: f"D{int(v)}" if pd.notna(v) else "–")
        st.dataframe(
            det[["trecho_fmt","data","Antec.","Preço ref.","Preço atual","Variação","cls_label"]]
                .rename(columns={"trecho_fmt":"Trecho","data":"Data","cls_label":"Classificação"}),
            use_container_width=True, hide_index=True
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — SEMANA 23-29
# ════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    if df_s23 is None:
        st.info("⬅️ Carregue o arquivo 'Semana 23–29/03' na barra lateral.")
    else:
        e = enrich(df_s23)
        st.markdown("#### Variação média por trecho — semana 23 a 29/03")
        st.caption("Comparação com a mesma antecedência na semana-base")

        summary = (e.groupby("trecho_unico")
                    .agg(pct=("pct","mean"), trecho_fmt=("trecho_fmt","first"),
                         media_preco_atual=("media_preco_atual","mean"),
                         media_preco_referencia=("media_preco_referencia","mean"))
                    .reset_index())
        summary["cls"] = summary["pct"].apply(classify)
        summary["cls_label"] = summary["cls"].map(CLASS_LABELS)

        sorted_s = summary.sort_values("pct", ascending=True)
        st.plotly_chart(bar_chart(sorted_s), use_container_width=True)

        filtro = st.radio("Filtrar:", ["Todos","Com repasse","Muito relevante","Moderado","Leve"],
                          horizontal=True, key="f_s23")
        show = filter_df(summary, filtro).sort_values("pct", ascending=False)
        show["Variação"] = show["pct"].apply(lambda v: f"{v:+.1f}%")
        show["Preço ref."] = show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        show["Preço médio"] = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")

        st.markdown("**Resumo por trecho (média semanal)**")
        st.dataframe(
            show[["trecho_fmt","Preço ref.","Preço médio","Variação","cls_label"]]
                .rename(columns={"trecho_fmt":"Trecho","cls_label":"Classificação"}),
            use_container_width=True, hide_index=True
        )

        st.markdown("**Detalhamento por dia e antecedência**")
        det = filter_df(e, filtro).sort_values(["trecho_unico","data"])
        det["Variação"] = det["pct"].apply(lambda v: f"{v:+.1f}%")
        det["Preço ref."] = det["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        det["Preço atual"] = det["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
        det["Antec."] = det["antecedencia"].apply(lambda v: f"D{int(v)}" if pd.notna(v) else "–")
        st.dataframe(
            det[["trecho_fmt","data","Antec.","Preço ref.","Preço atual","Variação","cls_label"]]
                .rename(columns={"trecho_fmt":"Trecho","data":"Data","cls_label":"Classificação"}),
            use_container_width=True, hide_index=True
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — PÁSCOA
# ════════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    if df_pascoa is None:
        st.info("⬅️ Carregue o arquivo 'Feriado Páscoa' na barra lateral.")
    else:
        e = enrich(df_pascoa)
        e["Sentido"] = e["data"].apply(lambda d: "Ida" if "02" in str(d) else "Volta")
        st.markdown("#### Páscoa vs. Carnaval")
        st.caption("Dias de maior movimento: Ida 02/04, Volta 05/04 | Ref.: Carnaval (Ida 13/02, Volta 17/02)")

        sorted_e = e.sort_values("pct", ascending=True)
        sorted_e["trecho_sentido"] = sorted_e["trecho_fmt"] + " (" + sorted_e["Sentido"] + ")"
        fig = bar_chart(sorted_e, y_col="trecho_sentido")
        st.plotly_chart(fig, use_container_width=True)

        filtro = st.radio("Filtrar:", ["Todos","Com repasse","Muito relevante","Moderado","Leve"],
                          horizontal=True, key="f_pas")
        show = filter_df(e, filtro).sort_values("pct", ascending=False)
        show["Variação"] = show["pct"].apply(lambda v: f"{v:+.1f}%")
        show["Ref. Carnaval"] = show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        show["Preço Páscoa"] = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
        show["Antec."] = show["antecedencia"].apply(lambda v: f"D{int(v)}" if pd.notna(v) else "–")
        st.dataframe(
            show[["trecho_fmt","data","Sentido","Antec.","Ref. Carnaval","Preço Páscoa","Variação","cls_label"]]
                .rename(columns={"trecho_fmt":"Trecho","data":"Data","cls_label":"Classificação"}),
            use_container_width=True, hide_index=True
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — TIRADENTES
# ════════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    if df_tiradentes is None:
        st.info("⬅️ Carregue o arquivo 'Feriado Tiradentes' na barra lateral.")
    else:
        e = enrich(df_tiradentes)
        e["Sentido"] = e["data"].apply(lambda d: "Ida" if "17" in str(d) else "Volta")
        st.markdown("#### Tiradentes vs. Carnaval")
        st.caption("Dias de maior movimento: Ida 17/04, Volta 21/04 | Ref.: Carnaval (Ida 13/02, Volta 17/02)")

        sorted_e = e.sort_values("pct", ascending=True)
        sorted_e["trecho_sentido"] = sorted_e["trecho_fmt"] + " (" + sorted_e["Sentido"] + ")"
        fig = bar_chart(sorted_e, y_col="trecho_sentido")
        st.plotly_chart(fig, use_container_width=True)

        filtro = st.radio("Filtrar:", ["Todos","Com repasse","Muito relevante","Moderado","Leve"],
                          horizontal=True, key="f_tir")
        show = filter_df(e, filtro).sort_values("pct", ascending=False)
        show["Variação"] = show["pct"].apply(lambda v: f"{v:+.1f}%")
        show["Ref. Carnaval"] = show["media_preco_referencia"].apply(lambda v: f"R$ {v:.2f}")
        show["Preço Tiradentes"] = show["media_preco_atual"].apply(lambda v: f"R$ {v:.2f}")
        show["Antec."] = show["antecedencia"].apply(lambda v: f"D{int(v)}" if pd.notna(v) else "–")
        st.dataframe(
            show[["trecho_fmt","data","Sentido","Antec.","Ref. Carnaval","Preço Tiradentes","Variação","cls_label"]]
                .rename(columns={"trecho_fmt":"Trecho","data":"Data","cls_label":"Classificação"}),
            use_container_width=True, hide_index=True
        )
