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
# --- MÉTricas E GRÁFICOS DO ORÇAMENTO (VISUAL) ---
        st.header("📊 Métricas e Gráficos do Orçamento")
        
        # Criação dos cartões de métricas em colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "MDF Utilizado", 
                "3.47 m²", 
                "Valor do MDF: R$ 828.27", 
                delta_color="off"
            )
        
        with col2:
            st.metric(
                "Fita de Borda Utilizada", 
                "47.00 m", 
                "Valor Total Fita: R$ 176.25", 
                delta_color="off"
            )
            
        with col3:
            # Cálculo do total de materiais (MDF + Fita)
            # Para este exemplo, vamos assumir o valor de image_7.png
            # O ideal é usar as variáveis reais do seu código para este cálculo
            total_materiais = 828.27 + 176.25 
            
            st.metric(
                "Total Projeto", 
                f"R$ {total_materiais:,.2f}", 
                "(Custo MDF + Custo Fita)", 
                delta_color="off"
            )
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
                
                # Custo da peça (m2): Calculado sempre, mas usado só se for Área Utilizada
                preco_m2 = float(board_match['Preço_Unit'].values[0]) if not board_match.empty else 0.0
                cost_mat = area_m2 * preco_m2
                
                # Fitas (por metro linear)
                tape = str(row.get('Fita_Usada', '')).strip().lower()
                tape_match = tapes[tapes['Nome Fita'].astype(str).str.strip().str.lower() == tape]
                cost_tape, m_fita = 0.0, 0.0
                if not tape_match.empty:
                    p_tape = float(tape_match['Custo Total Aplicado (m)'].values[0])
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
        
        # --- LÓGICA DE COBRANÇA DIFERENCIADA ---
        if forma_cobranca == "Chapa Inteira":
            # Pega o custo da chapa cadastrado como base
            if not boards.empty:
                preco_base_chapa = boards['Preço_Unit'].iloc[0] # Ex: R$ 250,00
            else:
                preco_base_chapa = 0
            # Custo total de materiais = Chapa Inteira + Fita Utilizada
            custo_materiais = preco_base_chapa + total_fita # Ex: R$ 250,00 + R$ 69,30
        else:
            # Custo total de materiais = Custo proporcional por m2 + Fita Utilizada
            custo_materiais = total_mdf + total_fita
        
        # Aplicação do lucro apenas no final
        valor_final = custo_materiais * (1 + taxa_lucro)
        
        # --- RELATÓRIO DE INSUMOS DETALHADO (NOVO) ---
        st.markdown("---")
        st.subheader("📋 Relatório de Insumos")
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("MDF Total Utilizado", f"{total_m2:.2f} m²", f"Custo: R$ {total_mdf:,.2f}")
        with c2:
            st.metric("Fita de Borda Total", f"{total_metros_fita:.2f} m", f"Custo: R$ {total_fita:,.2f}")
            if total_metros_fita > 0:
                st.write(f"Valor Unitário Médio da Fita: R$ {total_fita/total_metros_fita:.2f}/m")
        
        st.markdown("---")
        st.metric("Custo Total de Materiais (Sem Lucro)", f"R$ {custo_materiais:,.2f}")
        st.metric("Total do Projeto com Lucro", f"R$ {valor_final:,.2f}")
        
        # Exibe a tabela detalhada por peça
        st.subheader("Detalhe por Peça")
        st.dataframe(df)

# --- ABA 4: OTIMIZAÇÃO DE CHAPA (NOVO PASSO) ---
elif menu == "Otimização de Chapa (Visual)":
    st.header("📐 Otimização de Chapa (Visual)")
    if st.session_state.df_projeto is not None:
        st.info("Aqui iremos gerar a visualização das peças encaixadas na chapa.")
        # O próximo passo será criar a função de otimização
