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

menu = st.sidebar.radio("Navegação", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos", "Plano de Corte (Visual)"])

# --- ABA 1: CADASTRO DE INSUMOS ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Chapas (Material, Preço, Dimensões em mm)")
    
    # Nomes das colunas exatamente como na sua foto
    df_boards = st.data_editor(load_csv("materiais.csv", ['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_boards.to_csv("materiais.csv", index=False)
        st.success("Cadastro de Chapas Salvo!")
    
    st.subheader("Fitas")
    # Nomes das colunas exatamente como na sua foto
    df_tapes = st.data_editor(load_csv("fitas.csv", ['Nome Fita', 'Valor Rolo', 'Metros Rolo', 'Custo Cola/Tempo(m)', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"):
        df_tapes.to_csv("fitas.csv", index=False)
        st.success("Cadastro de Fitas Salvo!")

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
            st.write("Colunas detectadas:", df.columns.tolist())
            # Renomeação segura
            df = df.rename(columns={
                "Part #": "Código", 
                "Thickness(T)": "Material", 
                "Width(W)": "Largura(mm)", 
                "Length(L)": "Comprimento(mm)", 
                "Description": "Descrição",
                "Copies": "Quantidade"
            })
            df['Fita_Usada'] = ""; df['C1'] = False; df['C2'] = False; df['L1'] = False; df['L2'] = False
            st.session_state.df_projeto = df
            st.rerun()
    
    if st.session_state.df_projeto is not None:
        mats = load_csv("materiais.csv", ['Material'])['Material'].unique().tolist()
        tapes = load_csv("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        
        st.session_state.df_projeto = st.data_editor(st.session_state.df_projeto, key="tabela_corte", num_rows="dynamic", column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=mats),
            "Fita_Usada": st.column_config.SelectboxColumn("Fita_Usada", options=tapes)
        }, use_container_width=True)

# --- ABA 3: ORÇAMENTOS (RESTAURADO E SEGURO) ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        # Nomes das colunas como na sua foto
        boards = load_csv("materiais.csv", ['Material', 'Preço_Unit', 'Largura(mm)', 'Comprimento(mm)'])
        tapes = load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        # --- FUNÇÃO DE CÁLCULO REVISADA E SEGURA ---
        def calculate_row(row):
            def clean(v): 
                try: return float(''.join([c for c in str(v) if c.isdigit() or c == '.']))
                except: return 0.0
            
            try:
                l = clean(row.get('Largura(mm)', 0))
                w = clean(row.get('Comprimento(mm)', 0))
                qtd = clean(row.get('Quantidade', 1))
                area_m2 = (l * w * qtd) / 1000000
                
                mat = str(row.get('Material', '')).strip().lower()
                b_match = boards[boards['Material'].astype(str).str.strip().str.lower() == mat]
                
                if b_match.empty: return pd.Series([0.0, 0.0, area_m2, 0.0])
                
                # Custo MDF seguro
                preco_base = float(b_match['Preço_Unit'].values[0])
                l_c = float(b_match['Largura(mm)'].values[0] or 2750)
                c_c = float(b_match['Comprimento(mm)'].values[0] or 1840)
                preco_m2 = preco_base / ((l_c * c_c) / 1000000)
                cost_mat = area_m2 * preco_m2
                
                # Fitas seguro
                tape = str(row.get('Fita_Usada', '')).strip().lower()
                t_match = tapes[tapes['Nome Fita'].astype(str).str.strip().str.lower() == tape]
                cost_tape, metragem_fita = 0.0, 0.0
                if not t_match.empty:
                    p_tape = float(t_match['Custo Total Aplicado (m)'].values[0])
                    # Soma se a borda estiver marcada (True/False)
                    if row.get('C1'): metragem_fita += (l/1000) * qtd; cost_tape += (l/1000) * qtd * p_tape
                    if row.get('C2'): metragem_fita += (l/1000) * qtd; cost_tape += (l/1000) * qtd * p_tape
                    if row.get('L1'): metragem_fita += (w/1000) * qtd; cost_tape += (w/1000) * qtd * p_tape
                    if row.get('L2'): metragem_fita += (w/1000) * qtd; cost_tape += (w/1000) * qtd * p_tape
                    
                return pd.Series([cost_mat, cost_tape, area_m2, metragem_fita])
            except: return pd.Series([0.0, 0.0, 0.0, 0.0])

        df[['Custo_MDF', 'Custo_Fita', 'Area_M2', 'Metros_Fita']] = df.apply(calculate_row, axis=1)
        
        # --- RELATÓRIO DE INSUMOS ---
        st.subheader("📋 Relatório Detalhado de Insumos")
        
        c1, c2 = st.columns(2)
        total_m2 = df['Area_M2'].sum()
        total_mdf = df['Custo_MDF'].sum()
        total_fita = df['Custo_Fita'].sum()
        total_metros_fita = df['Metros_Fita'].sum()
        
        # Obter preço unitário médio da fita
        preco_unit_fita = total_fita / total_metros_fita if total_metros_fita > 0 else 0
        
        with c1:
            st.metric("MDF Utilizado", f"{total_m2:.2f} m²")
            st.write(f"Custo MDF: R$ {total_mdf:,.2f}")
        with c2:
            st.metric("Fita de Borda Utilizada", f"{total_metros_fita:.2f} m")
            st.write(f"Custo Fita: R$ {total_fita:,.2f}")
            st.write(f"**Valor Unitário da Fita:** R$ {preco_unit_fita:.2f}/m")
        
        valor_final = (total_mdf + total_fita) * (1 + taxa_lucro)
        
        st.markdown("---")
        st.metric("Total do Projeto com Lucro", f"R$ {valor_final:,.2f}")
        st.dataframe(df)

# --- ABA 4: PLANO DE CORTE (VISUAL) ---
elif menu == "Plano de Corte (Visual)":
    st.header("📐 Ilustração das Chapas")
    if st.session_state.df_projeto is not None:
        st.info("Módulo de Otimização Visual sendo carregado...")
        # Este é o ponto de partida para desenhar o plano de corte.
        # Precisaremos de uma função que pegue as peças (L/C/Qtd) e 
        # encaixe em quadros que representam as chapas (L_Chapa / C_Chapa).
      
