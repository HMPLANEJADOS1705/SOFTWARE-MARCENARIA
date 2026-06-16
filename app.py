import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def carregar_csv(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)

# Inicialização do Estado
if 'df_projeto' not in st.session_state: st.session_state.df_projeto = None

menu = st.sidebar.radio("Navegação", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos"])

# --- ABA 1: CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    
    st.subheader("Chapas")
    df_chapas = st.data_editor(carregar_csv("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic", key="c_chapas")
    if st.button("Salvar Chapas"): df_chapas.to_csv("materiais.csv", index=False)
    
    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(carregar_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic", key="c_fitas")
    if st.button("Salvar Fitas"): df_fitas.to_csv("fitas.csv", index=False)

# --- ABA 2: MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    
    if st.session_state.df_projeto is None:
        arquivo = st.file_uploader("Carregue o CSV do SketchUp", type="csv")
        if arquivo:
            df = pd.read_csv(arquivo, sep=';')
            df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
            st.session_state.df_projeto = df
            st.rerun()
    
    if st.session_state.df_projeto is not None:
        lista_mat = carregar_csv("materiais.csv", ['Material'])['Material'].unique().tolist()
        lista_fitas = carregar_csv("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        if 'Fita_Usada' not in st.session_state.df_projeto.columns: st.session_state.df_projeto['Fita_Usada'] = ""
        
        # Editor isolado
        temp_df = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn(options=lista_mat),
            "Fita_Usada": st.column_config.SelectboxColumn(options=lista_fitas)
        }, use_container_width=True)
        
        if st.button("✅ Confirmar e Salvar Dados"):
            st.session_state.df_projeto = temp_df
            st.success("Dados salvos!")

# --- ABA 3: ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        chapas = carregar_csv("materiais.csv", ['Material', 'Preço_Unit'])
        fitas = carregar_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        def calcular(row):
            try:
                l = float(str(row.get('Largura', 0)).replace(' mm', '').replace(',', '.'))
                c = float(str(row.get('Comprimento', 0)).replace(' mm', '').replace(',', '.'))
                area = (l * c) / 1000000
                p_mat = chapas[chapas['Material'] == row.get('Material')]['Preço_Unit'].values
                custo = area * (p_mat[0] if len(p_mat) > 0 else 0)
                
                fita = row.get('Fita_Usada')
                p_fita = fitas[fitas['Nome Fita'] == fita]['Custo Total Aplicado (m)'].values
                p_fita = p_fita[0] if len(p_fita) > 0 else 0
                
                if row.get('C1') or row.get('C2'): custo += (l/1000) * p_fita
                if row.get('L1') or row.get('L2'): custo += (c/1000) * p_fita
                return custo
            except: return 0
            
        df['Custo Total'] = df.apply(calcular, axis=1)
        st.dataframe(df[['Código', 'Descrição', 'Material', 'Fita_Usada', 'Custo Total']])
        st.metric("Total do Projeto", f"R$ {df['Custo Total'].sum():,.2f}")
    else:
        st.warning("⚠️ Carregue um arquivo no Mapa de Corte.")
