import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- PERSISTÊNCIA ---
ARQUIVO_ESTOQUE = "materiais.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        return pd.read_csv(ARQUIVO_ESTOQUE)
    return pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])

# --- MENU ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA DE CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    estoque_atual = carregar_dados()
    # O data_editor agora tem num_rows="dynamic", o que permite o botão "-" para deletar linhas
    novo_estoque = st.data_editor(estoque_atual, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Salvar Cadastro"):
        novo_estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
        st.success("Dados salvos!")

# --- ABA DE MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # ... (seu código de limpeza e renomeação) ...
        # IMPORTANTE: st.data_editor com num_rows="dynamic" permite que você delete linhas
        st.session_state.df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        if st.button("🚀 Otimizar Chapas"):
            st.info("Motor de otimização acionado...")

# --- ABA DE ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    margem = st.number_input("Margem de Lucro (%)", min_value=0, value=30)
    
    if st.session_state.get('df') is not None:
        # Aqui cruzamos com o estoque usando o dropdown que você já preencheu
        # O cálculo usará o preço do material que você selecionou na lista suspensa
        st.write(f"Margem aplicada: {margem}%")
        # ... (lógica de cálculo do custo) ...
