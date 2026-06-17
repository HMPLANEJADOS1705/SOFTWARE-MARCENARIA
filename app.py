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

# Sidebar Configs - MANTENDO A FLEXIBILIDADE DE COBRANÇA AQUI
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
        # AQUI O USO DO ST.DATA_EDITOR PRESERVA O ESTADO SEM APAGAR AO INTERAGIR
        st.session_state.df_projeto = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=mats),
            "Fita_Usada": st.column_config.SelectboxColumn("Fita_Usada", options=tapes)
        }, use_container_width=True)

 
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        
        # Carrega os dados com os nomes de colunas que estão na sua foto
        boards = load_csv("materiais.csv", ['Material', 'Preço_Unit', 'Largura_Chapa', 'Comprimento_Chapa'])
        tapes = load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        def calculate_row(row):
            try:
                # Limpeza robusta de dados
                def clean(v): 
                    s = str(v).replace(',', '.')
                    return float(''.join([c for c in s if c.isdigit() or c == '.']))
                
                l, w = clean(row.get('Largura', 0)), clean(row.get('Comprimento', 0))
                qtd = clean(row.get('Copies', 1))
                area_m2 = (l * w * qtd) / 1000000
                
                # Busca material ignorando maiúsculas/minúsculas e espaços
                mat_nome = str(row.get('Material', '')).strip().lower()
                b_match = boards[boards['Material'].astype(str).str.strip().str.lower() == mat_nome]
                
                cost_mat = 0.0
                if not b_match.empty and forma_cobranca == "Área Utilizada":
                    p_chapa = float(b_match['Preço_Unit'].values[0])
                    # Calcula área da chapa em m2 (usando Largura_Chapa e Comprimento_Chapa do seu CSV)
                    l_c = float(b_match['Largura_Chapa'].values[0]) / 1000
                    c_c = float(b_match['Comprimento_Chapa'].values[0]) / 1000
                    area_chapa = l_c * c_c
                    cost_mat = area_m2 * (p_chapa / area_chapa)

                # Cálculo de Fita (Mantido como estava)
                tape_nome = str(row.get('Fita_Usada', '')).strip().lower()
                t_match = tapes[tapes['Nome Fita'].astype(str).str.strip().str.lower() == tape_nome]
                cost_tape, m_fita = 0.0, 0.0
                if not t_match.empty:
                    p_tape = float(t_match['Custo Total Aplicado (m)'].values[0])
                    if row.get('C1'): m_fita += (l/1000)*qtd; cost_tape += (l/1000)*qtd * p_tape
                    if row.get('C2'): m_fita += (l/1000)*qtd; cost_tape += (l/1000)*qtd * p_tape
                    if row.get('L1'): m_fita += (w/1000)*qtd; cost_tape += (w/1000)*qtd * p_tape
                    if row.get('L2'): m_fita += (w/1000)*qtd; cost_tape += (w/1000)*qtd * p_tape
                
                return pd.Series([cost_mat, cost_tape, area_m2, m_fita])
            except Exception: return pd.Series([0.0, 0.0, 0.0, 0.0])

        df[['Custo_MDF', 'Custo_Fita', 'Area_M2', 'Metros_Fita']] = df.apply(calculate_row, axis=1)
        
        # --- CÁLCULO FINAL ---
        total_fita = df['Custo_Fita'].sum()
        if forma_cobranca == "Chapa Inteira":
            # Soma valor de chapas únicas necessárias
            mats_usados = df['Material'].unique()
            custo_mdf_total = 0
            for mat in mats_usados:
                b_match = boards[boards['Material'].astype(str).str.strip().str.lower() == str(mat).lower()]
                if not b_match.empty: custo_mdf_total += float(b_match['Preço_Unit'].values[0])
        else:
            custo_mdf_total = df['Custo_MDF'].sum()
            
        valor_final = (custo_mdf_total + total_fita) * (1 + taxa_lucro)
        
        # Exibição
        st.metric("Total do Projeto com Lucro", f"R$ {valor_final:,.2f}")
        st.dataframe(df)
