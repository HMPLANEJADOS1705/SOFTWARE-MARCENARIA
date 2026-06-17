import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÕES GERAIS ---
st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def load_csv(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

if 'df_projeto' not in st.session_state:
    st.session_state.df_projeto = None

# --- SIDEBAR (CONFIGURAÇÕES GERAIS) ---
st.sidebar.header("Configurações do Orçamento")
taxa_lucro = st.sidebar.number_input("Taxa de Lucro (%)", min_value=0.0, value=30.0) / 100

# Seletor de cobrança: Preservado e funcional
forma_cobranca = st.sidebar.radio("Forma de Cobrança", ["Área Utilizada", "Chapa Inteira"])

# Menu de navegação com a nova opção visual
menu = st.sidebar.radio("Navegação", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos", "Otimização de Chapa (Visual)"])

# --- ABA 1: CADASTRO DE INSUMOS ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Chapas (Material, Preço, Largura da Chapa, Comprimento da Chapa)")
    df_boards = st.data_editor(load_csv("materiais.csv", ['Material', 'Preço_Unit', 'Largura_Chapa', 'Comprimento_Chapa']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_boards.to_csv("materiais.csv", index=False)
        st.success("Salvo!")
    
    st.subheader("Fitas")
    df_tapes = st.data_editor(load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"):
        df_tapes.to_csv("fitas.csv", index=False)
        st.success("Salvo!")

# --- ABA 2: MAPA DE CORTE ---
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
        
        # Uso do st.data_editor preserva o estado sem apagar ao interagir
        st.session_state.df_projeto = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=mats),
            "Fita_Usada": st.column_config.SelectboxColumn("Fita_Usada", options=tapes)
        }, use_container_width=True)

# --- ABA 3: ORÇAMENTOS (AJUSTADA E COMPLETA) ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        
        boards = load_csv("materiais.csv", ['Material', 'Preço_Unit', 'Largura_Chapa', 'Comprimento_Chapa'])
        tapes = load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        # --- FUNÇÃO DE CÁLCULO ---
        def calculate_row(row):
            try:
                def clean(v): return float(''.join([c for c in str(v) if c.isdigit() or c == '.']))
                l, w = clean(row.get('Largura', 0)), clean(row.get('Comprimento', 0))
                area_m2 = (l * w) / 1000000
                
                mat = str(row.get('Material', '')).strip().lower()
                board_match = boards[boards['Material'].astype(str).str.strip().str.lower() == mat]
                preco_m2 = float(board_match['Preço_Unit'].values[0]) if not board_match.empty else 0.0
                cost_mat = area_m2 * preco_m2
                
                tape = str(row.get('Fita_Usada', '')).strip().lower()
                t_match = tapes[tapes['Nome Fita'].astype(str).str.strip().str.lower() == tape]
                cost_tape, m_fita = 0.0, 0.0
                if not t_match.empty:
                    p_tape = float(t_match['Custo Total Aplicado (m)'].values[0])
                    # Soma se a borda estiver marcada
                    if row.get('C1'): m_fita += (l/1000); cost_tape += (l/1000) * p_tape
                    if row.get('C2'): m_fita += (l/1000); cost_tape += (l/1000) * p_tape
                    if row.get('L1'): m_fita += (w/1000); cost_tape += (w/1000) * p_tape
                    if row.get('L2'): m_fita += (w/1000); cost_tape += (w/1000) * p_tape
                return pd.Series([cost_mat, cost_tape, area_m2, m_fita])
            except: return pd.Series([0.0, 0.0, 0.0, 0.0])

        df[['Custo_MDF', 'Custo_Fita', 'Area_M2', 'Metros_Fita']] = df.apply(calculate_row, axis=1)
        
        # --- CÁLCULO TOTAL ---
        total_m2 = df['Area_M2'].sum()
        total_mdf = df['Custo_MDF'].sum()
        total_fita = df['Custo_Fita'].sum()
        total_metros_fita = df['Metros_Fita'].sum()
        
        if forma_cobranca == "Chapa Inteira":
            # Agora calculamos o custo real de chapas inteiras para TODOS os materiais usados
            materiais_unicos = df[df['Area_M2'] > 0]['Material'].unique()
            custo_base_mdf = 0
            for mat in materiais_unicos:
                b_match = boards[boards['Material'].astype(str).str.strip().str.lower() == mat.lower()]
                if not b_match.empty: custo_base_mdf += float(b_match['Preço_Unit'].values[0])
            custo_materiais = custo_base_mdf + total_fita
        else:
            custo_materiais = total_mdf + total_fita
        
        valor_final = custo_materiais * (1 + taxa_lucro)
        
        # --- MÉTricas E GRÁFICOS (VISUAL) ---
        st.header("📊 Métricas e Gráficos do Orçamento")
        col1, col2, col3 = st.columns(3)
        col1.metric("Área Total Utilizada", f"{total_m2:.2f} m²", f"Valor do MDF: R$ {total_mdf:,.2f}", delta_color="off")
        col2.metric("Total Fita de Borda", f"{total_metros_fita:.2f} m", f"Valor Total Fita: R$ {total_fita:,.2f}", delta_color="off")
        col3.metric("Total Projeto com Lucro", f"R$ {valor_final:,.2f}", f"(Materiais + Fita) + {taxa_lucro*100}%", delta_color="off")

        st.header("📊 Resumo e Custos Detalhados")
        
        # 1. Criação do Módulo de Resumo MDF (AGORA DINÂMICO!)
        st.subheader("Resumo MDF")
        if not df[df['Area_M2'] > 0].empty:
            # AGRUPAMENTO POR MATERIAL: A mágica acontece aqui!
            # O sistema soma a área e custo de todas as peças de cada material
            df_mdf_agrupado = df.groupby('Material')[['Area_M2', 'Custo_MDF']].sum().reset_index()
            
            # Formatação para exibição
            df_mdf_agrupado.columns = ['Material', 'Área Total (m²)', 'Custo (R$)']
            df_mdf_agrupado['Área Total (m²)'] = df_mdf_agrupado['Área Total (m²)'].map('{:.2f} m²'.format)
            df_mdf_agrupado['Custo (R$)'] = df_mdf_agrupado['Custo (R$)'].map('R$ {:,.2f}'.format)
            
            # Exibe a tabela com as duas linhas (6mm e 15mm)
            st.table(df_mdf_agrupado)
        else:
            st.write("Nenhuma chapa utilizada no Mapa de Corte.")

        # 2. Criação do Módulo de Resumo Fita (MANTIDO DINÂMICO)
        st.subheader("Resumo Fita de Borda")
        if not df[df['Metros_Fita'] > 0].empty:
            df_tape_agrupado = df.groupby('Fita_Usada')[['Metros_Fita', 'Custo_Fita']].sum().reset_index()
            df_tape_agrupado.columns = ['Nome Fita', 'Metros Usados (m)', 'Custo (R$)']
            df_tape_agrupado['Metros Usados (m)'] = df_tape_agrupado['Metros Usados (m)'].map('{:.2f} m'.format)
            df_tape_agrupado['Custo (R$)'] = df_tape_agrupado['Custo (R$)'].map('R$ {:,.2f}'.format)
            st.table(df_tape_agrupado)
        else:
            st.write("Nenhuma fita utilizada no Mapa de Corte.")
# --- ABA 4: OTIMIZAÇÃO DE CHAPA (NOVO PASSO) ---
elif menu == "Otimização de Chapa (Visual)":
    st.header("📐 Otimização de Chapa (Visual)")
    if st.session_state.df_projeto is not None:
        st.info("Aqui iremos gerar a visualização das peças encaixadas na chapa.")
        # O próximo passo será criar a função de otimização
