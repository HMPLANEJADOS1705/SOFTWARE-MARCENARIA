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
            
          # Dentro do loop de espessuras
        if st.button(f"Otimizar Chapas para {espessura}"):
            container_resultado = st.container() # Cria uma área dedicada ao resultado
            
            with container_resultado:
                packer = newPacker(rotation=True)
                for _ in range(5): 
                    packer.add_bin(2750, 1840)
                
                # ... (seu código de packer.add_rect e packer.pack continua igual) ...
                
                packer.pack()
                
                # Exibe cada chapa dentro do container
                for i, bin in enumerate(packer):
                    if len(bin.rect_list()) > 0:
                        st.write(f"### Chapa {i+1}")
                        fig, ax = plt.subplots(figsize=(8, 4))
                        # ... (seu código de desenho continua aqui) ...
                        st.pyplot(fig) # Agora o pyplot sabe onde desenhar
