import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- FUNÇÕES DE APOIO ---
def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

# --- INICIALIZAÇÃO DE ESTADO ---
if 'df_projeto' not in st.session_state: st.session_state.df_projeto = None
if 'otimizado' not in st.session_state: st.session_state.otimizado = False

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    df_chapas = st.data_editor(load_csv_data("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"): df_chapas.to_csv("materiais.csv", index=False)
    
    df_fitas = st.data_editor(load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"): df_fitas.to_csv("fitas.csv", index=False)

# --- ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
        st.session_state.df_projeto = df

    if st.session_state.df_projeto is not None:
        lista_mat = load_csv_data("materiais.csv", ['Material'])['Material'].unique().tolist()
        lista_fitas = load_csv_data("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        
        if 'Fita_Usada' not in st.session_state.df_projeto.columns: st.session_state.df_projeto['Fita_Usada'] = ""
        
        # Edição persistente
        st.session_state.df_projeto = st.data_editor(
            st.session_state.df_projeto, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_mat),
                "Fita_Usada": st.column_config.SelectboxColumn("Fita", options=lista_fitas)
            },
            num_rows="dynamic", use_container_width=True
        )
        
        if st.button("🚀 Otimizar Chapas"):
            st.session_state.otimizado = True
            st.success("Otimização gravada! Vá para a aba de Orçamentos.")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if st.session_state.otimizado and st.session_state.df_projeto is not None:
        df_calc = st.session_state.df_projeto.copy()
        df_chapas = load_csv_data("materiais.csv", ['Material', 'Preço_Unit'])
        df_fitas = load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        def calcular(row):
            try:
                larg = float(str(row.get('Largura', 0)).replace(' mm', '').replace(',', '.'))
                comp = float(str(row.get('Comprimento', 0)).replace(' mm', '').replace(',', '.'))
                area = (larg * comp) / 1000000
                
                preco_mat = df_chapas[df_chapas['Material'] == row.get('Material')]['Preço_Unit'].values
                custo = area * (preco_mat[0] if len(preco_mat) > 0 else 0)
                
                preco_f = df_fitas[df_fitas['Nome Fita'] == row.get('Fita_Usada')]['Custo Total Aplicado (m)'].values
                preco_f = preco_f[0] if len(preco_f) > 0 else 0
                
                if row.get('C1') or row.get('C2'): custo += (larg/1000) * preco_f
                if row.get('L1') or row.get('L2'): custo += (comp/1000) * preco_f
                return custo
            except: return 0.0

        df_calc['Custo'] = df_calc.apply(calcular, axis=1)
        st.dataframe(df_calc[['Código', 'Descrição', 'Material', 'Fita_Usada', 'Custo']])
        st.metric("Total", f"R$ {df_calc['Custo'].sum():,.2f}")
    else:
        st.warning("⚠️ Você precisa clicar em '🚀 Otimizar Chapas' na aba anterior.")
