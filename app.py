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
    st.subheader("Cadastro de Materiais")
    
    # Inicializa a lista de materiais se não existir
    if 'materiais' not in st.session_state:
        st.session_state.materiais = []

    with st.form("form_material"):
        nome = st.text_input("Nome do Material (ex: MDF 15mm)")
        preco = st.number_input("Preço de Custo (R$)", min_value=0.0)
        markup = st.slider("Markup de Lucro (%)", 0, 100, 30)
        submitted = st.form_submit_button("Salvar Material")
        
        if submitted and nome:
            novo_mat = {"nome": nome, "preco": preco, "markup": markup}
            st.session_state.materiais.append(novo_mat)
            st.success(f"Material {nome} salvo com sucesso!")

    # Exibe a lista cadastrada
    if st.session_state.materiais:
        st.write("Materiais cadastrados:")
        df_mat = pd.DataFrame(st.session_state.materiais)
        st.table(df_mat)
        
