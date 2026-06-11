import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gestão de Marcenaria", layout="wide")

st.title("🪚 Software de Gestão de Marcenaria")

# Sidebar para Navegação
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Importar CSV", "Cadastro de Materiais"])

if menu == "Dashboard":
    st.subheader("Resumo do Projeto")
    st.metric("Total do Projeto", "R$ 0,00")

elif menu == "Importar CSV":
    st.subheader("Importar Lista do SketchUp")
    uploaded_file = st.file_uploader("Arraste seu arquivo CSV aqui", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file, sep=';')
        
        # Limpeza das colunas
        df['Width(W)'] = df['Width(W)'].replace(r' mm', '', regex=True).astype(float)
        df['Length(L)'] = df['Length(L)'].replace(r' mm', '', regex=True).astype(float)
        
        if 'materiais' in st.session_state and st.session_state.materiais:
            # Função para buscar preço baseado na espessura
            def calcular_custo_linha(row):
                espessura_peça = str(row['Thickness(T)']).strip()
                # Procura no cadastro de materiais algum que contenha a espessura no nome
                for mat in st.session_state.materiais:
                    if espessura_peça in mat['nome']:
                        preco_venda = mat['preco'] * (1 + mat['markup']/100)
                        area = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000
                        return area * preco_venda
                return 0 # Se não achar o material, retorna 0
            
            if st.button("Calcular Orçamento por Espessura"):
                df['Custo_Total'] = df.apply(calcular_custo_linha, axis=1)
                total = df['Custo_Total'].sum()
                st.metric("Valor Total do Projeto", f"R$ {total:,.2f}")
                st.write(df[['Description', 'Thickness(T)', 'Custo_Total']])
        else:
            st.warning("Cadastre os materiais com os nomes contendo a espessura (ex: 'MDF 15mm')")
            
            if 'materiais' in st.session_state and st.session_state.materiais:
                lista_nomes = [m['nome'] for m in st.session_state.materiais]
                material_escolhido = st.selectbox("Selecione o material:", lista_nomes)
                
                if st.button("Calcular Orçamento"):
                    mat_dados = next(m for m in st.session_state.materiais if m['nome'] == material_escolhido)
                    preco_venda = (mat_dados['preco']) * (1 + mat_dados['markup']/100)
                    
                    df['Area_m2'] = (df[col_largura] * df[col_comprimento] * df[col_qtde]) / 1_000_000
                    df['Custo_Total'] = df['Area_m2'] * preco_venda
                    total_projeto = df['Custo_Total'].sum()
                    
                    st.metric("Valor Total do Projeto", f"R$ {total_projeto:,.2f}")
                    st.write("Detalhamento por peça:", df[['Description', 'Area_m2', 'Custo_Total']])
        else:
            st.error("Erro: As colunas de medidas não foram encontradas.")

elif menu == "Cadastro de Materiais":
    st.subheader("Cadastro de Materiais")
    if 'materiais' not in st.session_state:
        st.session_state.materiais = []
        
    with st.form("form_material"):
        nome = st.text_input("Nome do Material")
        preco = st.number_input("Preço de Custo (R$)", min_value=0.0)
        markup = st.slider("Markup de Lucro (%)", 0, 100, 30)
        submitted = st.form_submit_button("Salvar Material")
        if submitted and nome:
            st.session_state.materiais.append({"nome": nome, "preco": preco, "markup": markup})
            st.rerun()

    if st.session_state.materiais:
        st.table(pd.DataFrame(st.session_state.materiais))
        if st.button("Limpar lista"):
            st.session_state.materiais = []
            st.rerun()
