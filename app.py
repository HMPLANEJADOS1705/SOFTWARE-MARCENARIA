import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

def load_csv(file, cols):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_csv(FILE_CHAPAS, ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_chapas.to_csv(FILE_CHAPAS, index=False)
        st.success("Salvo!")

# --- ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        # 1. Leitura
        df = pd.read_csv(arquivo, sep=';')
        
        # 2. Tradução Inteligente (Aceita nomes originais OU já traduzidos)
        mapa_de_nomes = {
            "Part #": "Código", "Thickness(T)": "Material", 
            "Width(W)": "Largura", "Length(L)": "Comprimento",
            "Copies": "Quantidade", "Description": "Descrição",
            "Sub-Assembly": "Sub-Montagem"
        }
        df = df.rename(columns=mapa_de_nomes)
        
        # 3. Garante que as colunas essenciais existam
        colunas_necessarias = ["Código", "Sub-Montagem", "Descrição", "Quantidade", "Material", "Largura", "Comprimento"]
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = "" # Cria a coluna vazia se não existir
        
        # 4. Garante colunas de fita
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns:
                df[f] = False
        
        # 5. Lista de materiais
        df_chapas = load_csv(FILE_CHAPAS, ['Material'])
        lista_mat = df_chapas['Material'].dropna().unique().tolist()
        
        # 6. Exibição
        st.session_state.df = st.data_editor(
            df[['Código', 'Sub-Montagem', 'Descrição', 'Quantidade', 'Material', 'Largura', 'Comprimento', 'C1', 'C2', 'L1', 'L2']],
            column_config={"Material": st.column_config.SelectboxColumn("Material", options=lista_mat)},
            num_rows="dynamic", use_container_width=True
        )
        
      # ... (seu código anterior do mapa de corte termina aqui) ...
        
        if st.button("🚀 Otimizar Chapas"):
            # O sistema agora vai pular direto para a aba de Orçamentos
            # salvando o estado atual para que o Orçamento consiga ler
            st.session_state.otimizado = True
            st.success("Otimização concluída! Vá para a aba 'Orçamentos' para ver os valores.")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    # Verifica se o usuário já clicou no botão de otimizar
    if 'otimizado' not in st.session_state:
        st.warning("⚠️ Você precisa ir no 'Mapa de Corte' e clicar em '🚀 Otimizar Chapas' antes de ver o orçamento.")
    else:
        # (Aqui entra todo o seu código de cálculo que fizemos antes)
        # O sistema agora tem certeza que o Mapa de Corte foi processado
        margem = st.number_input("Margem de Lucro (%)", value=30)
        # ... (restante do código de cálculo) ...
