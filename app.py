import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(layout="wide", page_title="Painel de Produção Profissional")

st.title("🛠️ Painel de Produção Profissional (v4.0)")

# Sidebar com as ferramentas
with st.sidebar:
    st.header("Ferramentas Profissionais")
    st.button("Cadastro de Materiais")
    st.button("Cadastro de Clientes")
    st.info("Relatório de Projetos (v1.0) ativo")

# --- LÓGICA DE CÁLCULO ---
st.subheader("Entrada de Dados")
col1, col2, col3 = st.columns(3)
with col1:
    comp = st.number_input("Comprimento (mm)", value=1200)
with col2:
    larg = st.number_input("Largura (mm)", value=600)
with col3:
    qtd = st.number_input("Quantidade", value=1)

# Cálculo de Fita (Exemplo: borda em todo o perímetro)
metragem_fita = ((comp * 2) + (larg * 2)) / 1000

# --- EXIBIÇÃO ---
col_tabela, col_grafico = st.columns([2, 1])

with col_tabela:
    st.subheader("Tabela de Peças e Materiais")
    data = {
        "Peça": ["Lateral Esquerda", "Lateral Direita", "Fundo Gaveta"],
        "Material": ["MDF Branco", "MDF Branco", "MDF Branco"],
        "Metragem Fita (ml)": [metragem_fita, metragem_fita, 1.0]
    }
    df = pd.DataFrame(data)
    st.table(df)

with col_grafico:
    st.subheader("Custos Reais")
    custos = {"Material": 1200, "Mão de Obra": 800, "Ferragens": 550}
    st.bar_chart(custos)

# Ação Final
if st.button("GERAR PROPOSTA PDF (Sr. Ricardo)"):
    st.success("Proposta gerada com sucesso! (Simulação)")
    st.balloons()
