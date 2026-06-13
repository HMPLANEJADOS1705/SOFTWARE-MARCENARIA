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
        
      from rectpack import newPacker

# --- LÓGICA DO ALGORITMO DE ENCAIXE ---
if st.button("Gerar Mapa de Corte (Automático)"):
    # 1. Configura o "empacotador"
    packer = newPacker()
    
    # 2. Adiciona a chapa (Bin)
    packer.add_bin(2750, 1840)
    
    # 3. Adiciona todas as peças do CSV
    for i, row in df.iterrows():
        # Largura e comprimento do CSV
        w = float(row['Width_num'])
        l = float(row['Length_num'])
        packer.add_rect(w, l, rid=i)
    
    # 4. Processa o encaixe
    packer.pack()
    
    # 5. Desenha o resultado
    fig, ax = plt.subplots(figsize=(10, 6))
    chapa = patches.Rectangle((0, 0), 2750, 1840, facecolor='#f0f0f0', edgecolor='black', linewidth=2)
    ax.add_patch(chapa)
    
    # Desenha cada peça na sua posição calculada
    for rect in packer.rect_list():
        b, x, y, w, h, rid = rect
        peca = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='blue', facecolor='skyblue', alpha=0.7)
        ax.add_patch(peca)
        ax.text(x+w/2, y+h/2, str(df.iloc[rid]['Description']), ha='center', va='center', fontsize=8)
    
    ax.set_xlim(0, 2750)
    ax.set_ylim(0, 1840)
    st.pyplot(fig)

