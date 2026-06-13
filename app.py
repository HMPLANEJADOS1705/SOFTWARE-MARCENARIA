import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

st.set_page_config(layout="wide")
st.title("Painel de Produção Profissional")

# Função para desenhar a peça com indicadores de fita
def desenhar_peca_com_fitas(ax, x, y, w, h, fitas, nome):
    # Fundo da peça
    ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='black', facecolor='#E0E0E0'))
    
    # Linhas de fita (indicadas por bordas vermelhas mais grossas)
    margem = 0 
    if fitas.get('C1'): ax.add_patch(patches.Rectangle((x, y + h - 3), w, 3, color='red'))
    if fitas.get('C2'): ax.add_patch(patches.Rectangle((x, y), w, 3, color='red'))
    if fitas.get('L1'): ax.add_patch(patches.Rectangle((x, y), 3, h, color='red'))
    if fitas.get('L2'): ax.add_patch(patches.Rectangle((x + w - 3, y), 3, h, color='red'))

    # Texto da peça
    rotacao = 90 if h > w else 0
    ax.text(x + w/2, y + h/2, nome, ha='center', va='center', fontsize=7, rotation=rotacao, color='black')

tab1, tab2 = st.tabs(["Orçamento", "Mapa de Corte (Otimização)"])

with tab2:
    st.header("Otimização de Corte Profissional")
    arquivo_csv = st.file_uploader("Carregue seu CSV", type="csv")
    
    if arquivo_csv is not None:
        df_base = pd.read_csv(arquivo_csv, sep=';')
        
        # Garante colunas de fita
        for lado in ['C1', 'C2', 'L1', 'L2']:
            if lado not in df_base.columns: df_base[lado] = False
        
        st.subheader("Lista de Peças e Configuração de Fitas")
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
                for _ in range(20): packer.add_bin(2750, 1840)
                
                for i, row in pecas_espessura.iterrows():
                    packer.add_rect(row['Width_num'] + SERRA, row['Length_num'] + SERRA, rid=i)
                
                packer.pack()
                all_rects = packer.rect_list()
                used_bins = sorted(list(set([r[0] for r in all_rects])))
                
                for bin_idx in used_bins:
                    st.write(f"### Chapa {bin_idx + 1}")
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.add_patch(patches.Rectangle((0, 0), 2750, 1840, fill=False, edgecolor='black', linewidth=2))
                    
                    for rect in [r for r in all_rects if r[0] == bin_idx]:
                        _, x, y, w, h, rid = rect
                        # Recupera dados de fita da linha original
                        fitas = {
                            'C1': pecas_espessura.iloc[rid]['C1'],
                            'C2': pecas_espessura.iloc[rid]['C2'],
                            'L1': pecas_espessura.iloc[rid]['L1'],
                            'L2': pecas_espessura.iloc[rid]['L2']
                        }
                        desenhar_peca_com_fitas(ax, x, y, w, h, fitas, pecas_espessura.iloc[rid]['Description'])
                    
                    ax.set_xlim(-50, 2800); ax.set_ylim(-50, 1900); ax.set_aspect('equal')
                    st.pyplot(fig)
