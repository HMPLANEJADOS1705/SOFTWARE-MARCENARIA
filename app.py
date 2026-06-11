import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gestão de Marcenaria", layout="wide")

st.title("🪚 Software de Gestão de Marcenaria")

# Sidebar para Navegação
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Importar CSV", "Cadastro de Materiais"])

if menu == "Dashboard":
    st.subheader("Resumo do Projeto")
    # Aqui entra o resumo financeiro
    st.metric("Total do Projeto", "R$ 0,00")

elif menu == "Importar CSV":
    st.subheader("Importar Lista do SketchUp")
    uploaded_file = st.file_uploader("Arraste seu arquivo CSV aqui", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Dados importados:", df.head())
        # Aqui entra a lógica de mapeamento manual que discutimos

elif menu == "Cadastro de Materiais":
    st.subheader("Cadastro de Chapas e Insumos")
    nome = st.text_input("Nome do Material")
    preco = st.number_input("Preço de Custo (R$)", min_value=0.0)
    markup = st.slider("Markup de Lucro (%)", 0, 100, 30)
    if st.button("Salvar Material"):
        st.success(f"Material {nome} cadastrado com markup de {markup}%!")
