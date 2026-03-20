# 🚌 Repasse do Diesel — Dashboard Streamlit

Dashboard interativo para monitorar o repasse do reajuste do diesel nas tarifas de transporte rodoviário de passageiros.

## Estrutura do projeto

```
streamlit-diesel/
├── app.py              ← app principal
├── requirements.txt    ← dependências
├── README.md
└── data/               ← CSVs padrão (opcionais)
    ├── semanas_anteriores.csv
    ├── semana_16_a_22.csv
    ├── semana_23_a_29.csv
    ├── feriado_pascoa.csv
    └── feriado_tiradentes.csv
```

## Como subir no Streamlit Community Cloud

### 1. Crie um repositório no GitHub
- Acesse github.com → **New repository**
- Nome sugerido: `repasse-diesel`
- Deixe **público** (necessário para o plano gratuito do Streamlit Cloud)

### 2. Suba os arquivos
Faça upload dos arquivos pelo GitHub (botão "Add file → Upload files") ou via terminal:

```bash
git init
git add .
git commit -m "primeiro deploy"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/repasse-diesel.git
git push -u origin main
```

### 3. Deploy no Streamlit Cloud
- Acesse **share.streamlit.io**
- Faça login com sua conta GitHub
- Clique em **"New app"**
- Selecione o repositório `repasse-diesel`
- Branch: `main`
- Main file path: `app.py`
- Clique **Deploy!**

Em ~2 minutos o app estará disponível em um link público tipo:
`https://repasse-diesel-USUARIO.streamlit.app`

## Como atualizar os dados

**Opção A — Upload direto no app (mais fácil):**
Use a barra lateral do app para fazer upload de novos CSVs. A análise atualiza instantaneamente.

**Opção B — Atualizar os CSVs padrão:**
Substitua os arquivos na pasta `data/` e faça um novo `git push`. O Streamlit Cloud atualiza automaticamente.

## Formato esperado dos CSVs

| Arquivo | Colunas obrigatórias |
|---|---|
| semanas_anteriores.csv | `trecho_unico, media_preco_atual, media_preco_referencia` |
| semana_16_a_22.csv | `antecedencia, trecho_unico, data, media_preco_atual, media_preco_referencia` |
| semana_23_a_29.csv | idem acima |
| feriado_pascoa.csv | idem acima |
| feriado_tiradentes.csv | idem acima |

> Colunas de mediana são ignoradas automaticamente.
