import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÕES E FUNÇÕES GLOBAIS (Devem vir primeiro) ---
st.set_page_config(layout="wide", page_title="Marcenaria Pro")

FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

def load_csv(file, cols):
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# --- 2. NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- 3. ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_csv(FILE_CHAPAS, ['Material', 'Tipo', 'Preço_Unit', 'Custo_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_chapas.to_csv(FILE_CHAPAS, index=False)
        st.success("Chapas salvas!")

    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(load_csv(FILE_FITAS, ['Nome Fita', 'Valor Rolo', 'Metros Rolo', 'Custo Cola/Tempo(m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"):
        # Cálculo de segurança
        df_fitas['Valor Rolo'] = pd.to_numeric(df_fitas['Valor Rolo'], errors='coerce').fillna(0)
        df_fitas['Metros Rolo'] = pd.to_numeric(df_fitas['Metros Rolo'], errors='coerce').fillna(0)
        df_fitas['Custo Cola/Tempo(m)'] = pd.to_numeric(df_fitas['Custo Cola/Tempo(m)'], errors='coerce').fillna(0)
        df_fitas.to_csv(FILE_FITAS, index=False)
        st.success("Fitas salvas!")

# --- 4. ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Limpeza
        df = df.drop(columns=[c for c in ["Material Type", "Material Name", "Unnamed: 10"] if c in df.columns], errors='ignore')
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Can Rotate": "Rotação"})
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
            
        # Carrega lista do CSV de chapas
        df_chapas = load_csv(FILE_CHAPAS, ['Material'])
        lista_materiais = df_chapas['Material'].dropna().unique().tolist() if not df_chapas.empty else []
        
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
                "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
            },
            num_rows="dynamic", use_container_width=True
        )

# --- 5. ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("Funcionalidade em desenvolvimento.")
