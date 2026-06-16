import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- FUNÇÕES ---
def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

if 'df_projeto' not in st.session_state: st.session_state.df_projeto = None

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- MAPA DE CORTE (FOCO EM ESTABILIDADE) ---
if menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    
    # Upload apenas se não houver dados
    if st.session_state.df_projeto is None:
        uploaded_file = st.file_uploader("Carregue o CSV", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file, sep=';')
            df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
            st.session_state.df_projeto = df
            st.rerun()

    if st.session_state.df_projeto is not None:
        lista_mat = load_csv_data("materiais.csv", ['Material'])['Material'].unique().tolist()
        lista_fitas = load_csv_data("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        
        # O editor é TEMPORÁRIO, ele não sobrescreve o estado até você clicar no botão
        edited_df = st.data_editor(
            st.session_state.df_projeto,
            key="temp_editor",
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_mat),
                "Fita_Usada": st.column_config.SelectboxColumn("Fita", options=lista_fitas)
            },
            num_rows="dynamic",
            use_container_width=True
        )
        
        # SÓ SALVA QUANDO VOCÊ QUISER
        if st.button("✅ Confirmar e Salvar Edições"):
            st.session_state.df_projeto = edited_df
            st.success("Dados salvos com sucesso!")
            st.rerun()

# --- ORÇAMENTOS (CÁLCULO ESTRUTURADO) ---
elif menu == "Orçamentos":
    st.header("💰 Orçamentos")
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        # Cálculo simples e seguro
        st.dataframe(df)
        st.info("Nota: O cálculo é feito com base na última versão salva no 'Mapa de Corte'.")
    else:
        st.warning("Carregue dados no Mapa de Corte.")
