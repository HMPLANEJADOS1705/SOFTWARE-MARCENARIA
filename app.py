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

# --- ABA 2: MAPA DE CORTE (SUBSTITUA ESTE BLOCO) ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    
    if st.button("🔄 Reiniciar/Limpar"):
        st.session_state.df_projeto = None
        st.rerun()

    if st.session_state.df_projeto is None:
        arquivo = st.file_uploader("Carregue o CSV do SketchUp", type="csv")
        if arquivo:
            df = pd.read_csv(arquivo, sep=';')
            df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
            
            # FORÇAR CRIAÇÃO DAS COLUNAS FALTANTES
            df['Fita_Usada'] = ""
            df['C1'] = False
            df['C2'] = False
            df['L1'] = False
            df['L2'] = False
            
            st.session_state.df_projeto = df
            st.rerun()
    
    if st.session_state.df_projeto is not None:
        lista_mat = carregar_csv("materiais.csv", ['Material'])['Material'].unique().tolist()
        lista_fitas = carregar_csv("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        
        # Garante que existam mesmo se o usuário carregou o arquivo antes
        for col in ['Fita_Usada', 'C1', 'C2', 'L1', 'L2']:
            if col not in st.session_state.df_projeto.columns:
                st.session_state.df_projeto[col] = False if 'C' in col or 'L' in col else ""
        
        temp_df = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn(options=lista_mat),
            "Fita_Usada": st.column_config.SelectboxColumn(options=lista_fitas),
            "C1": st.column_config.CheckboxColumn("C1"),
            "C2": st.column_config.CheckboxColumn("C2"),
            "L1": st.column_config.CheckboxColumn("L1"),
            "L2": st.column_config.CheckboxColumn("L2")
        }, use_container_width=True)
        
        if st.button("✅ Confirmar e Salvar"):
            st.session_state.df_projeto = temp_df
            st.success("Dados salvos!")
# --- ABA 3: ORÇAMENTOS (BLOCO DE DIAGNÓSTICO) ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    # Verifica se existe algo na memória
    if st.session_state.df_projeto is not None and not st.session_state.df_projeto.empty:
        st.write("Dados carregados com sucesso!") # Isso vai aparecer se o DF existir
        
        df = st.session_state.df_projeto.copy()
        
        # Carrega insumos
        chapas = carregar_csv("materiais.csv", ['Material', 'Preço_Unit'])
        fitas = carregar_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
       def calcular_linha(row):
            try:
                # 1. Limpeza
                def limpar(val):
                    s = ''.join([c for c in str(val) if c.isdigit() or c == '.'])
                    return float(s) if s else 0.0

                l = limpar(row.get('Largura', 0))
                c = limpar(row.get('Comprimento', 0))
                area = (l * c) / 1000000
                
                # 2. BUSCA COM LOG
                mat_linha = str(row.get('Material', '')).strip().lower()
                mat_desc = str(row.get('Descrição', '')).strip().lower()
                
                preco_mat = 0.0
                encontrou = False
                
                for index, item in chapas.iterrows():
                    mat_cad = str(item['Material']).strip().lower()
                    # Verifica se o material da linha (ou a descrição) é igual ao cadastro
                    if mat_linha == mat_cad or mat_desc == mat_cad:
                        preco_mat = float(item['Preço_Unit'])
                        encontrou = True
                        break
                
                if not encontrou:
                    return f"Não achei: {mat_linha}" # <--- ISSO VAI APARECER NA TABELA!
                
                custo = area * preco_mat
                
                # 3. Fita (mantém igual)
                fita_linha = str(row.get('Fita_Usada', '')).strip().lower()
                # ... (resto do código da fita)
                
                return float(round(custo, 2))
            except:
                return "Erro cálculo"
        df['Custo Total'] = df.apply(calcular_linha, axis=1)
        st.dataframe(df)
        st.metric("Total do Projeto", f"R$ {df['Custo Total'].astype(float).sum():,.2f}")
        
    else:
        st.warning("⚠️ A memória do projeto está vazia.")
        st.write("Verifique se você clicou em 'Confirmar e Salvar' na aba Mapa de Corte.")
