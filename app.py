import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configuração da página
st.set_page_config(layout="wide", page_title="Painel Marcenaria Pro")

st.title("🛠️ Painel de Produção Profissional")

# --- DEFINIÇÃO DAS ABAS ---
# Aqui criamos as abas. O Streamlit identifica automaticamente a ordem: 
# tab1 será a primeira, tab2 a segunda.
tab1, tab2 = st.tabs(["📊 Painel de Produção", "🧩 Mapa de Corte (Otimização)"])

# --- CONTEÚDO DA ABA 1 (Painel) ---
with tab1:
    st.header("Entrada de Dados e Orçamentos")
    st.write("Aqui ficará a sua tabela de peças e o gráfico de custos que você já tinha.")
    # Coloque o seu código original da aba 1 aqui abaixo:
    # ... (seu código de entrada de medidas e custos) ...

# --- CONTEÚDO DA ABA 2 (Mapa de Corte) ---
with tab2:
    st.header("Mapa de Corte (Otimização)")
    arquivo_csv = st.file_uploader("Carregue seu CSV", type="csv")
    
    if arquivo_csv is not None:
        df = pd.read_csv(arquivo_csv)
        
        # MOSTRAR NOMES REAIS DAS COLUNAS
        st.write("Colunas encontradas no seu arquivo:")
        st.write(df.columns.tolist()) 
        
        # Tente selecionar colunas apenas se elas existirem
        colunas_desejadas = [c for c in ['Description', 'Width(W)', 'Length(L)', 'Material'] if c in df.columns]
        
        if colunas_desejadas:
            st.dataframe(df[colunas_desejadas])
        else:
            st.error("Não encontrei as colunas esperadas. Verifique se o nome no arquivo está igual!")
        
        # 2. Botão para desenhar
        if st.button("Gerar Mapa de Corte da Chapa"):
            st.info("Desenhando peças na chapa de 2750x1840mm...")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Desenha a borda da chapa
            chapa = patches.Rectangle((0, 0), 2750, 1840, facecolor='#f0f0f0', edgecolor='black', linewidth=2)
            ax.add_patch(chapa)
            
            # Desenha a primeira peça como teste
            peca = patches.Rectangle((50, 50), df['Width(W)'].iloc[0], df['Length(L)'].iloc[0], 
                                     facecolor='skyblue', edgecolor='blue')
            ax.add_patch(peca)
            
            ax.set_xlim(0, 3000)
            ax.set_ylim(0, 2000)
            ax.set_title("Simulação de Encaixe na Chapa")
            
            st.pyplot(fig)
    else:
        st.warning("Por favor, carregue um arquivo CSV para visualizar o mapa de corte.")

