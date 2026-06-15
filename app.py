import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])
if 'df' not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# Função que garante que a lista de materiais seja sempre a mais atual
def get_lista_materiais():
    if not st.session_state.estoque.empty:
        return st.session_state.estoque['Material'].dropna().unique().tolist()
    return []

if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    # Capturamos o retorno do data_editor para atualizar o session_state
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Salvar Cadastro"): 
        st.success("Cadastro atualizado! Lista de materiais sincronizada.")

elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Renomeação e Limpeza
        df = df.rename(columns={"Part #": "Código", "Sub-Assembly": "Sub-Montagem", "Description": "Descrição", "Copies": "Quantidade", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Can Rotate": "Rotação"})
        df = df.drop(columns=[c for c in ["Material Type", "Material Name", "Unnamed: 10"] if c in df.columns])
        
        # Numeração
        if 'Código' in df.columns:
            max_code = df['Código'].max() if not pd.isna(df['Código'].max()) else 0
            for idx in df.index:
                if pd.isna(df.loc[idx, 'Código']) or str(df.loc[idx, 'Código']).strip() == "":
                    max_code += 1
                    df.loc[idx, 'Código'] = max_code

        # O SEGREDO: Chamamos a função de lista aqui, no momento da renderização
        lista_atual = get_lista_materiais()
        
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Código": st.column_config.NumberColumn("Código", disabled=True),
                "Material": st.column_config.SelectboxColumn("Material", options=lista_atual, required=True),
                "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
            },
            num_rows="dynamic",
            use_container_width=True
        )

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("Materiais disponíveis para cálculo: " + ", ".join(get_lista_materiais()))
