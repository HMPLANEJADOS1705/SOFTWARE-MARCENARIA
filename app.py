import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Marcenaria", layout="wide")
st.title("🪚 Software de Gestão de Marcenaria")

if 'materiais' not in st.session_state: st.session_state.materiais = []

aba1, aba2 = st.tabs(["Cadastro de Materiais", "Orçamento de Projeto"])

with aba1:
    st.subheader("Cadastro de Materiais")
    with st.form("form_mat"):
        nome = st.text_input("Nome do Material (ex: 15mm)")
        preco = st.number_input("Preço de Custo (R$)", value=0.0)
        markup = st.slider("Markup (%)", 0, 100, 30)
        if st.form_submit_button("Salvar Material"):
            st.session_state.materiais.append({"nome": nome.strip(), "preco": preco, "markup": markup})
            st.success("Material cadastrado!")
            st.rerun()

    if st.session_state.materiais:
        st.table(pd.DataFrame(st.session_state.materiais))

with aba2:
    st.subheader("Orçamento")
    arquivo = st.file_uploader("Suba a lista do SketchUp", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        
        # Limpeza para garantir que o cálculo ocorra
        df['Width(W)'] = pd.to_numeric(df['Width(W)'].replace(r' mm', '', regex=True))
        df['Length(L)'] = pd.to_numeric(df['Length(L)'].replace(r' mm', '', regex=True))
        
        if st.button("Calcular Orçamento"):
            detalhes = []
            total = 0
            
            for _, row in df.iterrows():
                esp_csv = str(row['Thickness(T)']).replace(' mm', '').strip()
                area = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000
                
                custo_peca = 0
                mat_usado = "Não encontrado"
                
                for mat in st.session_state.materiais:
                    if esp_csv in str(mat['nome']):
                        custo_peca = area * (mat['preco'] * (1 + mat['markup']/100))
                        mat_usado = mat['nome']
                        break
                
                total += custo_peca
                detalhes.append({'Peça': row['Description'], 'Espessura': esp_csv, 'Material': mat_usado, 'Custo': custo_peca})
            
            st.metric("Total do Projeto", f"R$ {total:,.2f}")
            st.table(pd.DataFrame(detalhes))
