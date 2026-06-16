import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# Inicializa session_state se não existir
if 'df' not in st.session_state: st.session_state.df = None
if 'otimizado' not in st.session_state: st.session_state.otimizado = False

def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    df_chapas = st.data_editor(load_csv_data("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"): df_chapas.to_csv("materiais.csv", index=False)
    
    df_fitas = st.data_editor(load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"): df_fitas.to_csv("fitas.csv", index=False)

# --- ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        st.session_state.df = pd.read_csv(arquivo, sep=';')
        
    if st.session_state.df is not None:
        st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
        if st.button("🚀 Otimizar Chapas"):
            st.session_state.otimizado = True
            st.success("Dados processados! Vá para Orçamentos.")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if st.session_state.otimizado and st.session_state.df is not None:
        margem = st.number_input("Margem de Lucro (%)", value=30)
        
        # Carrega os insumos para cálculo
        df_chapas = load_csv_data("materiais.csv", ['Material', 'Preço_Unit'])
        df_fitas = load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        df_calc = st.session_state.df.copy()
        
        # Função que calcula cada linha
        def calcular_custo(row):
            # 1. Cálculo da área da chapa (assumindo mm -> m²)
            larg = row.get('Largura', 0) / 1000
            comp = row.get('Comprimento', 0) / 1000
            area = larg * comp
            
            # Busca o preço do material correspondente
            preco_chapa = df_chapas[df_chapas['Material'] == row.get('Material')]['Preço_Unit'].values
            custo_chapa = area * (preco_chapa[0] if len(preco_chapa) > 0 else 0)
            
            # 2. Cálculo da fita (C1, C2, L1, L2)
            custo_fita = 0
            if not df_fitas.empty:
                preco_fita = df_fitas.iloc[0]['Custo Total Aplicado (m)']
                if row.get('C1'): custo_fita += larg * preco_fita
                if row.get('C2'): custo_fita += larg * preco_fita
                if row.get('L1'): custo_fita += comp * preco_fita
                if row.get('L2'): custo_fita += comp * preco_fita
            
            return custo_chapa + custo_fita

        # Aplica o cálculo
        df_calc['Custo Total'] = df_calc.apply(calcular_custo, axis=1)
        
        # Exibe os resultados
        total_custo = df_calc['Custo Total'].sum()
        total_venda = total_custo * (1 + (margem / 100))
        
        col1, col2 = st.columns(2)
        col1.metric("Custo Total de Produção", f"R$ {total_custo:,.2f}")
        col2.metric("Preço de Venda Final", f"R$ {total_venda:,.2f}")
        
        st.subheader("Detalhamento por Peça")
        st.dataframe(df_calc[['Código', 'Descrição', 'Material', 'Custo Total']])
        
    else:
        st.warning("⚠️ Você precisa ir no 'Mapa de Corte' e clicar em '🚀 Otimizar Chapas' primeiro.")
