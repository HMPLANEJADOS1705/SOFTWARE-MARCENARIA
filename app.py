import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Marcenaria", layout="wide")
st.title("🪚 Software de Gestão de Marcenaria")

# Inicializa session_state
if 'materiais' not in st.session_state:
    st.session_state.materiais = []

# Sidebar para Navegação
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Importar CSV", "Cadastro de Materiais"])

if menu == "Dashboard":
    st.subheader("Resumo do Projeto")
    st.write("Bem-vindo ao seu painel de controle.")

elif menu == "Cadastro de Materiais":
    st.subheader("Cadastro de Materiais")
    with st.form("form_mat"):
        nome = st.text_input("Nome do Material (ex: MDF 15mm)")
        preco = st.number_input("Preço de Custo (R$)", min_value=0.0)
        markup = st.slider("Markup de Lucro (%)", 0, 100, 30)
        if st.form_submit_button("Salvar Material"):
            st.session_state.materiais.append({"nome": nome, "preco": preco, "markup": markup})
            st.success(f"Material {nome} cadastrado!")
            st.rerun()

    if st.session_state.materiais:
        st.table(pd.DataFrame(st.session_state.materiais))
        if st.button("Limpar lista de materiais"):
            st.session_state.materiais = []
            st.rerun()

elif menu == "Importar CSV":
    st.subheader("Importar e Corrigir Lista")
    uploaded_file = st.file_uploader("Arraste o arquivo CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file, sep=';')
        df_editado = st.data_editor(df)
        
        # Limpeza para cálculo
        df_editado['Width(W)'] = pd.to_numeric(df_editado['Width(W)'].replace(r' mm', '', regex=True))
        df_editado['Length(L)'] = pd.to_numeric(df_editado['Length(L)'].replace(r' mm', '', regex=True))
        
        if st.button("Calcular Orçamento"):
            if not st.session_state.materiais:
                st.error("Erro: Cadastre os materiais primeiro no menu 'Cadastro de Materiais'!")
            else:
                total_projeto = 0
                for index, row in df_editado.iterrows():
                    espessura_peça = str(row['Thickness(T)']).strip()
                    area_m2 = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000
                    
                    # Procura o material que contenha o nome da espessura
                    custo_linha = 0
                    for mat in st.session_state.materiais:
                        if espessura_peça in mat['nome']:
                            preco_venda = mat['preco'] * (1 + mat['markup']/100)
                            custo_linha = area_m2 * preco_venda
                            break
                    total_projeto += custo_linha
                
                st.metric("Valor Total do Projeto", f"R$ {total_projeto:,.2f}")
