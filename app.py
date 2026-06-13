import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

# Configuração da página para ocupar a tela toda
st.set_page_config(layout="wide")

st.title("Painel de Produção Profissional")

# Aba para navegação
tab1, tab2 = st.tabs(["Orçamento", "Mapa de Corte (Otimização)"])

with tab2:
    st.header("Otimização de Corte Profissional")
    arquivo_csv = st.file_uploader("Carregue seu CSV", type="csv")
    
    if arquivo_csv is not None:
        # Carrega o CSV original
        df_base = pd.read_csv(arquivo_csv, sep=';')
        
        st.subheader("Lista de Peças (Edite aqui antes de Otimizar)")
        # Tabela editável para ajustes manuais
        df = st.data_editor(df_base, num_rows="dynamic")
        
        # Limpeza para cálculo
        df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
        df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
        
        # Filtragem e Otimização por espessura
        espessuras = df['Thickness(T)'].unique()
        SERRA = 3 # Desconto de serra em mm
        
        for espessura in espessuras:
            st.divider()
            st.subheader(f"Material: {espessura}")
            
            # Filtra, reseta índice e ORDENA pelas maiores peças primeiro (melhora a otimização)
            pecas_espessura = df[df['Thickness(T)'] == espessura].copy()
            pecas_espessura = pecas_espessura.sort_values(by=['Width_num', 'Length_num'], ascending=False).reset_index(drop=True)
            
            if st.button(f"Otimizar Chapas para {espessura}"):
                packer = newPacker(rotation=True, mode=PackingMode.Offline)
                
                # Adiciona chapas (reservatório)
                for _ in range(10): 
                    packer.add_bin(2750, 1840)
                
                # Adiciona peças com desconto da serra
                for i, row in pecas_espessura.iterrows():
                    packer.add_rect(row['Width_num'] + SERRA, row['Length_num'] + SERRA, rid=i)
                
                packer.pack()
                
                all_rects = packer.rect_list()
                st.write(f"Total de peças: {len(pecas_espessura)} | Encaixadas: {len(all_rects)}")
                
                # Desenho das chapas
                max_bin = max([r[0] for r in all_rects]) if all_rects else 0
                for bin_idx in range(max_bin + 1):
                    st.write(f"### Chapa {bin_idx + 1}")
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.add_patch(patches.Rectangle((0, 0), 2750, 1840, fill=False, edgecolor='black', linewidth=3))
                    
                    for rect in [r for r in all_rects if r[0] == bin_idx]:
                        _, x, y, w, h, rid = rect
                        # Desenha a peça
                        ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='blue', facecolor='skyblue', alpha=0.6))
                        
                        nome_peca = pecas_espessura.iloc[rid]['Description']
                        ax.text(x+w/2, y+h/2, str(nome_peca), ha='center', va='center', 
                                fontsize=7, fontweight='bold', color='white', 
                                bbox=dict(facecolor='black', alpha=0.5))
                    
                    ax.set_xlim(0, 2750)
                    ax.set_ylim(0, 1840)
                    st.pyplot(fig)
