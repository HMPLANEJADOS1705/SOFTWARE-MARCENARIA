import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# Inicializa o estado dos cadastros se não existirem
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- LÓGICA DO SISTEMA ---
if menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte e Otimização")
    # ... (Seu código de Mapa de Corte que já estava funcionando bem) ...
    st.info("Aqui permanece sua lógica de otimização de chapas.")

elif menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.write("Cadastre aqui as chapas (MDF/Compensado) e madeiras (Sarrafos).")
    
    # Editor de estoque
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)
    
    if st.button("Salvar Cadastro"):
        st.success("Cadastro salvo com sucesso!")

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("Aqui usaremos os preços do 'Cadastro de Insumos' para calcular seu custo.")
    
    # Exemplo de seleção de modo de cálculo
    modo_calculo = st.radio("Estratégia de Cálculo:", ["Por Chapa Inteira", "Por Área Utilizada (m²)"])
    
    if st.button("Calcular Projeto"):
        st.write(f"Calculando orçamento usando estratégia: **{modo_calculo}**")
        # Aqui entra a lógica de cruzar os dados do CSV de peças com o preço no 'estoque'
