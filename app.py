import streamlit as st
import pandas as pd
import os
from datetime import datetime
from zoneinfo import ZoneInfo


st.set_page_config(
    page_title="Inteligência de Mercado",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > .main { padding: 0 !important; }
    [data-testid="stHeader"] { display: none; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

with st.expander("📂 Atualizar arquivos CSV", expanded=False):
    st.caption("Substitua qualquer arquivo para atualizar a análise.")
    col1, col2, col3 = st.columns(3)
    with col1:
        up_semanas    = st.file_uploader("Semanas anteriores",  type="csv", key="up_sem")
        up_s16        = st.file_uploader("Semana 16-22/03",     type="csv", key="up_s16")
    with col2:
        up_s23        = st.file_uploader("Semana 23-29/03",     type="csv", key="up_s23")
        up_pascoa     = st.file_uploader("Feriado Páscoa",      type="csv", key="up_pas")
    with col3:
        up_tiradentes = st.file_uploader("Feriado Tiradentes",  type="csv", key="up_tir")

def load_file(upload, default_name):
    if upload:
        return pd.read_csv(upload)
    for folder in ["data", "."]:
        path = os.path.join(folder, default_name)
        if os.path.exists(path):
            return pd.read_csv(path)
    return None

df_semanas    = load_file(up_semanas,    "semanas_anteriores.csv")
df_s16        = load_file(up_s16,        "semana_16_a_22.csv")
df_s23        = load_file(up_s23,        "semana_23_a_29.csv")
df_pascoa     = load_file(up_pascoa,     "feriado_pascoa.csv")
df_tiradentes = load_file(up_tiradentes, "feriado_tiradentes.csv")

any_upload = any([up_semanas, up_s16, up_s23, up_pascoa, up_tiradentes])
if any_upload:
    now_sp = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
    update_label = f"Importado em {now_sp} · via upload manual"
else:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", "feriado_tiradentes.csv", "data/feriado_tiradentes.csv"],
            capture_output=True, text=True, cwd="."
        )
        if result.stdout.strip():
            from datetime import datetime as dt
            git_date = dt.fromisoformat(result.stdout.strip())
            git_date_sp = git_date.astimezone(ZoneInfo("America/Sao_Paulo"))
            update_label = f"Atualizado em {git_date_sp.strftime('%d/%m/%Y %H:%M')} · via Databricks"
        else:
            update_label = "via Databricks"
    except Exception:
        update_label = "via Databricks"

def df_to_json(df):
    if df is None:
        return "null"
    return df.to_json(orient="records")

data_js = f"""
const INJECTED = {{
  semanas:    {df_to_json(df_semanas)},
  s16:        {df_to_json(df_s16)},
  s23:        {df_to_json(df_s23)},
  pascoa:     {df_to_json(df_pascoa)},
  tiradentes: {df_to_json(df_tiradentes)},
}};
const UPDATE_LABEL = "{update_label}";
"""

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {{
    --bg:#F7F5F0;--surface:#fff;--surface2:#F0EDE6;
    --border:rgba(0,0,0,.08);--border-strong:rgba(0,0,0,.15);
    --text:#1A1A18;--muted:#6B6963;--faint:#9C9A93;
    --up:#C8402A;--up-l:#FAE8E4;
    --down:#2E6B40;--down-l:#E3F2E9;
    --warn:#B07A10;--warn-l:#FDF3DC;
    --neutral:#4A4A46;--neutral-l:#EDECE9;
    --r:10px;--rl:16px;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.6}}
  .header{{background:var(--surface);border-bottom:1px solid var(--border);padding:22px 28px 18px}}
  .title{{font-family:'DM Serif Display',serif;font-size:22px;font-weight:400;letter-spacing:-.3px}}
  .subtitle{{font-size:13px;color:var(--muted);margin-top:3px}}
  .tabs{{background:var(--surface);border-bottom:1px solid var(--border);padding:0 28px;display:flex;overflow-x:auto}}
  .tab{{padding:12px 16px;font-size:13px;font-weight:500;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}}
  .tab:hover{{color:var(--text)}}
  .tab.active{{color:var(--text);border-bottom-color:var(--up)}}
  .main{{padding:24px 28px}}
  .panel{{display:none}}.panel.active{{display:block}}

  /* SIGNAL CARD */
  .signal{{background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--up);border-radius:var(--rl);padding:20px 24px;margin-bottom:18px}}
  .signal.down{{border-left-color:var(--down)}}
  .signal.neutral{{border-left-color:var(--warn)}}
  .signal-lbl{{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--up);margin-bottom:7px}}
  .signal.down .signal-lbl{{color:var(--down)}}
  .signal.neutral .signal-lbl{{color:var(--warn)}}
  .signal-title{{font-family:'DM Serif Display',serif;font-size:18px;margin-bottom:9px;line-height:1.35}}
  .signal-body{{font-size:13px;color:var(--muted);line-height:1.7}}

  /* KPIs */
  .kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-bottom:18px}}
  .kpi{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px}}
  .kpi-lbl{{font-size:11px;color:var(--faint);text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px}}
  .kpi-val{{font-size:21px;font-weight:600;line-height:1;margin-bottom:3px}}
  .kpi-desc{{font-size:12px;color:var(--muted)}}
  .kpi.up   .kpi-val{{color:var(--up)}}
  .kpi.down .kpi-val{{color:var(--down)}}
  .kpi.warn .kpi-val{{color:var(--warn)}}

  /* CARDS GRID */
  .ig{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:18px}}
  .ic{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px}}
  .ic h4{{font-size:13px;font-weight:600;margin-bottom:6px}}
  .ic p{{font-size:13px;color:var(--muted);line-height:1.6}}

  /* CHART / TABLE CONTAINERS */
  .cc{{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);padding:20px;margin-bottom:16px}}
  .cc h3{{font-size:14px;font-weight:600;margin-bottom:3px}}
  .cdesc{{font-size:12px;color:var(--muted);margin-bottom:16px}}
  .cwrap{{position:relative;width:100%}}
  .tc{{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);overflow:hidden;margin-bottom:16px}}
  .th2{{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}}
  .th2 h3{{font-size:14px;font-weight:600}}

  /* FILTERS */
  .fr{{display:flex;gap:5px;flex-wrap:wrap}}
  .fc{{padding:3px 10px;border-radius:20px;border:1px solid var(--border-strong);font-size:12px;cursor:pointer;transition:all .15s;background:var(--surface);color:var(--muted);font-family:'DM Sans',sans-serif}}
  .fc:hover{{background:var(--surface2)}}
  .fc.active{{background:var(--text);color:#fff;border-color:var(--text)}}
  .fc.cu{{background:var(--up-l);color:var(--up);border-color:rgba(200,64,42,.2)}}
  .fc.cu.active{{background:var(--up);color:#fff}}
  .fc.cd{{background:var(--down-l);color:var(--down);border-color:rgba(46,107,64,.2)}}
  .fc.cd.active{{background:var(--down);color:#fff}}
  .fc.cw{{background:var(--warn-l);color:var(--warn);border-color:rgba(176,122,16,.2)}}
  .fc.cw.active{{background:var(--warn);color:#fff}}

  /* TABLE */
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  thead th{{padding:9px 14px;text-align:left;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--faint);background:var(--surface2);border-bottom:1px solid var(--border)}}
  tbody tr{{border-bottom:1px solid var(--border);transition:background .1s}}
  tbody tr:last-child{{border-bottom:none}}
  tbody tr:hover{{background:var(--surface2)}}
  tbody td{{padding:9px 14px}}
  .tt{{font-weight:500}}

  /* BADGES */
  .badge{{display:inline-flex;align-items:center;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;white-space:nowrap}}
  .b-alta   {{background:var(--up-l);color:var(--up)}}
  .b-queda  {{background:var(--down-l);color:var(--down)}}
  .b-instavel{{background:var(--warn-l);color:var(--warn)}}
  .b-estavel{{background:var(--neutral-l);color:var(--neutral)}}

  /* VAR COLORS */
  .vu{{color:var(--up);font-weight:600}}
  .vd{{color:var(--down);font-weight:600}}
  .vf{{color:var(--muted)}}

  .stitle{{font-family:'DM Serif Display',serif;font-size:17px;font-weight:400;margin-bottom:5px;margin-top:24px}}
  .stitle:first-child{{margin-top:0}}
  .sdesc{{font-size:13px;color:var(--muted);margin-bottom:16px}}
  .empty{{text-align:center;padding:50px 20px;color:var(--muted)}}
  .empty h3{{font-size:15px;font-weight:500;margin-bottom:7px}}
  footer{{text-align:center;padding:18px;font-size:12px;color:var(--faint);border-top:1px solid var(--border);background:var(--surface);margin-top:28px}}

  /* TREND SPARKLINE */
  .spark-row{{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--border)}}
  .spark-row:last-child{{border-bottom:none}}
  .spark-label{{font-size:12px;font-weight:500;min-width:160px}}
  .spark-dots{{display:flex;align-items:center;gap:3px;flex:1}}
  .spark-dot{{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:600;color:#fff;flex-shrink:0}}
  .spark-val{{font-size:12px;font-weight:600;min-width:52px;text-align:right}}
</style>
</head>
<body>

<div class="header">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div>
      <div class="title">Inteligência de Mercado — Rodoviário</div>
      <div class="subtitle">Monitoramento de movimentos de preço da concorrência por trecho</div>
    </div>
    <div style="display:flex;align-items:center;gap:6px;background:#E3F2E9;border:1px solid rgba(46,107,64,.2);border-radius:20px;padding:5px 12px;font-size:12px;color:#2E6B40;white-space:nowrap;margin-top:4px">
      <span style="width:7px;height:7px;border-radius:50%;background:#2E6B40;display:inline-block"></span>
      <span id="update-text">carregando...</span>
    </div>
  </div>
</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('visao',this)">Visão geral</div>
  <div class="tab" onclick="switchTab('altas',this)">🔺 Maiores altas</div>
  <div class="tab" onclick="switchTab('quedas',this)">🔻 Maiores quedas</div>
  <div class="tab" onclick="switchTab('instavel',this)">⚡ Comportamento instável</div>
  <div class="tab" onclick="switchTab('tendencia',this)">📈 Tendência semanal</div>
  <div class="tab" onclick="switchTab('feriados',this)">🎉 Feriados</div>
</div>

<div class="main">
  <div id="panel-visao"     class="panel active"></div>
  <div id="panel-altas"     class="panel"></div>
  <div id="panel-quedas"    class="panel"></div>
  <div id="panel-instavel"  class="panel"></div>
  <div id="panel-tendencia" class="panel"></div>
  <div id="panel-feriados"  class="panel"></div>
</div>

<footer>Referência base: semana 23/02–01/03/2026 · Monitoramento contínuo de movimentos de mercado</footer>

<script>
{data_js}

const CI={{}};
const CUP='#C8402A', CDN='#2E6B40', CWN='#B07A10', CGR='#9C9A93';

function vari(a,r){{return(!r||r==0)?null:((a-r)/r)*100}}
function fv(p){{
  if(p===null)return'<span class="vf">–</span>';
  const s=p>0?'+':'';
  return`<span class="${{p>0?'vu':p<0?'vd':'vf'}}">${{s}}${{p.toFixed(1)}}%</span>`;
}}
function fb(v){{return'R$ '+parseFloat(v).toFixed(2).replace('.',',')}}
function ts(t){{return t.split('-').filter(p=>p.length>2).map(p=>p[0].toUpperCase()+p.slice(1)).join(' › ')}}

function enrich(rows){{
  return rows.map(r=>{{
    const p=vari(r.media_preco_atual,r.media_preco_referencia);
    return{{...r,pct:p,tf:ts(r.trecho_unico)}};
  }});
}}

// Agrega por trecho — média de todas as obs de um período
function aggByTrecho(rows){{
  const byT={{}};
  enrich(rows).forEach(r=>{{
    if(!byT[r.trecho_unico])byT[r.trecho_unico]=[];
    byT[r.trecho_unico].push(r.pct||0);
  }});
  return Object.entries(byT).map(([t,pcts])=>{{
    const avg=pcts.reduce((s,v)=>s+v,0)/pcts.length;
    return{{trecho_unico:t,tf:ts(t),pct:avg,n:pcts.length,
      stddev:Math.sqrt(pcts.map(v=>(v-avg)**2).reduce((s,v)=>s+v,0)/pcts.length)}};
  }});
}}

// Todos os períodos combinados
function allAgg(){{
  const keys=['semanas','s16','s23','pascoa','tiradentes'];
  const combined={{}};
  keys.forEach(k=>{{
    if(!INJECTED[k])return;
    aggByTrecho(INJECTED[k]).forEach(r=>{{
      if(!combined[r.trecho_unico])combined[r.trecho_unico]=[];
      combined[r.trecho_unico].push(r.pct);
    }});
  }});
  return Object.entries(combined).map(([t,pcts])=>{{
    const avg=pcts.reduce((s,v)=>s+v,0)/pcts.length;
    const stddev=Math.sqrt(pcts.map(v=>(v-avg)**2).reduce((s,v)=>s+v,0)/pcts.length);
    return{{trecho_unico:t,tf:ts(t),pct:avg,stddev,n:pcts.length}};
  }}).sort((a,b)=>b.pct-a.pct);
}}

function dotColor(pct){{
  if(pct>10)return CUP;
  if(pct>3)return'#E07050';
  if(pct>-3)return CGR;
  if(pct>-10)return'#50A070';
  return CDN;
}}

function movBadge(pct,std){{
  if(std>10)return'<span class="badge b-instavel">⚡ Instável</span>';
  if(pct>=5)return'<span class="badge b-alta">🔺 Em alta</span>';
  if(pct<=-5)return'<span class="badge b-queda">🔻 Em queda</span>';
  return'<span class="badge b-estavel">— Estável</span>';
}}

function destroyChart(id){{if(CI[id]){{CI[id].destroy();delete CI[id]}}}}

function hbarChart(id,labels,data,colors,h){{
  destroyChart(id);
  setTimeout(()=>{{
    const ctx=document.getElementById(id);if(!ctx)return;
    CI[id]=new Chart(ctx,{{type:'bar',
      data:{{labels,datasets:[{{data,backgroundColor:colors,borderRadius:4,borderSkipped:false}}]}},
      options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{c.raw>0?'+':''}}${{c.raw.toFixed(1)}}%`}}}}}},
        scales:{{
          x:{{grid:{{color:'rgba(0,0,0,0.05)'}},ticks:{{callback:v=>`${{v>0?'+':''}}${{v.toFixed(0)}}%`,font:{{size:11}}}},
             zeroline:true,zerolinecolor:'rgba(0,0,0,0.2)'}},
          y:{{grid:{{display:false}},ticks:{{font:{{size:11}},color:'#6B6963'}}}}
        }}
      }}
    }});
  }},50);
}}

function switchTab(key,el){{
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('panel-'+key).classList.add('active');
  renderPanel(key);
}}

// ── VISÃO GERAL ──────────────────────────────────────────────────────────────
function renderVisao(){{
  const all=allAgg();
  if(!all.length){{
    document.getElementById('panel-visao').innerHTML='<div class="empty"><h3>Nenhum dado carregado</h3><p>Carregue os arquivos CSV para visualizar a análise.</p></div>';
    return;
  }}

  const altas  = all.filter(r=>r.pct>=5).length;
  const quedas = all.filter(r=>r.pct<=-5).length;
  const instaveis = all.filter(r=>r.stddev>10).length;
  const avg = all.reduce((s,r)=>s+r.pct,0)/all.length;

  const topAlta  = all[0];
  const topQueda = [...all].sort((a,b)=>a.pct-b.pct)[0];
  const topInst  = [...all].sort((a,b)=>b.stddev-a.stddev)[0];

  // Signal
  let signalClass='', signalLabel='', signalText='';
  const altaPct=topAlta?topAlta.pct:0;
  const altaSign=altaPct>0?'+':'';
  const quedaPct=topQueda?topQueda.pct:0;
  const avgSign2=avg>0?'+':'';
  if(altas>quedas*2){{
    signalClass=''; signalLabel='Movimento de alta generalizado';
    signalText='O mercado está sinalizando pressão de alta em '+altas+' trecho(s). O trecho com maior movimento é <strong>'+(topAlta?topAlta.tf:'–')+'</strong> com variação média de <strong>'+altaSign+altaPct.toFixed(1)+'%</strong> sobre a referência.';
  }} else if(quedas>altas*2){{
    signalClass='down'; signalLabel='Movimento de queda generalizado';
    signalText='O mercado está sinalizando queda de preços em '+quedas+' trecho(s). O trecho com maior redução é <strong>'+(topQueda?topQueda.tf:'–')+'</strong> com '+quedaPct.toFixed(1)+'% abaixo da referência.';
  }} else {{
    signalClass='neutral'; signalLabel='Mercado misto — monitorar';
    signalText='Sinais divergentes: '+altas+' trecho(s) em alta e '+quedas+' em queda. Variação média geral de '+avgSign2+avg.toFixed(1)+'%. Recomenda-se acompanhar a evolução semanal.';
  }}

  const top8 = all.slice(0,8);
  const bot8 = [...all].sort((a,b)=>a.pct-b.pct).slice(0,8);

  document.getElementById('panel-visao').innerHTML=`
    <div class="signal ${{signalClass}}">
      <div class="signal-lbl">Sinal de mercado — ${{new Date().toLocaleDateString('pt-BR')}}</div>
      <div class="signal-title">${{signalLabel}}</div>
      <div class="signal-body">${{signalText}}</div>
    </div>

    <div class="kpi-grid">
      <div class="kpi ${{avg>=5?'up':avg<=-5?'down':'warn'}}">
        <div class="kpi-lbl">Variação média geral</div>
        <div class="kpi-val">\${{avgSign2}}\${{avg.toFixed(1)}}%</div>
        <div class="kpi-desc">Todos os trechos e períodos</div>
      </div>
      <div class="kpi up">
        <div class="kpi-lbl">Trechos em alta ≥5%</div>
        <div class="kpi-val">${{altas}}</div>
        <div class="kpi-desc">de ${{all.length}} monitorados</div>
      </div>
      <div class="kpi down">
        <div class="kpi-lbl">Trechos em queda ≥5%</div>
        <div class="kpi-val">${{quedas}}</div>
        <div class="kpi-desc">de ${{all.length}} monitorados</div>
      </div>
      <div class="kpi warn">
        <div class="kpi-lbl">Comportamento instável</div>
        <div class="kpi-val">${{instaveis}}</div>
        <div class="kpi-desc">desvio padrão &gt;10%</div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:18px">
      <div class="cc">
        <h3>Top 8 maiores altas</h3>
        <p class="cdesc">Trechos com maior pressão de alta da concorrência</p>
        <div class="cwrap" style="height:${{Math.max(240,top8.length*36)}}px">
          <canvas id="c-top-altas"></canvas>
        </div>
      </div>
      <div class="cc">
        <h3>Top 8 maiores quedas</h3>
        <p class="cdesc">Trechos onde a concorrência reduziu mais os preços</p>
        <div class="cwrap" style="height:${{Math.max(240,bot8.length*36)}}px">
          <canvas id="c-top-quedas"></canvas>
        </div>
      </div>
    </div>

    <div class="tc">
      <div class="th2"><h3>Todos os trechos — resumo de movimentos</h3></div>
      <table>
        <thead><tr>
          <th>Trecho</th>
          <th>Variação média</th>
          <th>Volatilidade</th>
          <th>Obs.</th>
          <th>Sinal</th>
        </tr></thead>
        <tbody>
          ${{all.map(r=>`
            <tr>
              <td class="tt">${{r.tf}}</td>
              <td>${{fv(r.pct)}}</td>
              <td><span style="color:${{r.stddev>10?CWN:r.stddev>5?'#888':CGR}};font-size:12px">
                ${{r.stddev>10?'⚡ Alta':r.stddev>5?'Média':'Baixa'}} (${{r.stddev.toFixed(1)}}σ)
              </span></td>
              <td style="color:var(--muted);font-size:12px">${{r.n}}</td>
              <td>${{movBadge(r.pct,r.stddev)}}</td>
            </tr>`).join('')}}
        </tbody>
      </table>
    </div>
  `;

  hbarChart('c-top-altas', top8.map(r=>r.tf), top8.map(r=>parseFloat(r.pct.toFixed(1))),
    top8.map(r=>r.pct>0?CUP:CDN), Math.max(240,top8.length*36));
  hbarChart('c-top-quedas', bot8.map(r=>r.tf), bot8.map(r=>parseFloat(r.pct.toFixed(1))),
    bot8.map(r=>r.pct>0?CUP:CDN), Math.max(240,bot8.length*36));
}}

// ── MAIORES ALTAS ─────────────────────────────────────────────────────────────
function renderAltas(){{
  const all=allAgg().filter(r=>r.pct>0).sort((a,b)=>b.pct-a.pct);
  if(!all.length){{document.getElementById('panel-altas').innerHTML='<div class="empty"><h3>Nenhuma alta identificada</h3></div>';return;}}

  document.getElementById('panel-altas').innerHTML=`
    <h2 class="stitle">Trechos com maiores altas</h2>
    <p class="sdesc">Concorrentes aumentando preços — ordenado por maior variação positiva média.</p>
    <div class="cc">
      <h3>Variação positiva por trecho</h3>
      <p class="cdesc">Média de todos os períodos carregados</p>
      <div class="cwrap" style="height:${{Math.max(300,all.length*36)}}px">
        <canvas id="c-altas"></canvas>
      </div>
    </div>
    <div class="tc">
      <div class="th2"><h3>Detalhamento</h3></div>
      <table>
        <thead><tr><th>Trecho</th><th>Variação média</th><th>Volatilidade</th><th>Sinal</th></tr></thead>
        <tbody>${{all.map(r=>`
          <tr>
            <td class="tt">${{r.tf}}</td>
            <td>${{fv(r.pct)}}</td>
            <td style="font-size:12px;color:var(--muted)">${{r.stddev.toFixed(1)}}σ</td>
            <td>${{movBadge(r.pct,r.stddev)}}</td>
          </tr>`).join('')}}
        </tbody>
      </table>
    </div>`;

  hbarChart('c-altas', all.map(r=>r.tf), all.map(r=>parseFloat(r.pct.toFixed(1))),
    all.map(()=>CUP), Math.max(300,all.length*36));
}}

// ── MAIORES QUEDAS ────────────────────────────────────────────────────────────
function renderQuedas(){{
  const all=allAgg().filter(r=>r.pct<0).sort((a,b)=>a.pct-b.pct);
  if(!all.length){{document.getElementById('panel-quedas').innerHTML='<div class="empty"><h3>Nenhuma queda identificada</h3></div>';return;}}

  document.getElementById('panel-quedas').innerHTML=`
    <h2 class="stitle">Trechos com maiores quedas</h2>
    <p class="sdesc">Concorrentes reduzindo preços — pode indicar estratégia de ganho de share ou demanda fraca.</p>
    <div class="cc">
      <h3>Variação negativa por trecho</h3>
      <p class="cdesc">Média de todos os períodos carregados</p>
      <div class="cwrap" style="height:${{Math.max(300,all.length*36)}}px">
        <canvas id="c-quedas"></canvas>
      </div>
    </div>
    <div class="tc">
      <div class="th2"><h3>Detalhamento</h3></div>
      <table>
        <thead><tr><th>Trecho</th><th>Variação média</th><th>Volatilidade</th><th>Sinal</th></tr></thead>
        <tbody>${{all.map(r=>`
          <tr>
            <td class="tt">${{r.tf}}</td>
            <td>${{fv(r.pct)}}</td>
            <td style="font-size:12px;color:var(--muted)">${{r.stddev.toFixed(1)}}σ</td>
            <td>${{movBadge(r.pct,r.stddev)}}</td>
          </tr>`).join('')}}
        </tbody>
      </table>
    </div>`;

  hbarChart('c-quedas', all.map(r=>r.tf), all.map(r=>parseFloat(r.pct.toFixed(1))),
    all.map(()=>CDN), Math.max(300,all.length*36));
}}

// ── COMPORTAMENTO INSTÁVEL ────────────────────────────────────────────────────
function renderInstavel(){{
  const all=allAgg().sort((a,b)=>b.stddev-a.stddev);
  if(!all.length){{document.getElementById('panel-instavel').innerHTML='<div class="empty"><h3>Nenhum dado</h3></div>';return;}}

  document.getElementById('panel-instavel').innerHTML=`
    <h2 class="stitle">Comportamento instável</h2>
    <p class="sdesc">Trechos com maior volatilidade de preço — concorrentes mudando estratégia com frequência.</p>
    <div class="cc">
      <h3>Desvio padrão por trecho (σ)</h3>
      <p class="cdesc">Quanto maior o σ, mais inconsistente o comportamento de precificação da concorrência</p>
      <div class="cwrap" style="height:${{Math.max(300,all.length*36)}}px">
        <canvas id="c-instavel"></canvas>
      </div>
    </div>
    <div class="tc">
      <div class="th2"><h3>Ranking de volatilidade</h3></div>
      <table>
        <thead><tr><th>Trecho</th><th>Desvio padrão (σ)</th><th>Variação média</th><th>Obs.</th><th>Sinal</th></tr></thead>
        <tbody>${{all.map(r=>`
          <tr>
            <td class="tt">${{r.tf}}</td>
            <td style="font-weight:600;color:${{r.stddev>10?CWN:r.stddev>5?'#888':CGR}}">${{r.stddev.toFixed(1)}}σ</td>
            <td>${{fv(r.pct)}}</td>
            <td style="font-size:12px;color:var(--muted)">${{r.n}}</td>
            <td>${{movBadge(r.pct,r.stddev)}}</td>
          </tr>`).join('')}}
        </tbody>
      </table>
    </div>`;

  destroyChart('c-instavel');
  setTimeout(()=>{{
    const ctx=document.getElementById('c-instavel');if(!ctx)return;
    CI['c-instavel']=new Chart(ctx,{{type:'bar',
      data:{{labels:all.map(r=>r.tf),datasets:[{{
        data:all.map(r=>parseFloat(r.stddev.toFixed(1))),
        backgroundColor:all.map(r=>r.stddev>10?CWN:r.stddev>5?'#C89040':CGR),
        borderRadius:4,borderSkipped:false
      }}]}},
      options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`σ = ${{c.raw.toFixed(1)}}`}}}}}},
        scales:{{
          x:{{grid:{{color:'rgba(0,0,0,0.05)'}},ticks:{{callback:v=>`σ${{v}}`,font:{{size:11}}}}}},
          y:{{grid:{{display:false}},ticks:{{font:{{size:11}},color:'#6B6963'}}}}
        }}
      }}
    }});
  }},50);
}}

// ── TENDÊNCIA SEMANAL ─────────────────────────────────────────────────────────
function renderTendencia(){{
  const periods=[
    {{key:'semanas',label:'Sem. ant.'}},
    {{key:'s16',label:'16–22/03'}},
    {{key:'s23',label:'23–29/03'}},
  ];
  const available=periods.filter(p=>INJECTED[p.key]);
  if(available.length<2){{
    document.getElementById('panel-tendencia').innerHTML='<div class="empty"><h3>Carregue ao menos 2 semanas</h3><p>Para ver tendência é necessário ter pelo menos 2 períodos semanais carregados.</p></div>';
    return;
  }}

  // Trechos presentes em todos os períodos disponíveis
  const trechoSets=available.map(p=>new Set(aggByTrecho(INJECTED[p.key]).map(r=>r.trecho_unico)));
  const comuns=[...trechoSets[0]].filter(t=>trechoSets.every(s=>s.has(t)));

  const rows=comuns.map(t=>{{
    const pcts=available.map(p=>{{
      const found=aggByTrecho(INJECTED[p.key]).find(r=>r.trecho_unico===t);
      return found?parseFloat(found.pct.toFixed(1)):null;
    }});
    const trend=pcts.length>=2?(pcts[pcts.length-1]-pcts[0]):0;
    return{{t,tf:ts(t),pcts,trend}};
  }}).sort((a,b)=>Math.abs(b.trend)-Math.abs(a.trend));

  const sparkRows=rows.map(r=>{{
    const dots=r.pcts.map((p,i)=>{{
      const c=dotColor(p||0);
      const lbl=available[i].label;
      return`<div class="spark-dot" style="background:${{c}};title='${{lbl}}'" title="${{lbl}}: ${{p>0?'+':''}}${{p?.toFixed(1)}}%">${{p>0?'+':''}}${{p?.toFixed(0)}}</div>`;
    }}).join('');
    const arrow=r.trend>3?'↑':r.trend<-3?'↓':'→';
    const ac=r.trend>3?CUP:r.trend<-3?CDN:CGR;
    return`<div class="spark-row">
      <div class="spark-label">${{r.tf}}</div>
      <div class="spark-dots">${{dots}}</div>
      <div class="spark-val" style="color:${{ac}}">${{arrow}} ${{r.trend>0?'+':''}}${{r.trend.toFixed(1)}}%</div>
    </div>`;
  }}).join('');

  document.getElementById('panel-tendencia').innerHTML=`
    <h2 class="stitle">Evolução semanal de preços</h2>
    <p class="sdesc">Como os preços da concorrência evoluíram semana a semana. Cada bolinha representa a variação média daquele período.</p>
    <div class="ig" style="margin-bottom:16px">
      <div class="ic">
        <h4>Legenda das bolinhas</h4>
        <p style="display:flex;gap:8px;flex-wrap:wrap;margin-top:4px">
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${{CUP}};vertical-align:middle"></span> Alta &gt;10%</span>
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#E07050;vertical-align:middle"></span> Alta leve</span>
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${{CGR}};vertical-align:middle"></span> Estável</span>
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#50A070;vertical-align:middle"></span> Queda leve</span>
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${{CDN}};vertical-align:middle"></span> Queda &gt;10%</span>
        </p>
      </div>
      <div class="ic">
        <h4>Períodos carregados</h4>
        <p>${{available.map(p=>`<strong>${{p.label}}</strong>`).join(' → ')}}</p>
      </div>
    </div>
    <div class="cc">
      <h3>Trajetória por trecho</h3>
      <p class="cdesc">Ordenado por maior variação acumulada no período</p>
      ${{sparkRows}}
    </div>`;
}}

// ── FERIADOS ──────────────────────────────────────────────────────────────────
function renderFeriados(){{
  const feriados=[
    {{key:'pascoa',nome:'Páscoa',ref:'Carnaval',ida:'02/04',volta:'05/04'}},
    {{key:'tiradentes',nome:'Tiradentes',ref:'Carnaval',ida:'17/04',volta:'21/04'}},
  ].filter(f=>INJECTED[f.key]);

  if(!feriados.length){{
    document.getElementById('panel-feriados').innerHTML='<div class="empty"><h3>Nenhum feriado carregado</h3><p>Carregue os arquivos de Páscoa e/ou Tiradentes.</p></div>';
    return;
  }}

  let html='';
  html+=`<h2 class="stitle">Comparativo de feriados</h2>`;
  html+=`<p class="sdesc">Comportamento da concorrência nos principais feriados vs. Carnaval como referência de demanda alta.</p>`;

  // Side-by-side se tiver os dois
  if(feriados.length===2){{
    const agg0=aggByTrecho(INJECTED[feriados[0].key]).sort((a,b)=>b.pct-a.pct);
    const agg1=aggByTrecho(INJECTED[feriados[1].key]).sort((a,b)=>b.pct-a.pct);
    const trechos=new Set([...agg0.map(r=>r.trecho_unico),...agg1.map(r=>r.trecho_unico)]);

    const rows=[...trechos].map(t=>{{
      const r0=agg0.find(r=>r.trecho_unico===t);
      const r1=agg1.find(r=>r.trecho_unico===t);
      return{{t,tf:ts(t),p0:r0?r0.pct:null,p1:r1?r1.pct:null}};
    }}).sort((a,b)=>Math.max(Math.abs(b.p0||0),Math.abs(b.p1||0))-Math.max(Math.abs(a.p0||0),Math.abs(a.p1||0)));

    html+=`<div class="tc">
      <div class="th2"><h3>Comparativo ${{feriados[0].nome}} vs ${{feriados[1].nome}}</h3>
        <span style="font-size:12px;color:var(--muted)">Referência: Carnaval</span>
      </div>
      <table>
        <thead><tr>
          <th>Trecho</th>
          <th>${{feriados[0].nome}} (${{feriados[0].ida}}/${{feriados[0].volta}})</th>
          <th>${{feriados[1].nome}} (${{feriados[1].ida}}/${{feriados[1].volta}})</th>
          <th>Δ entre feriados</th>
        </tr></thead>
        <tbody>${{rows.map(r=>{{
          const delta=(r.p1!==null&&r.p0!==null)?r.p1-r.p0:null;
          return`<tr>
            <td class="tt">${{r.tf}}</td>
            <td>${{fv(r.p0)}}</td>
            <td>${{fv(r.p1)}}</td>
            <td>${{fv(delta)}}</td>
          </tr>`;
        }}).join('')}}</tbody>
      </table>
    </div>`;
  }}

  // Individual por feriado
  feriados.forEach(f=>{{
    const agg=aggByTrecho(INJECTED[f.key]).sort((a,b)=>b.pct-a.pct);
    const cid=`c-fer-${{f.key}}`;
    html+=`
      <h2 class="stitle" style="margin-top:28px">${{f.nome}} vs ${{f.ref}}</h2>
      <p class="sdesc">Ida ${{f.ida}}, Volta ${{f.volta}} · Maior variação indica precificação acima da referência de alta demanda.</p>
      <div class="cc">
        <h3>Variação por trecho</h3>
        <div class="cwrap" style="height:${{Math.max(280,agg.length*36)}}px"><canvas id="${{cid}}"></canvas></div>
      </div>`;
    setTimeout(()=>hbarChart(cid,
      [...agg].sort((a,b)=>a.pct-b.pct).map(r=>r.tf),
      [...agg].sort((a,b)=>a.pct-b.pct).map(r=>parseFloat(r.pct.toFixed(1))),
      [...agg].sort((a,b)=>a.pct-b.pct).map(r=>r.pct>0?CUP:CDN),
      Math.max(280,agg.length*36)
    ),100);
  }});

  document.getElementById('panel-feriados').innerHTML=html;
}}

// ── ROUTER ────────────────────────────────────────────────────────────────────
function renderPanel(key){{
  if(key==='visao')    renderVisao();
  else if(key==='altas')     renderAltas();
  else if(key==='quedas')    renderQuedas();
  else if(key==='instavel')  renderInstavel();
  else if(key==='tendencia') renderTendencia();
  else if(key==='feriados')  renderFeriados();
}}

// ── INIT ──────────────────────────────────────────────────────────────────────
document.getElementById('update-text').textContent = UPDATE_LABEL;
renderVisao();
</script>
</body></html>"""

import streamlit.components.v1 as components
import hashlib

data_hash = hashlib.md5(data_js.encode()).hexdigest()
html_with_hash = html.replace("</body>", f"<!-- hash:{data_hash} --></body>")
components.html(html_with_hash, height=2800, scrolling=True)
