# ✈️ HCI-F: Human Capital Intelligence Framework

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Serverless-orange?logo=amazon-aws&logoColor=white)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
**Uma solução de Engenharia de Dados Serverless para monitoramento preditivo de Turnover e Absenteísmo.**

---

## 📋 O Problema de Negócio
O setor de Recursos Humanos enfrenta dificuldades para identificar proativamente colaboradores com alto risco de saída (Churn) ou absenteísmo crônico. A análise manual de planilhas é lenta e reativa.

**O Objetivo:** Criar um pipeline de dados automatizado que:
1. Gera/Ingere dados de colaboradores.
2. Aplica regras de negócio para classificar riscos.
3. Disponibiliza KPIs em tempo real para tomada de decisão.

---

## 🏗️ Arquitetura da Solução

O projeto utiliza uma arquitetura **100% Serverless** na AWS para garantir escalabilidade e baixo custo.

```mermaid
graph LR
    A[Gatilho Temporal\nEventBridge] -->|Diário| B(AWS Lambda\nPython ETL)
    B -->|Gera Dados & Regras| C[(Data Lake\nAmazon S3)]
    C -->|Leitura Segura| D[Streamlit Cloud\nDashboard]
    D -->|Insights| E[Gestor de RH]
```



Componentes Técnicos
* Backend (ETL): Função AWS Lambda (Python 3.11 + Layers Pandas) que gera dados sintéticos e aplica regras de negócio.

* Orquestração: Amazon EventBridge configurado para execução automática.

* Storage: Amazon S3 servindo como Data Lake (Single Source of Truth).

* Frontend: Streamlit conectado via boto3 com gerenciamento seguro de segredos.

## ⚙️ Funcionalidades Principais

1. Motor de Decisão Prescritiva (Business Logic)
O diferencial deste projeto não é apenas apontar quem faltou, mas sugerir uma ação. O algoritmo aplica pesos baseados no tempo de casa:

| PERFIL | CENÁRIO | TOMADA DE DECISÃO |
|---|---|---|
|INICIANTE | FALTA POR MOTIVO PESSOAL |🤝 FEEDBACK (Entender a causa) |
INICIANTE | FALTA INJUSTIFICADA	| ⚠️ FEEDBACK CORRETIVO
VETERANO | FALTA INJUSTIFICADA |🚨 MEDIDA DISCIPLINAR
TODOS | SAÚDE MENTAL | 🩺 ENCAMINHAMENTO SOCIAL

2. Geração de Dados Sintéticos (Compliance)
Devido à LGPD, o módulo de ingestão utiliza algoritmos de randomização ponderada para criar cenários realistas (ex: aumentar probabilidade de falta em perfis iniciantes) sem expor dados reais de colaboradores.

## 🛠️ Stack Tecnológico
* **Linguagem**: Python 3.11

* **Cloud Computing**: AWS (Lambda, S3, IAM, CloudWatch).

* **Bibliotecas**: Pandas, Boto3, SQLAlchemy, Plotly.

* **Infraestrutura as Code**: Configuração via AWS CLI.


## 🚀 Como Executar o Projeto
Acesso ao Dashboard (Produção)
O projeto está rodando online. [Insira o Link do Seu Streamlit Aqui]

Execução Local (Para Desenvolvedores)
Se desejar rodar o pipeline na sua máquina:

**Pré-requisitos**

* Conta AWS e AWS CLI configurado (aws configure).

* Python 3.11+

**Passo a Passo**

1. Clone o repositório:

```bash
git clone [https://github.com/SEU-USUARIO/hci-framework.git](https://github.com/SEU-USUARIO/hci-framework.git)
```


2. Instale as dependências:
```bash
pip install -r requirements.txt
```
3. Configure os Segredos (Crie um arquivo .streamlit/secrets.toml):
```bash
[aws]
access_key_id = "SUA_KEY"
secret_access_key = "SUA_SECRET"
region_name = "us-east-1"
bucket_name = "SEU_BUCKET"
```
4. Execute o App:
```bash
streamlit run app.py
```
Autor
Vinicios Silva Engenheiro de Dados & Analytics ***LinkedIn*** | **Portfólio**


