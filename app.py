import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- FUNÇÕES DE APOIO ---
def carregar_csv(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)

# --- INICIALIZAÇÃO DE ESTADO ---
if 'df_projeto' not in st.session_state: 
    st.session_state.df_projeto = None

menu = st.sidebar.radio("Navegação", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos"])

# --- ABA 1: CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    
    st.subheader("Chapas")
    df_chapas = st.data_editor(carregar_csv("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic", key="c_chapas")
    if st.button("Salvar Chapas"): 
        df_chapas.to_csv("materiais.csv", index=False)
        st.success("Chapas salvas!")
    
    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(carregar_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic", key="c_fitas")
    if st.button("Salvar Fitas"): 
        df_fitas.to_csv("fitas.csv", index=False)
        st.success("Fitas salvas!")

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
        
        temp_df = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn(options=lista_mat),
            "Fita_Usada": st.column_config.SelectboxColumn(options=lista_fitas)
        }, use_container_width=True)
        
        if st.button("✅ Confirmar e Salvar Dados"):
            st.session_state.df_projeto = temp_df
            st.success("Dados salvos!")

# --- ABA 3: ORÇAMENTOS (CORREÇÃO FINAL DE CÁLCULO) ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        chapas = carregar_csv("materiais.csv", ['Material', 'Preço_Unit'])
        fitas = carregar_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        def calcular(row):
            try:
                # Limpeza rigorosa para extrair apenas o número
                def limpar_num(val):
                    s = str(val).lower().replace(' mm', '').replace(',', '.').strip()
                    # Remove qualquer caractere que não seja número ou ponto
                    s = ''.join([c for c in s if c.isdigit() or c == '.'])
                    return float(s) if s else 0.0

                l = limpar_num(row.get('Largura', 0))
                c = limpar_num(row.get('Comprimento', 0))
                area = (l * c) / 1000000
                
                # Busca Preço Chapa
                mat = str(row.get('Material', '')).strip()
                p_mat = chapas[chapas['Material'].astype(str).str.strip() == mat]['Preço_Unit']
                custo = area * (float(p_mat.values[0]) if not p_mat.empty else 0)
                
                # Busca Preço Fita
                fita = str(row.get('Fita_Usada', '')).strip()
                if fita and fita != "None":
                    p_fita_row = fitas[fitas['Nome Fita'].astype(str).str.strip() == fita]['Custo Total Aplicado (m)']
                    if not p_fita_row.empty:
                        p_fita = float(p_fita_row.values[0])
                        if row.get('C1'): custo += (l/1000) * p_fita
                        if row.get('C2'): custo += (l/1000) * p_fita
                        if row.get('L1'): custo += (c/1000) * p_fita
                        if row.get('L2'): custo += (c/1000) * p_fita
                
                return float(round(custo, 2))
            except: 
                return 0.0 # Retorna 0 em caso de falha silenciosa para não quebrar o sum()
            
        # Aplica o cálculo
        df['Custo Total'] = df.apply(calcular, axis=1)
        
        # Exibição
        st.dataframe(df[['Código', 'Descrição', 'Material', 'Fita_Usada', 'Custo Total']])
        
        # Garante que o total seja numérico
        total_projeto = df['Custo Total'].astype(float).sum()
        st.metric("Total do Projeto", f"R$ {total_projeto:,.2f}")
    else:
        st.warning("⚠️ Carregue os dados no Mapa de Corte.")
