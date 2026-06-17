import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def load_csv(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

# Sidebar Configs
st.sidebar.header("Configurações do Orçamento")
taxa_lucro = st.sidebar.number_input("Taxa de Lucro (%)", min_value=0.0, value=30.0) / 100
forma_cobranca = st.sidebar.radio("Forma de Cobrança", ["Área Utilizada", "Chapa Inteira"])

menu = st.sidebar.radio("Navegação", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos"])

if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    df_boards = st.data_editor(load_csv("materiais.csv", ['Material', 'Preço_Unit', 'Largura_Chapa', 'Comprimento_Chapa']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_boards.to_csv("materiais.csv", index=False)
        st.success("Salvo!")
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
        
        def calculate_row(row):
            try:
                def clean(v): return float(''.join([c for c in str(v) if c.isdigit() or c == '.']))
                l, w = clean(row.get('Largura', 0)), clean(row.get('Comprimento', 0))
                area_m2 = (l * w) / 1000000
                
                mat = str(row.get('Material', '')).strip().lower()
                board_match = boards[boards['Material'].astype(str).str.strip().str.lower() == mat]
                
                # CÁLCULO CORRIGIDO:
                # 1. Tenta pegar o preço por M2 se existir no cadastro.
                # 2. Se não, usa o Preço_Unit como base (sua lógica antiga que funcionava).
                if not board_match.empty:
                    preco_unit = float(board_match['Preço_Unit'].values[0])
                    # Verifica se temos dimensões de chapa válidas para calcular m2 real
                    l_chapa = float(board_match.get('Largura_Chapa', 2750).values[0] or 2750)
                    c_chapa = float(board_match.get('Comprimento_Chapa', 1840).values[0] or 1840)
                    area_chapa_m2 = (l_chapa * c_chapa) / 1000000
                    
                    # Custo = área da peça * (preço da chapa / área da chapa)
                    cost_mat = area_m2 * (preco_unit / area_chapa_m2)
                else:
                    cost_mat = 0.0
                
                # Fitas (por metro linear) - MANTENDO LÓGICA FUNCIONAL
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
            except Exception as e:
                return pd.Series([0.0, 0.0, 0.0])

        df[['Custo_MDF', 'Custo_Fita', 'Area_M2']] = df.apply(calculate_row, axis=1)
        
        # --- RELATÓRIO ---
        st.subheader("📋 Relatório de Insumos")
        total_m2 = df['Area_M2'].sum()
        total_mdf = df['Custo_MDF'].sum()
        total_fita = df['Custo_Fita'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Área Total (m²)", f"{total_m2:.2f} m²")
        c2.metric("Total MDF", f"R$ {total_mdf:,.2f}")
        st.metric("Total Fitas", f"R$ {total_fita:,.2f}")
        
        valor_final = (total_mdf + total_fita) * (1 + taxa_lucro)
        st.markdown("---")
        st.metric("Total do Projeto com Lucro", f"R$ {valor_final:,.2f}")
        st.dataframe(df)
