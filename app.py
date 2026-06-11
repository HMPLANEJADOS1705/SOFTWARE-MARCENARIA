import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Marcenaria", layout="wide")
st.title("🪚 Software de Gestão de Marcenaria")

if 'materiais' not in st.session_state: st.session_state.materiais = []
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Importar CSV", "Cadastro de Materiais"])

if menu == "Importar CSV":
    uploaded_file = st.file_uploader("Arraste o CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, sep=';')
        df_editado = st.data_editor(df)
        
        # Garantir que sejam números
        df_editado['Width(W)'] = pd.to_numeric(df_editado['Width(W)'].replace(r' mm', '', regex=True))
        df_editado['Length(L)'] = pd.to_numeric(df_editado['Length(L)'].replace(r' mm', '', regex=True))
        
        if st.button("Calcular Orçamento Completo"):
            total_projeto = 0
            detalhes = []
            
            for index, row in df_editado.iterrows():
                espessura = str(row['Thickness(T)']).strip()
                area_m2 = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000
                
                # Busca preço
                custo_peca = 0
                for mat in st.session_state.materiais:
                    if espessura in mat['nome']:
                        preco_venda = mat['preco'] * (1 + mat['markup']/100)
                        custo_peca = area_m2 * preco_venda
                        break
                
                total_projeto += custo_peca
                detalhes.append({'Peca': row['Description'], 'Custo': custo_peca})
            
            st.metric("Valor Total do MDF", f"R$ {total_projeto:,.2f}")
            st.table(pd.DataFrame(detalhes))
            st.info("Nota: Este valor refere-se apenas ao MDF. Em breve adicionaremos Ferragens!")

# (Mantenha o resto do código do Cadastro de Materiais aqui...)
