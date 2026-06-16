import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- PERSISTÊNCIA EM ARQUIVO ---
ARQUIVO_ESTOQUE = "materiais.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        return pd.read_csv(ARQUIVO_ESTOQUE)
    return pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])

def salvar_dados(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA DE CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    estoque_atual = carregar_dados()
    
    # Editor
    novo_df = st.data_editor(estoque_atual, num_rows="dynamic", use_container_width=True, key="editor_fixo")
    
    if st.button("💾 Salvar Cadastro Permanentemente"):
        salvar_dados(novo_df)
        st.success("Dados salvos no arquivo materiais.csv com sucesso!")

# --- ABA DE MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    estoque_salvo = carregar_dados()
    lista_materiais = estoque_salvo['Material'].dropna().unique().tolist()
    
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Limpeza e Renomeação
        df = df.drop(columns=[c for c in ["Material Type", "Material Name", "Unnamed: 10"] if c in df.columns], errors='ignore')
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Can Rotate": "Rotação"})
        
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
            
        st.data_editor(df, column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
            "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
        }, use_container_width=True)

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    estoque_salvo = carregar_dados()
    st.write("Materiais carregados do arquivo:", estoque_salvo['Material'].tolist())
