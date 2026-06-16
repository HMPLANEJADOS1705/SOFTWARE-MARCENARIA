import streamlit as st
import pandas as pd
import os

# --- ARQUIVOS ---
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

# Função que garante a leitura mesmo que o arquivo tenha colunas diferentes
def load_data(filename, default_cols):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        # Se faltar alguma coluna, adicionamos ela vazia para não dar erro
        for col in default_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=default_cols)

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    
    # Chapas
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_data(FILE_CHAPAS, ['Material', 'Tipo', 'Preço_Unit', 'Custo_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"): 
        df_chapas.to_csv(FILE_CHAPAS, index=False)
        st.success("Chapas salvas!")
    
    # Fitas
    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(load_data(FILE_FITAS, ['Nome Fita', 'Valor Rolo', 'Metros Rolo', 'Custo Cola/Tempo(m)']), num_rows="dynamic")
  # ... dentro da aba de cadastro, na parte de fitas ...
    if st.button("💾 Salvar Fitas"):
        # Força a conversão para numérico, transformando erros em 0
        df_fitas['Valor Rolo'] = pd.to_numeric(df_fitas['Valor Rolo'], errors='coerce').fillna(0)
        df_fitas['Metros Rolo'] = pd.to_numeric(df_fitas['Metros Rolo'], errors='coerce').fillna(0)
        df_fitas['Custo Cola/Tempo(m)'] = pd.to_numeric(df_fitas['Custo Cola/Tempo(m)'], errors='coerce').fillna(0)
        
        # Agora o cálculo é seguro
        # Evita divisão por zero se Metros Rolo for 0
        df_fitas['Preço por Metro (Base)'] = df_fitas.apply(
            lambda x: x['Valor Rolo'] / x['Metros Rolo'] if x['Metros Rolo'] > 0 else 0, axis=1
        )
        
        df_fitas['Custo Total Aplicado (m)'] = df_fitas['Preço por Metro (Base)'] + df_fitas['Custo Cola/Tempo(m)']
        
        df_fitas.to_csv(FILE_FITAS, index=False)
        st.success("Fitas salvas com sucesso!")
        st.rerun() # Recarrega a página para atualizar a tabela
# --- ABA DE MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV (do SketchUp)", type="csv")
    
    if arquivo:
        # 1. Leitura
        df = pd.read_csv(arquivo, sep=';')
        
        # 2. Limpeza Imediata (Remove as colunas indesejadas)
        cols_to_drop = ["Material Type", "Material Name", "Unnamed: 10"]
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        
        # 3. Renomeação (Mantém o padrão em Português)
        rename_map = {
            "Part #": "Código",
            "Sub-Assembly": "Sub-Montagem",
            "Description": "Descrição",
            "Copies": "Quantidade",
            "Thickness(T)": "Material",
            "Width(W)": "Largura",
            "Length(L)": "Comprimento",
            "Can Rotate": "Rotação"
        }
        df = df.rename(columns=rename_map)
        
        # 4. Garantir colunas de fita
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
            
        # 5. Lista suspensa (Puxa os materiais do arquivo 'materiais.csv' que já salvamos)
        lista_materiais = load_csv(FILE_CHAPAS, ['Material'])['Material'].dropna().unique().tolist()
        
        # 6. Exibição (Configuração visual)
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
                "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
            },
            num_rows="dynamic",
            use_container_width=True
        )

# --- ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    margem = st.number_input("Margem de Lucro (%)", value=30)
    
    if 'df' in st.session_state:
        # Lógica: Cruzar peças do projeto com custos cadastrados
        # 1. Calcular área e custo de chapa
        # 2. Calcular metros de fita (C1+C2+L1+L2 == True) * (Preço + Custo_Aplicacao)
        # 3. Aplicar Margem
        st.write("Orçamento detalhado será gerado aqui.")
