import streamlit as st
import pandas as pd
import sqlalchemy as db
import plotly.express as px
import os
import boto3 

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="HCI-F | Gestão de Risco",
    page_icon="✈️",
    layout="wide"
)

# --- SEGURANÇA: CARREGAR SECRETS ---
try:
 
    AWS_ACCESS_KEY = st.secrets["aws"]["access_key_id"]
    AWS_SECRET_KEY = st.secrets["aws"]["secret_access_key"]
    AWS_REGION = st.secrets["aws"]["region_name"]
    BUCKET_NAME = st.secrets["aws"]["bucket_name"]
except Exception as e:
    st.error("❌ Erro de configuração: Secrets não encontrados ou mal formatados.")
    st.info("Verifique se o arquivo .streamlit/secrets.toml está correto.")
    st.stop()

DB_FILENAME = "DB_RH_CONSOLIDADO.db"

# --- TÍTULO E CABEÇALHO ---
st.title("✈️ HCI-F: Human Capital Intelligence Framework")
st.markdown("### Monitorização de Risco de Turnover e Absenteísmo")
st.markdown("---")

# --- FUNÇÃO DE CARGA DE DADOS (HÍBRIDA) ---
@st.cache_data(ttl=3600, show_spinner="Baixando dados da Nuvem...")
def carregar_dados_do_banco():
 
    local_path = f"/tmp/{DB_FILENAME}"
    if os.name == 'nt':
        local_path = DB_FILENAME
    
    
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,     
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION              
        )

        s3.download_file(BUCKET_NAME, DB_FILENAME, local_path)
    
    except Exception as e:
        print(f"❌ Erro ao conectar na AWS S3: {e}")
        return pd.DataFrame() # Retorna vazio se falhar o download

    # 2. TENTA LER O ARQUIVO BAIXADO
    try:
        # Verifica se o arquivo realmente chegou
        if not os.path.exists(local_path):
            st.error("Arquivo não encontrado após download.")
            return pd.DataFrame()

        engine = db.create_engine(f'sqlite:///{local_path}')
        conn = engine.connect()
     
        df = pd.read_sql("SELECT * FROM TB_HISTORICO_PRESENCA", conn) 
        conn.close()
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao ler o banco SQLite: {e}")
        return pd.DataFrame()

# --- EXECUÇÃO ---
df = carregar_dados_do_banco()

# Se o dataframe estiver vazio, para por aqui
if df.empty:
    st.warning("Nenhum dado disponível. Verifique a conexão com a AWS.")
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros Operacionais")

# Verifica se as colunas existem antes de criar filtros (para evitar erro de KeyError)
if 'CAPACITAÇÃO' in df.columns:
    opcoes_capacitacao = df['CAPACITAÇÃO'].unique().tolist()
    filtro_capacitacao = st.sidebar.multiselect(
        "Nível de Capacitação:",
        options=opcoes_capacitacao,
        default=opcoes_capacitacao
    )
else:
    filtro_capacitacao = []

if 'ACAO_SUGERIDA' in df.columns:
    opcoes_acao = df['ACAO_SUGERIDA'].unique().tolist()
    filtro_acao = st.sidebar.multiselect(
        "Ação Recomendada:",
        options=opcoes_acao,
        default=opcoes_acao
    )
else:
    filtro_acao = []

# Aplica os filtros
df_filtrado = df.copy()
if filtro_capacitacao:
    df_filtrado = df_filtrado[df_filtrado['CAPACITAÇÃO'].isin(filtro_capacitacao)]
if filtro_acao:
    df_filtrado = df_filtrado[df_filtrado['ACAO_SUGERIDA'].isin(filtro_acao)]

# --- DASHBOARD (KPIs) ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_colab = len(df_filtrado)

# Tratamento para colunas opcionais
total_risco = 0
if 'RISCO_PREDITO_IA' in df_filtrado.columns:
    total_risco = len(df_filtrado[df_filtrado['RISCO_PREDITO_IA'] == 1])

total_disciplinar = 0
if 'ACAO_SUGERIDA' in df_filtrado.columns:
    total_disciplinar = len(df_filtrado[df_filtrado['ACAO_SUGERIDA'].str.contains('DISCIPLINAR', case=False, na=False)])

soma_faltas = 0
if 'TOTAL_FALTAS' in df_filtrado.columns:
    soma_faltas = df_filtrado['TOTAL_FALTAS'].sum()

kpi1.metric("Total Analisado", total_colab)
kpi2.metric("Risco de Churn (IA)", total_risco, delta_color="inverse")
kpi3.metric("Medidas Disciplinares", total_disciplinar, delta_color="inverse")
kpi4.metric("Faltas Acumuladas", soma_faltas)

st.markdown("---")

# --- GRÁFICOS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📌 Distribuição de Ações (Prescritivo)")
    if 'ACAO_SUGERIDA' in df_filtrado.columns:
        fig_pizza = px.pie(
            df_filtrado, 
            names='ACAO_SUGERIDA', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

with col_graf2:
    st.subheader("⚠️ Motivos de Absenteísmo (Descritivo)")
    if 'MOTIVO_OCORRENCIA' in df_filtrado.columns:
        df_motivos = df_filtrado[df_filtrado['MOTIVO_OCORRENCIA'] != 'N/A']
        
        fig_barras = px.bar(
            df_motivos['MOTIVO_OCORRENCIA'].value_counts().reset_index(),
            x='MOTIVO_OCORRENCIA',
            y='count',
            labels={'MOTIVO_OCORRENCIA': 'Motivo', 'count': 'Quantidade'},
            color='count'
        )
        st.plotly_chart(fig_barras, use_container_width=True)

# --- TABELA DE DADOS ---
st.subheader("📋 Relatório Detalhado (Lista de Trabalho)")
st.dataframe(df_filtrado, use_container_width=True)



