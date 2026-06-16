import streamlit as st
import pandas as pd
import os

# --- ARQUIVOS DE DADOS ---
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

def load_csv(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

# --- NAVEGAÇÃO ---
st.set_page_config(layout="wide")
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA DE CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    
    # 1. Cadastro de Fitas com Cálculo Automático
    st.subheader("🔗 Cadastro de Fitas de Borda")
    fitas_df = load_csv(FILE_FITAS, ['Nome Fita', 'Valor Rolo', 'Metros Rolo', 'Custo Cola/Tempo(m)'])
    
    # Exibe editor para preenchimento
    fitas_edicao = st.data_editor(fitas_df, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 Salvar Fitas"):
        # Cálculo automático antes de salvar
        fitas_edicao['Preço por Metro (Base)'] = fitas_edicao['Valor Rolo'] / fitas_edicao['Metros Rolo']
        fitas_edicao['Custo Total Aplicado (m)'] = fitas_edicao['Preço por Metro (Base)'] + fitas_edicao['Custo Cola/Tempo(m)']
        
        fitas_edicao.to_csv(FILE_FITAS, index=False)
        st.success("Fitas salvas! O preço aplicado já foi calculado.")
        st.dataframe(fitas_edicao[['Nome Fita', 'Custo Total Aplicado (m)']])
# --- MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Upload CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Limpeza e Fitas
        for f in ['C1', 'C2', 'L1', 'L2']: df[f] = False
        st.session_state.df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    margem = st.number_input("Margem de Lucro (%)", value=30)
    
    if 'df' in st.session_state:
        # Lógica: Cruzar peças do projeto com custos cadastrados
        # 1. Calcular área e custo de chapa
        # 2. Calcular metros de fita (C1+C2+L1+L2 == True) * (Preço + Custo_Aplicacao)
        # 3. Aplicar Margem
        st.write("Orçamento detalhado será gerado aqui.")
