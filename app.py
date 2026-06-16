import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÕES ---
st.set_page_config(layout="wide", page_title="Marcenaria Pro")
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

def load_csv(file, cols):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_csv(FILE_CHAPAS, ['Material', 'Tipo', 'Preço_Unit', 'Custo_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_chapas.to_csv(FILE_CHAPAS, index=False)
        st.success("Chapas salvas!")

    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(load_csv(FILE_FITAS, ['Nome Fita', 'Valor Rolo', 'Metros Rolo', 'Custo Cola/Tempo(m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"):
        df_fitas.to_csv(FILE_FITAS, index=False)
        st.success("Fitas salvas!")

# --- ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        # 1. Leitura
        df = pd.read_csv(arquivo, sep=';')
        
        # 2. TRADUÇÃO E LIMPEZA (Aqui forçamos os nomes em português)
        rename_map = {
            "Part #": "Código", "Sub-Assembly": "Sub-Montagem", "Description": "Descrição",
            "Copies": "Quantidade", "Thickness(T)": "Material", "Width(W)": "Largura",
            "Length(L)": "Comprimento", "Can Rotate": "Rotação"
        }
        df = df.rename(columns=rename_map)
        cols_to_drop = ["Material Type", "Material Name", "Unnamed: 10"]
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        
        # 3. Adiciona colunas de fita se não existirem
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
            
        # 4. Lista do cadastro
        df_chapas = load_csv(FILE_CHAPAS, ['Material'])
        lista_materiais = df_chapas['Material'].dropna().unique().tolist()
        
        # 5. Editor com as colunas corretas e traduzidas
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
                "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
            },
            num_rows="dynamic", use_container_width=True
        )
        # --- ABA ORÇAMENTOS (Cole isto abaixo do final do bloco do Mapa de Corte) ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    # 1. Margem de Lucro
    margem = st.number_input("Margem de Lucro sobre o Custo (%)", min_value=0, value=30)
    
    if 'df' in st.session_state and st.session_state.df is not None:
        df_projeto = st.session_state.df
        df_chapas = load_csv(FILE_CHAPAS, ['Material', 'Preço_Unit'])
        df_fitas = load_csv(FILE_FITAS, ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        # Merge para trazer preço da chapa
        df_calc = df_projeto.merge(df_chapas, on='Material', how='left')
        
        # 2. Lógica de cálculo unificada
        def calcular_linha(row):
            # Custo da Chapa
            area_m2 = (row['Largura'] * row['Comprimento']) / 1000000
            custo_chapa = area_m2 * row.get('Preço_Unit', 0)
            
            # Custo da Fita
            custo_fita_total = 0
            if not df_fitas.empty:
                # Usa a primeira fita cadastrada como base no momento
                preco_fita = df_fitas.iloc[0]['Custo Total Aplicado (m)'] 
                if row.get('C1'): custo_fita_total += (row['Largura']/1000) * preco_fita
                if row.get('C2'): custo_fita_total += (row['Largura']/1000) * preco_fita
                if row.get('L1'): custo_fita_total += (row['Comprimento']/1000) * preco_fita
                if row.get('L2'): custo_fita_total += (row['Comprimento']/1000) * preco_fita
            
            return custo_chapa + custo_fita_total

        df_calc['Custo_Item'] = df_calc.apply(calcular_linha, axis=1)
        
        # 3. Totais
        custo_total = df_calc['Custo_Item'].sum()
        valor_venda = custo_total * (1 + (margem / 100))
        
        # Exibição
        st.metric("Custo de Produção", f"R$ {custo_total:,.2f}")
        st.metric("Preço Final (com margem)", f"R$ {valor_venda:,.2f}")
        
        st.subheader("Detalhamento por Peça")
        st.dataframe(df_calc[['Sub-Montagem', 'Descrição', 'Material', 'Custo_Item']])
        
    else:
        st.warning("Você precisa processar um arquivo na aba 'Mapa de Corte' primeiro.")
        # 6. BOTÃO DE OTIMIZAÇÃO (Aqui ele aparece abaixo da tabela)
        if st.button("🚀 Otimizar Chapas"):
            st.info("Otimizando chapas e gerando relatório de retalhos...")
            # Aqui entrará a lógica do motor de cálculo
