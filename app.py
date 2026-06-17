import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def load_csv(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

if 'df_projeto' not in st.session_state:
    st.session_state.df_projeto = None

# Sidebar Configs
st.sidebar.header("Configurações do Orçamento")
taxa_lucro = st.sidebar.number_input("Taxa de Lucro (%)", min_value=0.0, value=30.0) / 100
forma_cobranca = st.sidebar.radio("Forma de Cobrança", ["Área Utilizada", "Chapa Inteira"])

menu = st.sidebar.radio("Navegação", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos"])

if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Chapas (Material, Preço, Largura da Chapa, Comprimento da Chapa)")
    df_boards = st.data_editor(load_csv("materiais.csv", ['Material', 'Preço_Unit', 'Largura_Chapa', 'Comprimento_Chapa']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_boards.to_csv("materiais.csv", index=False)
        st.success("Salvo!")
    
    st.subheader("Fitas")
    df_tapes = st.data_editor(load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"):
        df_tapes.to_csv("fitas.csv", index=False)
        st.success("Salvo!")

elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    if st.button("🔄 Reiniciar Projeto"):
        st.session_state.df_projeto = None
        st.rerun()

    if st.session_state.df_projeto is None:
        file = st.file_uploader("Upload CSV", type="csv")
        if file:
            df = pd.read_csv(file, sep=';')
            df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
            df['Fita_Usada'] = ""; df['C1'] = False; df['C2'] = False; df['L1'] = False; df['L2'] = False
            st.session_state.df_projeto = df
            st.rerun()
    
    if st.session_state.df_projeto is not None:
        mats = load_csv("materiais.csv", ['Material'])['Material'].unique().tolist()
        tapes = load_csv("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        
        # Edição dinâmica habilitada
        st.session_state.df_projeto = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=mats),
            "Fita_Usada": st.column_config.SelectboxColumn("Fita_Usada", options=tapes)
        }, use_container_width=True)

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        boards = load_csv("materiais.csv", ['Material', 'Preço_Unit', 'Largura_Chapa', 'Comprimento_Chapa'])
        tapes = load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        # --- FUNÇÃO DE CÁLCULO ---
        def calculate_row(row):
            try:
                def clean(v): return float(''.join([c for c in str(v) if c.isdigit() or c == '.']))
                l, w = clean(row.get('Largura', 0)), clean(row.get('Comprimento', 0))
                area_m2 = (l * w) / 1000000
                
                mat = str(row.get('Material', '')).strip().lower()
                board_match = boards[boards['Material'].astype(str).str.strip().str.lower() == mat]
                
                # Custo da peça (m2)
                preco_m2 = float(board_match['Preço_Unit'].values[0]) if not board_match.empty else 0.0
                cost_mat = area_m2 * preco_m2
                
                # Fitas (por metro linear)
                tape = str(row.get('Fita_Usada', '')).strip().lower()
                tape_match = tapes[tapes['Nome Fita'].astype(str).str.strip().str.lower() == tape]
                cost_tape = 0.0
                if not tape_match.empty:
                    p_tape = float(tape_match['Custo Total Aplicado (m)'].values[0])
                    if row.get('C1'): cost_tape += (l/1000) * p_tape
                    if row.get('C2'): cost_tape += (l/1000) * p_tape
                    if row.get('L1'): cost_tape += (w/1000) * p_tape
                    if row.get('L2'): cost_tape += (w/1000) * p_tape
                    
                return pd.Series([cost_mat, cost_tape, area_m2])
            except: return pd.Series([0.0, 0.0, 0.0])

        df[['Custo_MDF', 'Custo_Fita', 'Area_M2']] = df.apply(calculate_row, axis=1)
        
        # --- RELATÓRIO RESUMIDO (O QUE VOCÊ PEDIU) ---
        st.subheader("📋 Relatório de Insumos")
        col1, col2 = st.columns(2)
        
        total_m2 = df['Area_M2'].sum()
        total_mdf = df['Custo_MDF'].sum()
        total_fita = df['Custo_Fita'].sum()
        
        col1.metric("Área Total (m²)", f"{total_m2:.2f} m²")
        col2.metric("Total MDF", f"R$ {total_mdf:,.2f}")
        st.metric("Total Fitas", f"R$ {total_fita:,.2f}")
        
        # --- CÁLCULO FINAL ---
        custo_materiais_fita = total_mdf + total_fita
        valor_final = custo_materiais_fita * (1 + taxa_lucro)
        
        st.markdown("---")
        st.metric("Total do Projeto com Lucro", f"R$ {valor_final:,.2f}")
        
        # Exibe a tabela detalhada
        st.subheader("Detalhe por Peça")
        st.dataframe(df)
      
