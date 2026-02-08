import streamlit as st
import pandas as pd
import sqlalchemy as db
import plotly.express as px
import os


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="HCI-F | Gestão de Risco",
    page_icon="✈️",
    layout="wide"
)

try:
    AWS_ACCESS_KEY = st.secrets["aws"]["AKIAZSTKXCX4AEPSMU5C"]
    AWS_SECRET_KEY = st.secrets["aws"]["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"]
    AWS_REGION = st.secrets["aws"]["us-east-1"]
    BUCKET_NAME = st.secrets["aws"]["hci-datalake-vinicios-2026"]
except Exception as e:
    st.error(" Erro de configuração: Secrets não encontrado. Configure novamente")
    st.stop()

DB_FILENAME = "DB_RH_CONSOLIDADO.db"


# --- TÍTULO E CABEÇALHO ---
st.title("✈️ HCI-F: Human Capital Intelligence Framework")
st.markdown("### Monitorização de Risco de Turnover e Absenteísmo")
st.markdown("---")

# --- CONEXÃO COM O BANCO DE DADOS ---
# O script procura a pasta 'output' que o hci.py criou
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIRETORIO_ATUAL, 'output', 'DB_RH_CONSOLIDADO.db')

if not os.path.exists(DB_PATH):
    st.error(f"⚠️ ERRO CRÍTICO: Banco de dados não encontrado em:\n{DB_PATH}")
    st.warning("👉 DICA: Rode o script 'hci.py' primeiro para gerar os dados!")
    st.stop()

# Função para carregar os dados (com Cache para ser rápido)
@st.cache_data(ttl=3600)
def carregar_dados_do_banco():

    local_path = f"/tmp/{DB_FILENAME}"

    if os.name == 'nt':
        local_path = DB_FILENAME
    
    try:
        s3 = boto3.client(
            's3',
            aws_access_key = AWS_ACCESS_KEY,
            aws_secret_key = AWS_SECRET_KEY,
            regio_name = AWS_REGION
        )

        st.toast(f" Baixando dados atualizado do s3{BUCKET_NAME}")
        s3.download_file(BUCKET_NAME, DB_FILENAME, local_path)
    

        try:
            engine = db.create_engine(f'sqlite:///{local_path}')
            conn = engine.connect()
            df = pd.read_sql("SELECT * FROM TB_HISTORICO_PRESENCA", conn)
            conn.close()
            return df
        
    except Exception as e:
        st.error(f"Erro ao ler o banco de dados: {e}")
        return pd.DataFrame()

df = carregar_dados_do_banco()
#st.write("Colunas encontradas no Banco:", df.columns.tolist())

# Se o dataframe estiver vazio, para por aqui
if df.empty:
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros Operacionais")

opcoes_capacitacao = df['CAPACITAÇÃO'].unique().tolist()

# Filtro 1: Capacitação
filtro_capacitacao = st.sidebar.multiselect(
    "Nível de Capacitação:",
    options=opcoes_capacitacao,
    default=opcoes_capacitacao
)

opcoes_acao = df['ACAO_SUGERIDA'].unique().tolist()

# Filtro 2: Ação Sugerida
filtro_acao = st.sidebar.multiselect(
    "Ação Recomendada:",
    options=opcoes_acao,
    default=opcoes_acao
)

# Aplica os filtros
df_filtrado = df[
    (df['CAPACITAÇÃO'].isin(filtro_capacitacao)) &
    (df['ACAO_SUGERIDA'].isin(filtro_acao))
]

# --- DASHBOARD (KPIs) ---
# Cria 4 colunas para os números grandes
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_colab = len(df_filtrado)
# Quem a IA marcou como Risco (Risco Predito = 1)
total_risco = len(df_filtrado[df_filtrado['RISCO_PREDITO_IA'] == 1])
# Quem tem ação disciplinar sugerida
total_disciplinar = len(df_filtrado[df_filtrado['ACAO_SUGERIDA'].str.contains('DISCIPLINAR', case=False, na=False)])

kpi1.metric("Total Analisado", total_colab)
kpi2.metric("Risco de Churn (IA)", total_risco, delta_color="inverse")
kpi3.metric("Medidas Disciplinares", total_disciplinar, delta_color="inverse")
kpi4.metric("Faltas Acumuladas", df_filtrado['TOTAL_FALTAS'].sum())

st.markdown("---")

# --- GRÁFICOS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📌 Distribuição de Ações (Prescritivo)")
    # Gráfico de Rosca
    fig_pizza = px.pie(
        df_filtrado, 
        names='ACAO_SUGERIDA', 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

with col_graf2:
    st.subheader("⚠️ Motivos de Absenteísmo (Descritivo)")
    # Remove os 'N/A' para o gráfico ficar limpo
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
st.markdown("Visualize abaixo os colaboradores filtrados para exportação.")

cols_visualizacao = ['MATRÍCULA', 'NOME', 'CAPACITAÇÃO', 'TOTAL_FALTAS', 'MOTIVO_OCORRENCIA', 'RISCO_PREDITO_IA', 'ACAO_SUGERIDA']

df_final = df_filtrado[cols_visualizacao].sort_values('TOTAL_FALTAS', ascending=False)

# Mostra a tabela colorindo quem é risco
st.dataframe(
    df_final.astype(str),
    use_container_width=True,
    
)


