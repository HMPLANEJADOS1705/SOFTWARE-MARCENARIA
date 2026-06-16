import streamlit as st
import pandas as pd
import os
from difflib import get_close_matches
st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def carregar_csv(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)

if 'df_projeto' not in st.session_state:
    st.session_state.df_projeto = None

menu = st.sidebar.radio("Navegação", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos"])

if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Chapas")
    df_chapas = st.data_editor(carregar_csv("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic", key="c_chapas")
    if st.button("Salvar Chapas"):
        df_chapas.to_csv("materiais.csv", index=False)
        st.success("Salvo!")
    st.subheader("Fitas")
    df_fitas = st.data_editor(carregar_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic", key="c_fitas")
    if st.button("Salvar Fitas"):
        df_fitas.to_csv("fitas.csv", index=False)
        st.success("Salvo!")

elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    if st.session_state.df_projeto is None:
        arquivo = st.file_uploader("Carregue o CSV", type="csv")
        if arquivo:
            df = pd.read_csv(arquivo, sep=';')
            df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
            st.session_state.df_projeto = df
            st.rerun()
    
    if st.session_state.df_projeto is not None:
        lista_mat = carregar_csv("materiais.csv", ['Material'])['Material'].unique().tolist()
        lista_fitas = carregar_csv("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        if 'Fita_Usada' not in st.session_state.df_projeto.columns: st.session_state.df_projeto['Fita_Usada'] = ""
        
        temp_df = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn(options=lista_mat),
            "Fita_Usada": st.column_config.SelectboxColumn(options=lista_fitas)
        }, use_container_width=True)
        
        if st.button("✅ Confirmar e Salvar"):
            st.session_state.df_projeto = temp_df
            st.rerun()

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        chapas = carregar_csv("materiais.csv", ['Material', 'Preço_Unit'])
        fitas = carregar_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
   # Adicione esta importação no topo do arquivo se não existir:
        # from difflib import get_close_matches

        def calcular_linha(row):
            try:
                # Limpeza simples
                def limpar(val):
                    s = ''.join([c for c in str(val) if c.isdigit() or c == '.'])
                    return float(s) if s else 0.0

                l = limpar(row.get('Largura', 0))
                c = limpar(row.get('Comprimento', 0))
                area = (l * c) / 1000000
                
                # BUSCA INTELIGENTE (Aproximação)
                mat_mapa = str(row.get('Material', '')).strip()
                lista_materiais = chapas['Material'].astype(str).tolist()
                
                # Tenta encontrar o material mais parecido na lista
                match = get_close_matches(mat_mapa, lista_materiais, n=1, cutoff=0.6)
                
                custo = 0.0
                if match:
                    preco = chapas[chapas['Material'] == match[0]]['Preço_Unit'].values[0]
                    custo = area * float(preco)
                
                # Mesma lógica para Fita
                fita = str(row.get('Fita_Usada', '')).strip()
                lista_fitas = fitas['Nome Fita'].astype(str).tolist()
                fita_match = get_close_matches(fita, lista_fitas, n=1, cutoff=0.6)
                
                if fita_match:
                    p_fita = float(fitas[fitas['Nome Fita'] == fita_match[0]]['Custo Total Aplicado (m)'].values[0])
                    if row.get('C1') or row.get('C2'): custo += (l/1000) * p_fita
                    if row.get('L1') or row.get('L2'): custo += (c/1000) * p_fita
                
                return float(round(custo, 2))
            except Exception:
                return 0.0
