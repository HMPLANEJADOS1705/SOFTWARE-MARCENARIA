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
        # AQUI ESTÁ A CORREÇÃO: adicionamos sep=';'
        df = pd.read_csv(arquivo_csv, sep=';')
        
        st.write("Colunas encontradas:")
        st.write(df.columns.tolist()) 
        
        # Agora o Python vai enxergar as colunas corretamente!
        # Vamos usar os nomes exatos que apareceram na sua tela (com espaços se houver)
        # Note que eles estão sem os espaços extras que o Excel colocou
        colunas_desejadas = ['Description', 'Width(W)', 'Length(L)']
        
        # Verifica se as colunas estão lá agora
        if all(col in df.columns for col in colunas_desejadas):
            st.dataframe(df[colunas_desejadas])
        else:
            st.error("Ainda não encontrei as colunas. Verifique se os nomes batem exatamente com a lista acima.")
        
       # 2. Botão para desenhar
        if st.button("Gerar Mapa de Corte da Chapa"):
            try:
                # Limpeza: remove ' mm' e transforma em número
                df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
                df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
                
                st.info("Desenhando peças na chapa...")
                
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Desenha a borda da chapa (2750 x 1840)
                chapa = patches.Rectangle((0, 0), 2750, 1840, facecolor='#f0f0f0', edgecolor='black', linewidth=2)
                ax.add_patch(chapa)
                
                # Desenha a primeira peça da lista
                peca = patches.Rectangle((50, 50), df['Width_num'].iloc[0], df['Length_num'].iloc[0], 
                                         facecolor='skyblue', edgecolor='blue')
                ax.add_patch(peca)
                
                ax.set_xlim(0, 3000)
                ax.set_ylim(0, 2000)
                ax.set_title("Simulação: Primeira peça na Chapa")
                
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Erro ao gerar desenho: {e}")

