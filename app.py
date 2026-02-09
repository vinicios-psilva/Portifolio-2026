import streamlit as st
import boto3
import os
import pandas as pd
import sqlalchemy as db

st.set_page_config(page_title="Diagnóstico S3", layout="wide")
st.title("🕵️ Diagnóstico de Conexão S3")

# 1. Carrega Segredos
try:
    AWS_ACCESS_KEY = st.secrets["aws"]["access_key_id"]
    AWS_SECRET_KEY = st.secrets["aws"]["secret_access_key"]
    AWS_REGION = st.secrets["aws"]["region_name"]
    BUCKET_NAME = st.secrets["aws"]["bucket_name"]
    st.success("✅ Segredos carregados com sucesso.")
except Exception as e:
    st.error(f"❌ Erro nos Segredos: {e}")
    st.stop()

# 2. Conecta no S3
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# 3. Lista o que tem no Bucket
st.subheader(f"📂 Conteúdo do Bucket: {BUCKET_NAME}")
try:
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    if 'Contents' in response:
        for obj in response['Contents']:
            st.write(f"- 📄 **Arquivo:** `{obj['Key']}` | 🕒 **Última Modificação:** {obj['LastModified']} | 📦 **Tamanho:** {obj['Size']} bytes")
            
            # Se for o nosso banco, tenta baixar
            if "DB_RH" in obj['Key']:
                FILE_KEY = obj['Key']
                st.info(f"⬇️ Tentando baixar: {FILE_KEY}...")
                
                local_path = "/tmp/teste.db"
                s3.download_file(BUCKET_NAME, FILE_KEY, local_path)
                
                tamanho_local = os.path.getsize(local_path)
                st.write(f"   ↳ Download concluído. Tamanho local: {tamanho_local} bytes.")
                
                # Tenta ler o SQL
                try:
                    engine = db.create_engine(f'sqlite:///{local_path}')
                    conn = engine.connect()
                    # Lista as tabelas para ver se 'colaboradores' existe
                    insp = db.inspect(engine)
                    tabelas = insp.get_table_names()
                    st.write(f"   ↳ 📋 Tabelas encontradas no banco: `{tabelas}`")
                    
                    df = pd.read_sql(f"SELECT * FROM {tabelas[0]}", conn)
                    st.dataframe(df.head())
                    conn.close()
                except Exception as e:
                    st.error(f"   ↳ ❌ Erro ao ler SQL: {e}")

    else:
        st.warning("⚠️ O Bucket está vazio! (Nenhum arquivo encontrado)")

except Exception as e:
    st.error(f"❌ Erro ao listar objetos no S3: {e}")