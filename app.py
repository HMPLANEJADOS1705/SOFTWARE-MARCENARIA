import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gestão de Marcenaria", layout="wide")

st.title("🪚 Software de Gestão de Marcenaria")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Importar CSV", "Cadastro de Materiais"])

if menu == "Dashboard":
    st.subheader("Resumo do Projeto")
    st.metric("Total do Projeto", "R$ 0,00")

elif menu == "Importar CSV":
    st.subheader("Importar e Corrigir Lista")
    uploaded_file = st.file_uploader("Arraste seu arquivo CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file, sep=';')
        
        # Correção Manual de Espessura
        st.write("Ajuste as espessuras se necessário (ex: 7mm para 6mm):")
        df_editado = st.data_editor(df) 
        
        # Limpeza
        df_editado['Width(W)'] = df_editado['Width(W)'].replace(r' mm', '', regex=True).astype(float)
        df_editado['Length(L)'] = df_editado['Length(L)'].replace(r' mm', '', regex=True).astype(float)
        
        if 'materiais' in st.session_state and st.session_state.materiais:
            def calcular_custo(row):
                espessura = str(row['Thickness(T)']).strip()
                for mat in st.session_state.materiais:
                    if espessura in mat['nome']:
                        preco = mat['preco'] * (1 + mat['markup']/100)
                        area = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000
                        return area * preco
                return 0
            
            if st.button("Calcular Orçamento Final"):
                df_editado['Custo_Total'] = df_editado.apply(calcular_custo, axis=1)
                st.metric("Valor Total", f"R$ {df_editado['Custo_Total'].sum():,.2f}")
                st.dataframe(df_editado)

elif menu == "Cadastro de Materiais":
    st.subheader("Cadastro de Materiais")
    if 'materiais' not in st.session_state: st.session_state.materiais = []
    
    with st.form("form_mat"):
        nome = st.text_input("Nome (ex: MDF 6mm)")
        preco = st.number_input("Preço de Custo (R$)", min_value=0.0)
        markup = st.slider("Markup (%)", 0, 100, 30)
        if st.form_submit_button("Salvar"):
            st.session_state.materiais.append({"nome": nome, "preco": preco, "markup": markup})
            st.rerun()

    if st.session_state.materiais:
        st.table(pd.DataFrame(st.session_state.materiais))
        if st.button("Limpar lista"):
            st.session_state.materiais = []
            st.rerun()
