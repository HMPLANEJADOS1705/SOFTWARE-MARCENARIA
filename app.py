import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker  # Importação no TOPO do arquivo
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
        df = pd.read_csv(arquivo_csv, sep=';')
        
        # Limpeza necessária
        df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
        df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
        
        if st.button("Gerar Mapa de Corte (Automático)"):
            packer = newPacker()
            packer.add_bin(2750, 1840)
            
            for i, row in df.iterrows():
                packer.add_rect(row['Width_num'], row['Length_num'], rid=i)
            
            packer.pack()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            chapa = patches.Rectangle((0, 0), 2750, 1840, facecolor='#f0f0f0', edgecolor='black', linewidth=2)
            ax.add_patch(chapa)
            
            for rect in packer.rect_list():
                b, x, y, w, h, rid = rect
                peca = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='blue', facecolor='skyblue', alpha=0.7)
                ax.add_patch(peca)
                ax.text(x+w/2, y+h/2, str(df.iloc[rid]['Description']), ha='center', va='center', fontsize=6)
            
            ax.set_xlim(0, 2750)
            ax.set_ylim(0, 1840)
            st.pyplot(fig)

