import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Repasse do Diesel",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Remove streamlit default padding + force sidebar always visible
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > .main { padding: 0 !important; }
    [data-testid="stHeader"] { display: none; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid rgba(0,0,0,0.08);
        min-width: 280px !important;
        width: 280px !important;
    }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR — UPLOAD ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 Arquivos CSV")
    st.caption("Substitua qualquer arquivo para atualizar a análise automaticamente.")
    st.divider()

    up_semanas    = st.file_uploader("Semanas anteriores",  type="csv", key="up_sem")
    up_s16        = st.file_uploader("Semana 16–22/03",     type="csv", key="up_s16")
    up_s23        = st.file_uploader("Semana 23–29/03",     type="csv", key="up_s23")
    up_pascoa     = st.file_uploader("Feriado Páscoa",      type="csv", key="up_pas")
    up_tiradentes = st.file_uploader("Feriado Tiradentes",  type="csv", key="up_tir")

    st.divider()
    st.caption("**Referência base:** semana 23/02–01/03/2026")
    st.caption("**Reajuste:** pós 16/03/2026")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
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
"""

# ── HTML DASHBOARD ────────────────────────────────────────────────────────────
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
    --accent:#C8402A;--accent-l:#FAE8E4;
    --warn:#B07A10;--warn-l:#FDF3DC;
    --ok:#2E6B40;--ok-l:#E3F2E9;
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
  .tab.active{{color:var(--text);border-bottom-color:var(--accent)}}
  .main{{padding:24px 28px}}
  .panel{{display:none}}.panel.active{{display:block}}
  .verdict{{background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:var(--rl);padding:20px 24px;margin-bottom:18px}}
  .verdict-lbl{{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:7px}}
  .verdict-title{{font-family:'DM Serif Display',serif;font-size:18px;margin-bottom:9px;line-height:1.35}}
  .verdict-body{{font-size:13px;color:var(--muted);line-height:1.7}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-bottom:18px}}
  .kpi{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px}}
  .kpi-lbl{{font-size:11px;color:var(--faint);text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px}}
  .kpi-val{{font-size:21px;font-weight:600;line-height:1;margin-bottom:3px}}
  .kpi-desc{{font-size:12px;color:var(--muted)}}
  .kpi.up .kpi-val{{color:var(--accent)}}.kpi.warn .kpi-val{{color:var(--warn)}}.kpi.ok .kpi-val{{color:var(--ok)}}
  .ig{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:18px}}
  .ic{{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px}}
  .ic h4{{font-size:13px;font-weight:600;margin-bottom:6px}}
  .ic p{{font-size:13px;color:var(--muted);line-height:1.6}}
  .cc{{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);padding:20px;margin-bottom:16px}}
  .cc h3{{font-size:14px;font-weight:600;margin-bottom:3px}}
  .cdesc{{font-size:12px;color:var(--muted);margin-bottom:16px}}
  .cwrap{{position:relative;width:100%}}
  .tc{{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);overflow:hidden;margin-bottom:16px}}
  .th2{{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}}
  .th2 h3{{font-size:14px;font-weight:600}}
  .fr{{display:flex;gap:5px;flex-wrap:wrap}}
  .fc{{padding:3px 10px;border-radius:20px;border:1px solid var(--border-strong);font-size:12px;cursor:pointer;transition:all .15s;background:var(--surface);color:var(--muted);font-family:'DM Sans',sans-serif}}
  .fc:hover{{background:var(--surface2)}}
  .fc.active{{background:var(--text);color:#fff;border-color:var(--text)}}
  .fc.ca{{background:var(--accent-l);color:var(--accent);border-color:rgba(200,64,42,.2)}}
  .fc.ca.active{{background:var(--accent);color:#fff}}
  .fc.cm{{background:var(--warn-l);color:var(--warn);border-color:rgba(176,122,16,.2)}}
  .fc.cm.active{{background:var(--warn);color:#fff}}
  .fc.cl{{background:var(--ok-l);color:var(--ok);border-color:rgba(46,107,64,.2)}}
  .fc.cl.active{{background:var(--ok);color:#fff}}
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  thead th{{padding:9px 14px;text-align:left;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--faint);background:var(--surface2);border-bottom:1px solid var(--border)}}
  tbody tr{{border-bottom:1px solid var(--border);transition:background .1s}}
  tbody tr:last-child{{border-bottom:none}}
  tbody tr:hover{{background:var(--surface2)}}
  tbody td{{padding:9px 14px}}
  .tt{{font-weight:500}}
  .badge{{display:inline-flex;align-items:center;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;white-space:nowrap}}
  .ba{{background:var(--accent-l);color:var(--accent)}}
  .bm{{background:var(--warn-l);color:var(--warn)}}
  .bl{{background:var(--ok-l);color:var(--ok)}}
  .bn{{background:var(--neutral-l);color:var(--neutral)}}
  .vu{{color:var(--accent);font-weight:600}}.vd{{color:var(--ok)}}.vf{{color:var(--muted)}}
  .stitle{{font-family:'DM Serif Display',serif;font-size:17px;font-weight:400;margin-bottom:5px;margin-top:24px}}
  .stitle:first-child{{margin-top:0}}
  .sdesc{{font-size:13px;color:var(--muted);margin-bottom:16px}}
  .empty{{text-align:center;padding:50px 20px;color:var(--muted)}}
  .empty h3{{font-size:15px;font-weight:500;margin-bottom:7px}}
  footer{{text-align:center;padding:18px;font-size:12px;color:var(--faint);border-top:1px solid var(--border);background:var(--surface);margin-top:28px}}
</style>
</head>
<body>
<div class="header">
  <div class="title">Monitoramento de Repasse do Diesel</div>
  <div class="subtitle">Transporte rodoviário de passageiros — Comparativo pós-reajuste</div>
</div>
<div class="tabs">
  <div class="tab active" onclick="switchTab('resumo',this)">Resumo executivo</div>
  <div class="tab" onclick="switchTab('semanas',this)">Semanas anteriores</div>
  <div class="tab" onclick="switchTab('s16',this)">16–22/03</div>
  <div class="tab" onclick="switchTab('s23',this)">23–29/03</div>
  <div class="tab" onclick="switchTab('pascoa',this)">Páscoa</div>
  <div class="tab" onclick="switchTab('tiradentes',this)">Tiradentes</div>
</div>
<div class="main">
  <div id="panel-resumo" class="panel active"></div>
  <div id="panel-semanas" class="panel"></div>
  <div id="panel-s16" class="panel"></div>
  <div id="panel-s23" class="panel"></div>
  <div id="panel-pascoa" class="panel"></div>
  <div id="panel-tiradentes" class="panel"></div>
</div>
<footer>Referência base: semana 23/02–01/03/2026 · Reajuste do diesel analisado pós-16/03/2026</footer>

<script>
{data_js}
const CI={{}};
let AF={{semanas:'todos',s16:'todos',s23:'todos',pascoa:'todos',tiradentes:'todos'}};
const CL={{alto:'#C8402A',mod:'#B07A10',leve:'#2E6B40',pos:'#2E6B40',neg:'#9C9A93'}};
const LL={{alto:'Muito relevante',mod:'Moderado',leve:'Leve',pos:'Leve positivo',neg:'Sem repasse'}};

function vari(a,r){{return(!r||r==0)?null:((a-r)/r)*100}}
function cls(p){{if(p===null)return null;if(p>=15)return'alto';if(p>=10)return'mod';if(p>=5)return'leve';if(p>0)return'pos';return'neg'}}
function badge(c){{const m={{alto:'ba',mod:'bm',leve:'bl',pos:'bl',neg:'bn'}};return`<span class="badge ${{m[c]||'bn'}}">${{LL[c]||'–'}}</span>`}}
function fv(p){{if(p===null)return'<span class="vf">–</span>';const s=p>0?'+':'';return`<span class="${{p>0?'vu':p<0?'vd':'vf'}}">${{s}}${{p.toFixed(1)}}%</span>`}}
function fb(v){{return'R$ '+parseFloat(v).toFixed(2).replace('.',',')}}
function ts(t){{return t.split('-').filter(p=>p.length>2).map(p=>p[0].toUpperCase()+p.slice(1)).join(' › ')}}
function enrich(rows){{return rows.map(r=>{{const p=vari(r.media_preco_atual,r.media_preco_referencia);return{{...r,pct:p,cls:cls(p),tf:ts(r.trecho_unico)}}}})}}
function filt(rows,f){{if(f==='todos')return rows;if(f==='repasse')return rows.filter(r=>r.pct>=5);return rows.filter(r=>r.cls===f)}}
function chips(key,f){{return`<div class="fr">
  <button class="fc ${{f==='todos'?'active':''}}" onclick="sf('${{key}}','todos',this)">Todos</button>
  <button class="fc ca ${{f==='alto'?'active':''}}" onclick="sf('${{key}}','alto',this)">Muito relevante ≥15%</button>
  <button class="fc cm ${{f==='mod'?'active':''}}" onclick="sf('${{key}}','mod',this)">Moderado 10–15%</button>
  <button class="fc cl ${{f==='leve'?'active':''}}" onclick="sf('${{key}}','leve',this)">Leve 5–10%</button>
  <button class="fc ${{f==='repasse'?'active':''}}" onclick="sf('${{key}}','repasse',this)">Com repasse ≥5%</button>
</div>`}}
function dc(id){{if(CI[id]){{CI[id].destroy();delete CI[id]}}}}
function bar(id,labels,data,colors,h){{
  dc(id);
  setTimeout(()=>{{
    const ctx=document.getElementById(id);if(!ctx)return;
    CI[id]=new Chart(ctx,{{type:'bar',
      data:{{labels,datasets:[{{data,backgroundColor:colors,borderRadius:4,borderSkipped:false}}]}},
      options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{c.raw>0?'+':''}}${{c.raw.toFixed(1)}}%`}}}}}},
        scales:{{
          x:{{grid:{{color:'rgba(0,0,0,0.05)'}},ticks:{{callback:v=>`${{v>0?'+':''}}${{v.toFixed(0)}}%`,font:{{size:11}}}}}},
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
}}
function sf(key,val,el){{
  AF[key]=val;
  el.closest('.fr').querySelectorAll('.fc').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
  rp(key);
}}
function rp(key){{
  if(key==='semanas')rSem();
  else if(key==='s16')rDet('s16','16 a 22 de março');
  else if(key==='s23')rDet('s23','23 a 29 de março');
  else if(key==='pascoa')rFer('pascoa','Páscoa','02/04 (ida) e 05/04 (volta)','Carnaval');
  else if(key==='tiradentes')rFer('tiradentes','Tiradentes','17/04 (ida) e 21/04 (volta)','Carnaval');
}}

function rExec(){{
  const keys=['semanas','s16','s23','pascoa','tiradentes'];
  const all=[];const ps=[];
  const plabels={{semanas:'Sem. ant.',s16:'16–22/03',s23:'23–29/03',pascoa:'Páscoa',tiradentes:'Tiradentes'}};
  keys.forEach(k=>{{
    if(!INJECTED[k])return;
    const e=enrich(INJECTED[k]);
    e.forEach(r=>all.push(r));
    const avg=e.reduce((s,r)=>s+(r.pct||0),0)/e.length;
    ps.push({{label:plabels[k],avg,cls:cls(avg)}});
  }});
  if(!all.length){{
    document.getElementById('panel-resumo').innerHTML='<div class="empty"><h3>Nenhum dado carregado</h3><p>Use a barra lateral para fazer upload dos CSVs.</p></div>';return;
  }}
  const wr=all.filter(r=>r.pct>=5);
  const ac=all.filter(r=>r.cls==='alto').length;
  const mc=all.filter(r=>r.cls==='mod').length;
  const ag=all.reduce((s,r)=>s+(r.pct||0),0)/all.length;
  const pr=(wr.length/all.length*100).toFixed(0);
  const verdict=ac>3?'Sinais expressivos de repasse identificados — múltiplos trechos com variações acima de 15%.':
    wr.length>all.length*.4?'Repasse parcial em andamento — parte significativa dos trechos já apresenta elevações tarifárias.':
    'Repasse limitado até o momento — maioria dos trechos ainda sem variação significativa.';
  const byT={{}};
  all.filter(r=>r.pct>=5).forEach(r=>{{if(!byT[r.trecho_unico])byT[r.trecho_unico]=[];byT[r.trecho_unico].push(r.pct)}});
  const top=Object.entries(byT).map(([t,pcts])=>{{const a=pcts.reduce((s,v)=>s+v,0)/pcts.length;return{{t,a,c:cls(a)}}}})
    .sort((a,b)=>b.a-a.a).slice(0,6);
  const hi=[...all].sort((a,b)=>b.pct-a.pct)[0];
  const lo=[...all].sort((a,b)=>a.pct-b.pct)[0];

  document.getElementById('panel-resumo').innerHTML=`
    <div class="verdict">
      <div class="verdict-lbl">Diagnóstico — ${{new Date().toLocaleDateString('pt-BR')}}</div>
      <div class="verdict-title">${{verdict}}</div>
      <div class="verdict-body">De ${{all.length}} observações em ${{ps.length}} período(s), ${{wr.length}} (${{pr}}%) apresentam variação ≥5%. Variação média geral: ${{ag>0?'+':''}}${{ag.toFixed(1)}}%.</div>
    </div>
    <div class="kpi-grid">
      <div class="kpi ${{ag>=10?'up':ag>=5?'warn':'ok'}}"><div class="kpi-lbl">Variação média geral</div><div class="kpi-val">${{ag>0?'+':''}}${{ag.toFixed(1)}}%</div><div class="kpi-desc">Sobre a semana de referência</div></div>
      <div class="kpi up"><div class="kpi-lbl">Com repasse ≥5%</div><div class="kpi-val">${{pr}}%</div><div class="kpi-desc">${{wr.length}} de ${{all.length}} registros</div></div>
      <div class="kpi up"><div class="kpi-lbl">Muito relevante ≥15%</div><div class="kpi-val">${{ac}}</div><div class="kpi-desc">Registros com alta variação</div></div>
      <div class="kpi warn"><div class="kpi-lbl">Moderado 10–15%</div><div class="kpi-val">${{mc}}</div><div class="kpi-desc">Registros com var. moderada</div></div>
    </div>
    <div class="cc">
      <h3>Variação média por período</h3><p class="cdesc">Média de todos os trechos em cada período carregado</p>
      <div class="cwrap" style="height:200px"><canvas id="c-exec-p"></canvas></div>
    </div>
    ${{top.length?`<div class="tc"><div class="th2"><h3>Trechos com maior sinal de repasse</h3></div>
    <table><thead><tr><th>Trecho</th><th>Variação média</th><th>Classificação</th></tr></thead>
    <tbody>${{top.map(r=>`<tr><td class="tt">${{ts(r.t)}}</td><td>${{fv(r.a)}}</td><td>${{badge(r.c)}}</td></tr>`).join('')}}</tbody></table></div>`:''}}
    <div class="ig">
      <div class="ic"><h4>Maior variação</h4><p><strong>${{ts(hi.trecho_unico)}}</strong> com ${{fv(hi.pct)}} — ${{badge(hi.cls)}}</p></div>
      <div class="ic"><h4>Menor variação</h4><p><strong>${{ts(lo.trecho_unico)}}</strong> com ${{fv(lo.pct)}} — sem sinal de repasse.</p></div>
      <div class="ic"><h4>Legenda</h4><p><span class="badge ba">Muito relevante</span> ≥15% &nbsp;<span class="badge bm">Moderado</span> 10–15% &nbsp;<span class="badge bl">Leve</span> 5–10%</p></div>
    </div>`;

  dc('c-exec-p');setTimeout(()=>{{
    const ctx=document.getElementById('c-exec-p');if(!ctx)return;
    CI['c-exec-p']=new Chart(ctx,{{type:'bar',
      data:{{labels:ps.map(p=>p.label),datasets:[{{data:ps.map(p=>parseFloat(p.avg.toFixed(1))),backgroundColor:ps.map(p=>CL[p.cls]||'#9C9A93'),borderRadius:6}}]}},
      options:{{responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{c.raw>0?'+':''}}${{c.raw.toFixed(1)}}%`}}}}}},
        scales:{{x:{{grid:{{display:false}},ticks:{{font:{{size:12}}}}}},y:{{grid:{{color:'rgba(0,0,0,0.05)'}},ticks:{{callback:v=>`${{v>0?'+':''}}${{v.toFixed(0)}}%`,font:{{size:11}}}}}}}}
      }}
    }});
  }},50);
}}

function rSem(){{
  if(!INJECTED.semanas){{document.getElementById('panel-semanas').innerHTML='<div class="empty"><h3>Arquivo não carregado</h3></div>';return}}
  const e=enrich(INJECTED.semanas);const f=AF.semanas;
  const filtered=filt(e,f).sort((a,b)=>b.pct-a.pct);
  const sorted=[...e].sort((a,b)=>a.pct-b.pct);
  document.getElementById('panel-semanas').innerHTML=`
    <h2 class="stitle">Semanas anteriores ao reajuste</h2>
    <p class="sdesc">Preços médios agregados por trecho vs. semana-base 23/02–01/03/2026.</p>
    <div class="cc"><h3>Variação percentual por trecho</h3><p class="cdesc">Positivo = preço atual acima da referência</p>
      <div class="cwrap" style="height:${{Math.max(300,sorted.length*38)}}px"><canvas id="c-sem"></canvas></div></div>
    <div class="tc"><div class="th2"><h3>Tabela detalhada</h3>${{chips('semanas',f)}}</div>
    <table><thead><tr><th>Trecho</th><th>Preço ref.</th><th>Preço atual</th><th>Variação</th><th>Classificação</th></tr></thead>
    <tbody>${{filtered.map(r=>`<tr><td class="tt">${{r.tf}}</td><td>${{fb(r.media_preco_referencia)}}</td><td>${{fb(r.media_preco_atual)}}</td><td>${{fv(r.pct)}}</td><td>${{badge(r.cls)}}</td></tr>`).join('')}}</tbody></table></div>`;
  bar('c-sem',sorted.map(r=>r.tf),sorted.map(r=>parseFloat(r.pct.toFixed(1))),sorted.map(r=>CL[r.cls]||'#9C9A93'),Math.max(300,sorted.length*38));
}}

function rDet(key,title){{
  if(!INJECTED[key]){{document.getElementById('panel-'+key).innerHTML='<div class="empty"><h3>Arquivo não carregado</h3></div>';return}}
  const e=enrich(INJECTED[key]);const f=AF[key];
  const byT={{}};e.forEach(r=>{{if(!byT[r.trecho_unico])byT[r.trecho_unico]=[];byT[r.trecho_unico].push(r)}});
  const sum=Object.entries(byT).map(([t,recs])=>{{
    const a=recs.reduce((s,r)=>s+(r.pct||0),0)/recs.length;
    const aA=recs.reduce((s,r)=>s+r.media_preco_atual,0)/recs.length;
    const aR=recs.reduce((s,r)=>s+r.media_preco_referencia,0)/recs.length;
    return{{trecho_unico:t,tf:ts(t),pct:a,cls:cls(a),media_preco_atual:aA,media_preco_referencia:aR}};
  }}).sort((a,b)=>b.pct-a.pct);
  const fs=filt(sum,f);const fd=filt(e,f).sort((a,b)=>a.trecho_unico.localeCompare(b.trecho_unico));
  const sorted=[...sum].sort((a,b)=>a.pct-b.pct);
  document.getElementById('panel-'+key).innerHTML=`
    <h2 class="stitle">Semana ${{title}}</h2>
    <p class="sdesc">Preços por dia e antecedência vs. mesma antecedência na semana-base.</p>
    <div class="cc"><h3>Variação média por trecho</h3><p class="cdesc">Média de todos os dias e antecedências</p>
      <div class="cwrap" style="height:${{Math.max(280,sorted.length*38)}}px"><canvas id="c-${{key}}"></canvas></div></div>
    <div class="tc"><div class="th2"><h3>Resumo por trecho (média semanal)</h3>${{chips(key,f)}}</div>
    <table><thead><tr><th>Trecho</th><th>Preço ref.</th><th>Preço médio</th><th>Variação</th><th>Classificação</th></tr></thead>
    <tbody>${{fs.map(r=>`<tr><td class="tt">${{r.tf}}</td><td>${{fb(r.media_preco_referencia)}}</td><td>${{fb(r.media_preco_atual)}}</td><td>${{fv(r.pct)}}</td><td>${{badge(r.cls)}}</td></tr>`).join('')}}</tbody></table></div>
    <div class="tc"><div class="th2"><h3>Detalhamento por dia e antecedência</h3></div>
    <table><thead><tr><th>Trecho</th><th>Data</th><th>Antec.</th><th>Preço ref.</th><th>Preço atual</th><th>Variação</th><th>Classificação</th></tr></thead>
    <tbody>${{fd.map(r=>`<tr><td class="tt">${{r.tf}}</td><td>${{r.data||'–'}}</td><td>D${{r.antecedencia}}</td><td>${{fb(r.media_preco_referencia)}}</td><td>${{fb(r.media_preco_atual)}}</td><td>${{fv(r.pct)}}</td><td>${{badge(r.cls)}}</td></tr>`).join('')}}</tbody></table></div>`;
  bar('c-'+key,sorted.map(r=>r.tf),sorted.map(r=>parseFloat(r.pct.toFixed(1))),sorted.map(r=>CL[r.cls]||'#9C9A93'),Math.max(280,sorted.length*38));
}}

function rFer(key,nome,dias,refNome){{
  if(!INJECTED[key]){{document.getElementById('panel-'+key).innerHTML='<div class="empty"><h3>Arquivo não carregado</h3></div>';return}}
  const e=enrich(INJECTED[key]).map(r=>{{return{{...r,sentido:(r.data||'').includes('02')||(r.data||'').includes('17')?'Ida':'Volta'}}}});
  const f=AF[key];
  const filtered=filt(e,f).sort((a,b)=>b.pct-a.pct);
  const sorted=[...e].sort((a,b)=>a.pct-b.pct);
  const labels=sorted.map(r=>r.tf+(e.filter(x=>x.trecho_unico===r.trecho_unico).length>1?` (${{r.sentido}})`:''));
  document.getElementById('panel-'+key).innerHTML=`
    <h2 class="stitle">Feriado de ${{nome}}</h2>
    <p class="sdesc">Dias de maior movimento: ${{dias}}. Referência: ${{refNome}}.</p>
    <div class="cc"><h3>Variação percentual vs. ${{refNome}}</h3><p class="cdesc">Preço atual vs. mesmo trecho no ${{refNome}}</p>
      <div class="cwrap" style="height:${{Math.max(280,sorted.length*42)}}px"><canvas id="c-${{key}}"></canvas></div></div>
    <div class="tc"><div class="th2"><h3>Tabela detalhada — ${{nome}}</h3>${{chips(key,f)}}</div>
    <table><thead><tr><th>Trecho</th><th>Data</th><th>Sentido</th><th>Antec.</th><th>Ref. (${{refNome}})</th><th>Preço atual</th><th>Variação</th><th>Classificação</th></tr></thead>
    <tbody>${{filtered.map(r=>`<tr><td class="tt">${{r.tf}}</td><td>${{r.data||'–'}}</td><td>${{r.sentido}}</td><td>D${{r.antecedencia}}</td><td>${{fb(r.media_preco_referencia)}}</td><td>${{fb(r.media_preco_atual)}}</td><td>${{fv(r.pct)}}</td><td>${{badge(r.cls)}}</td></tr>`).join('')}}</tbody></table></div>`;
  bar('c-'+key,labels,sorted.map(r=>parseFloat(r.pct.toFixed(1))),sorted.map(r=>CL[r.cls]||'#9C9A93'),Math.max(280,sorted.length*42));
}}

rExec();
['semanas','s16','s23','pascoa','tiradentes'].forEach(rp);
</script>
</body></html>"""

import streamlit.components.v1 as components
components.html(html, height=2600, scrolling=True)
