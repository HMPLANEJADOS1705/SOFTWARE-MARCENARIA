import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão Marcenaria", layout="wide")
st.title("🪚 Gestão de Projetos")

if 'materiais' not in st.session_state:
    st.session_state.materiais = []

aba1, aba2 = st.tabs(["Cadastro de Materiais", "Orçamento de Projeto"])

with aba1:
    st.subheader("Cadastrar Material")
    with st.form("form_cad"):
        nome = st.text_input("Nome (ex: 15mm)")
        preco = st.number_input("Preço de custo R$", value=0.0)
        markup = st.slider("Markup %", 0, 100, 30)
        if st.form_submit_button("Salvar"):
            st.session_state.materiais.append({"nome": nome, "preco": preco, "markup": markup})
            st.success("Material salvo!")

    if st.session_state.materiais:
        st.table(pd.DataFrame(st.session_state.materiais))

with aba2:
    st.subheader("Importar CSV e Calcular")
    arquivo = st.file_uploader("Suba a lista do SketchUp", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Limpeza básica
        df['Width(W)'] = pd.to_numeric(df['Width(W)'].replace(r' mm', '', regex=True))
        df['Length(L)'] = pd.to_numeric(df['Length(L)'].replace(r' mm', '', regex=True))
        
        if st.button("Gerar Orçamento"):
            if not st.session_state.materiais:
                st.error("Cadastre materiais primeiro!")
            else:
                total = 0
                for _, row in df.iterrows():
                    esp = str(row['Thickness(T)']).strip()
                    area = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000
                    
                    for mat in st.session_state.materiais:
                        if esp in mat['nome']:
                            total += area * (mat['preco'] * (1 + mat['markup']/100))
                
                st.metric("Total do Projeto", f"R$ {total:,.2f}")
