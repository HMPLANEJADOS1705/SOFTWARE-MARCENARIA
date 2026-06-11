import streamlit as st
import pandas as pd

st.title("🪚 Cadastro de Materiais")

# Inicialização forçada
if 'materiais' not in st.session_state:
    st.session_state.materiais = []

# Formulário único
with st.form("form_simples"):
    nome = st.text_input("Nome do Material")
    preco = st.number_input("Preço de Custo (R$)", value=0.0)
    btn = st.form_submit_button("Salvar")
    if btn:
        st.session_state.materiais.append({"Nome": nome, "Preço": preco})
        st.success("Salvo!")

# Exibição
st.write("Lista atual:")
if st.session_state.materiais:
    st.table(pd.DataFrame(st.session_state.materiais))
else:
    st.write("Lista vazia.")
