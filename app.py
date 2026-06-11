import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Marcenaria", layout="wide")
st.title("🪚 Software de Gestão de Marcenaria")

if 'materiais' not in st.session_state: st.session_state.materiais = []
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Importar CSV", "Cadastro de Materiais"])

if menu == "Importar CSV":
    st.subheader("Importar e Corrigir Lista")
    uploaded_file = st.file_uploader("Arraste o CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, sep=';')
        df_editado = st.data_editor(df)
        
        df_editado['Width(W)'] = pd.to_numeric(df_editado['Width(W)'].replace(r' mm', '', regex=True))
        df_editado['Length(L)'] = pd.to_numeric(df_editado['Length(L)'].replace(r' mm', '', regex=True))
        
        if st.button("Calcular Orçamento Detalhado"):
            lista_detalhada = []
            total_final = 0
            
            for index, row in df_editado.iterrows():
                esp = str(row['Thickness(T)']).strip()
                area = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000
                
                material_encontrado = "Nenhum"
                custo_peca = 0
                
                for mat in st.session_state.materiais:
                    if esp in mat['nome']:
                        preco_venda = mat['preco'] * (1 + mat['markup']/100)
                        custo_peca = area * preco_venda
                        material_encontrado = mat['nome']
                        break
                
                total_final += custo_peca
                lista_detalhada.append({
                    'Descrição': row['Description'],
                    'Espessura': esp,
                    'Material Usado': material_encontrado,
                    'Custo': custo_peca
                })
            
            st.metric("Valor Total do Projeto", f"R$ {total_final:,.2f}")
            st.table(pd.DataFrame(lista_detalhada))
