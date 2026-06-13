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
    st.header("Otimização de Corte Profissional")
    arquivo_csv = st.file_uploader("Carregue seu CSV", type="csv")
    
    if arquivo_csv is not None:
        df = pd.read_csv(arquivo_csv, sep=';')
        
        # Limpeza necessária
        df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
        df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
        
        # Agrupa por espessura
        espessuras = df['Thickness(T)'].unique()
        
        for espessura in espessuras:
            st.subheader(f"Material: {espessura}")
            # Reseta o índice para evitar o erro de 'out-of-bounds'
            pecas_espessura = df[df['Thickness(T)'] == espessura].reset_index(drop=True)
            
            if st.button(f"Otimizar Chapas para {espessura}"):
                packer = newPacker(rotation=True)
                for _ in range(5): 
                    packer.add_bin(2750, 1840)
                
                for i, row in pecas_espessura.iterrows():
                    packer.add_rect(row['Width_num'], row['Length_num'], rid=i)
                
                packer.pack()
                
                # --- NOVO BLOCO DE DESENHO ROBUSTO ---
                # Acessa todos os retângulos processados, independentemente da chapa
                all_rects = packer.rect_list()
                
                st.write(f"Total de peças na lista: {len(pecas_espessura)}")
                st.write(f"Peças que o algoritmo conseguiu encaixar: {len(all_rects)}")
                
                # Agrupa os retângulos por número da chapa (bin index)
                # O rectpack organiza os resultados em uma lista de retângulos (b, x, y, w, h, rid)
                # Onde 'b' é o índice da chapa (0 para a primeira, 1 para a segunda, etc.)
                
                max_bin = max([r[0] for r in all_rects]) if all_rects else 0
                
                for bin_idx in range(max_bin + 1):
                    st.write(f"### Chapa {bin_idx + 1}")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.add_patch(patches.Rectangle((0, 0), 2750, 1840, fill=False, edgecolor='black', linewidth=3))
                    
                    # Filtra apenas peças desta chapa
                    rects_in_bin = [r for r in all_rects if r[0] == bin_idx]
                    
                    for rect in rects_in_bin:
                        b, x, y, w, h, rid = rect
                        ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='blue', facecolor='skyblue', alpha=0.6))
                        
                        # Nome da peça
                        nome_peca = pecas_espessura.iloc[rid]['Description']
                        ax.text(x+w/2, y+h/2, str(nome_peca), ha='center', va='center', fontsize=6)
                    
                    ax.set_xlim(0, 2750)
                    ax.set_ylim(0, 1840)
                    st.pyplot(fig)
