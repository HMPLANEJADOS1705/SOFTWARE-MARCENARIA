import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

st.set_page_config(layout="wide")
st.title("Painel de Produção Profissional")

tab1, tab2 = st.tabs(["Orçamento", "Mapa de Corte (Otimização)"])

with tab2:
    st.header("Otimização de Corte Profissional")
    arquivo_csv = st.file_uploader("Carregue seu CSV", type="csv")
    
    if arquivo_csv is not None:
        df_base = pd.read_csv(arquivo_csv, sep=';')
        df = st.data_editor(df_base, num_rows="dynamic")
        
        df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
        df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
        
        espessuras = df['Thickness(T)'].unique()
        SERRA = 3 
        
        for espessura in espessuras:
            st.divider()
            st.subheader(f"Material: {espessura}")
            
            pecas_espessura = df[df['Thickness(T)'] == espessura].copy()
            pecas_espessura = pecas_espessura.sort_values(by=['Width_num', 'Length_num'], ascending=False).reset_index(drop=True)
            
            if st.button(f"Otimizar Chapas para {espessura}"):
                packer = newPacker(rotation=True, mode=PackingMode.Offline)
                
                # Adiciona um limite alto, mas o loop de desenho só processará as que tiverem peças
                for _ in range(20): 
                    packer.add_bin(2750, 1840)
                
                for i, row in pecas_espessura.iterrows():
                    packer.add_rect(row['Width_num'] + SERRA, row['Length_num'] + SERRA, rid=i)
                
                packer.pack()
                
                all_rects = packer.rect_list()
                
                # Identifica quantas chapas foram efetivamente usadas
                used_bins = sorted(list(set([r[0] for r in all_rects])))
                
                for bin_idx in used_bins:
                    st.write(f"### Chapa {bin_idx + 1}")
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.add_patch(patches.Rectangle((0, 0), 2750, 1840, fill=False, edgecolor='black', linewidth=2))
                    
                    for rect in [r for r in all_rects if r[0] == bin_idx]:
                        _, x, y, w, h, rid = rect
                        ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='black', facecolor='#E0E0E0', alpha=0.7))
                        
                        nome_peca = pecas_espessura.iloc[rid]['Description']
                        # Gira o texto se a peça for mais alta que larga
                        rotacao = 90 if h > w else 0
                        
                        ax.text(x + w/2, y + h/2, str(nome_peca), ha='center', va='center', 
                                fontsize=8, color='black', rotation=rotacao)
                    
                    ax.set_xlim(-50, 2800)
                    ax.set_ylim(-50, 1900)
                    ax.set_aspect('equal')
                    st.pyplot(fig)
