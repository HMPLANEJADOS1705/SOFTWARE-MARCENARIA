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
        # Limpeza básica (ajuste os nomes conforme necessário)
        df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
        df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
        
        # 1. Agrupar por espessura
        espessuras = df['Thickness(T)'].unique()
        
        for espessura in espessuras:
            st.subheader(f"Material: {espessura}")
            pecas_espessura = df[df['Thickness(T)'] == espessura]
            
            if st.button(f"Otimizar Chapas para {espessura}"):
                # 2. Configurar o Packer para múltiplas chapas
                packer = newPacker(rotation=True) # rotation=True ajuda muito no aproveitamento!
                
                # Adiciona várias chapas vazias (ex: 5 chapas)
                for _ in range(5): 
                    packer.add_bin(2750, 1840)
                
                for i, row in pecas_espessura.iterrows():
                    packer.add_rect(row['Width_num'], row['Length_num'], rid=i)
                
                packer.pack()
                
                # 3. Desenhar cada chapa individualmente
                for bin in packer:
                    if len(bin.rect_list()) > 0:
                        fig, ax = plt.subplots(figsize=(8, 4))
                        ax.add_patch(patches.Rectangle((0, 0), 2750, 1840, fill=False, edgecolor='black', linewidth=3))
                        
                      # Substitua o loop for rect in bin.rect_list(): por este abaixo:
                        for rect in bin:
                            # Tentamos acessar os atributos. Se o rectpack for uma versão 
                            # que trata como objeto, .x, .y, .width, .height funcionarão.
                            try:
                                x, y, w, h = rect.x, rect.y, rect.width, rect.height
                            except AttributeError:
                                # Caso a versão trate como tupla/lista indexada
                                x, y, w, h = rect[0], rect[1], rect[2], rect[3]
                            
                            rid = rect.rid
                            
                            ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='blue', facecolor='skyblue', alpha=0.6))
                            
                            # Recupera o nome da peça com segurança
                            nome_peca = pecas_espessura.iloc[rid]['Description'] if rid < len(pecas_espessura) else "Peça"
                            ax.text(x+w/2, y+h/2, str(nome_peca), ha='center', va='center', fontsize=6)
