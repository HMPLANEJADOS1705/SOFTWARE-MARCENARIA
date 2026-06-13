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
    st.header("Gestão e Otimização de Corte")
    arquivo_csv = st.file_uploader("Carregue seu CSV", type="csv")
    
    if arquivo_csv is not None:
        # Carrega e permite edição
        df_base = pd.read_csv(arquivo_csv, sep=';')
        
        st.subheader("Lista de Peças (Edite aqui antes de Otimizar)")
        # st.data_editor permite adicionar/remover/editar valores
        df = st.data_editor(df_base, num_rows="dynamic")
        
        # Limpeza para cálculo
        df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
        df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
        
        # Filtragem por espessura exclusiva
        espessuras = df['Thickness(T)'].unique()
        
        for espessura in espessuras:
            st.divider()
            st.subheader(f"Processando Material: {espessura}")
            pecas_espessura = df[df['Thickness(T)'] == espessura].reset_index(drop=True)
            
            if st.button(f"Otimizar Chapas para {espessura}"):
                # O segredo: Strategy. Guillotine ou MaxRects são mais eficientes que o padrão
                from rectpack import PackingMode
                packer = newPacker(rotation=True, mode=PackingMode.Offline)
                
                # Adiciona chapas sob demanda
                for _ in range(10): 
                    packer.add_bin(2750, 1840)
                
                for i, row in pecas_espessura.iterrows():
                    packer.add_rect(row['Width_num'], row['Length_num'], rid=i)
                
                packer.pack()
                
                # Exibe resultado com rotação visível
                all_rects = packer.rect_list()
                for bin_idx in range(max([r[0] for r in all_rects]) + 1):
                    st.write(f"### Chapa {bin_idx + 1} ({espessura})")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.add_patch(patches.Rectangle((0, 0), 2750, 1840, fill=False, edgecolor='black', linewidth=3))
                    
                    for rect in [r for r in all_rects if r[0] == bin_idx]:
                        _, x, y, w, h, rid = rect
                        # Desenha a peça
                        ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='red', facecolor='orange', alpha=0.6))
                        # Indica se houve rotação (nome da peça de lado)
                        nome_peca = pecas_espessura.iloc[rid]['Description']
                        ax.text(x+w/2, y+h/2, str(nome_peca), ha='center', va='center', fontsize=6, rotation=0)
                    
                    ax.set_xlim(0, 2750)
                    ax.set_ylim(0, 1840)
                    st.pyplot(fig)
