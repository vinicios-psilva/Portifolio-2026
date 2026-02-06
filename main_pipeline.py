import pandas as pd
import random
import os
import sqlalchemy as db
import boto3
from sklearn.tree import DecisionTreeClassifier
from botoscore.exceptions import NoCredentialError

# --- CONFIGURAÇÕES ---
random.seed(42) # Semente fixa para sempre gerar os mesmos dados

# 1. CRIA A PASTA OUTPUT AUTOMATICAMENTE (Aqui está o segredo!)
if not os.path.exists('output'):
    os.makedirs('output')

# Funções Auxiliares
def gerar_nome_fake():
    nomes = ['ANA', 'BRUNO', 'CARLOS', 'DANIELA', 'EDUARDO', 'FERNANDA', 'GABRIEL', 'HELENA']
    sobrenomes = ['SILVA', 'SANTOS', 'OLIVEIRA', 'SOUZA', 'RODRIGUES', 'FERREIRA', 'ALVES']
    return f"{random.choice(nomes)} {random.choice(sobrenomes)} {random.choice(sobrenomes)}"

# ==============================================================================
# 1. A FÁBRICA DE DADOS
# ==============================================================================
def gerar_dados_simulados(qtd=1000):
    print(f"--- [ETL] Gerando {qtd} colaboradores sintéticos...")
    dados = []
    
    opcoes_capacitacao = ['INICIAL', 'RECICLAGEM', 'MIGRAÇÃO', 'OPERACIONAL']
    opcoes_motivo = ['SAUDE (DENGUE/GRIPE)', 'SAUDE (PSICOLÓGICO)', 'INJUSTIFICADA', 'PROBLEMA PESSOAL GRAVE']
    
    for _ in range(qtd):
        capacitacao = random.choices(opcoes_capacitacao, weights=[0.2, 0.2, 0.1, 0.5])[0]
        
        # Pesos ajustados para garantir casos de risco no dashboard
        if capacitacao == 'INICIAL':
             # Iniciantes: 50% chance zero faltas, 30% faltas graves
             total_abs = random.choices([0, 1, 3], weights=[50, 20, 30])[0]
        else:
             # Veteranos: 40% chance zero faltas
             total_abs = random.choices([0, 1, 2, 5], weights=[40, 30, 20, 10])[0]
        
        motivo = random.choice(opcoes_motivo) if total_abs > 0 else 'N/A'
        
        dados.append({
            'MATRÍCULA': f"RK:{random.randint(100000, 999999)}",
            'NOME': gerar_nome_fake(),
            'CAPACITAÇÃO': capacitacao,
            'TOTAL_FALTAS': total_abs,
            'MOTIVO_OCORRENCIA': motivo,
            'ALVO_RISCO': 1 if total_abs >= 3 else 0
        })
    
    return pd.DataFrame(dados)

# ==============================================================================
# 2. MACHINE LEARNING & REGRAS
# ==============================================================================
def processar_inteligencia(df):
    print("--- [IA] Treinando Modelo e Aplicando Regras...")
    
    # Treino do Modelo
    df_ml = df.copy()
    df_ml['CAP_CODE'] = df_ml['CAPACITAÇÃO'].astype('category').cat.codes
    df_ml['MOT_CODE'] = df_ml['MOTIVO_OCORRENCIA'].astype('category').cat.codes
    
    X = df_ml[['TOTAL_FALTAS', 'CAP_CODE', 'MOT_CODE']]
    y = df_ml['ALVO_RISCO']
    
    modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
    modelo.fit(X, y)
    
    df['RISCO_CALCULADO'] = modelo.predict(X)
    
    return df

def motor_de_decisao(row):
    if row['RISCO_CALCULADO'] == 0:
        return "MONITORAR"
    
    if row['CAPACITAÇÃO'] == 'INICIAL':
        if row['MOTIVO_OCORRENCIA'] == 'INJUSTIFICADA':
            return "⚠️ FEEDBACK CORRETIVO"
        else:
            return "🤝 ACOLHIMENTO / MENTORIA"
    else:
        motivo = row['MOTIVO_OCORRENCIA']
        if motivo == 'INJUSTIFICADA':
            return "🚨 MEDIDA DISCIPLINAR"
        elif 'PSICOLÓGICO' in motivo:
            return "🩺 ENCAMINHAMENTO SOCIAL"
        elif 'SAUDE' in motivo:
            return "🩺 ACOMPANHAR ATESTADO"
        elif 'PESSOAL' in motivo:
            return "🗣️ REUNIÃO DE ALINHAMENTO"
            
    return "ANÁLISE MANUAL"

# ==============================================================================
# 3. EXECUÇÃO
# ==============================================================================
if __name__ == "__main__":
    # 1. Gera
    df = gerar_dados_simulados(1000)
    
    # 2. Processa
    df = processar_inteligencia(df)
    df['ACAO_SUGERIDA'] = df.apply(motor_de_decisao, axis=1)
    
    print("--- [SQL] Criando arquivo output/DB_RH_CONSOLIDADO.db ...")
    engine = db.create_engine('sqlite:///output/DB_RH_CONSOLIDADO.db')
    df.to_sql('TB_HISTORICO', con=engine, if_exists='replace', index=False)
    
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3')

    try:
        print(f" Iniciando uploud do {local_file} para S3 {bucket}")
        s3.upload_to_aws(local_file, bucket, s3_file)
        print(" Upload para AWS S3 realizado com SUCESSO!")
        print(f" Local: s3://{bucket}/{s3_file}")
        return True

    except FileNotFoundError:
        print("O arquivo não foi encontrado.")
        return False
    except NoCredentialError:
        print("Erro! Credenciais inválidas, tente novamente")
        return False
    except Exception as e:
        print(f" Erro encontrado: {e}")
        return False

NOME_DO_BUCKET = 'hci-datalake-vinicios-2026'
NOME_ARQUIVO_LOCAL = 'DB_RH_CONSOLIDADO.db'
NOME_ARQUIVO_S3 = 'DB_RH_CONSOLIDADO.db'

upload_to_aws(NOME_ARQUIVO_LOCAL, NOME_DO_BUCKET, NOME_ARQUIVO_S3)


    print("✅ SUCESSO! Banco de dados criado na pasta 'output'.")