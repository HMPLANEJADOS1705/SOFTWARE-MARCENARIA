import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])
if 'df' not in st.session_state:
    st.session_state.df = None

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- FUNÇÕES ---
def desenhar_peca(ax, x, y, w, h, fitas, nome):
    ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='black', facecolor='#E0E0E0'))
    if fitas.get('C1'): ax.add_patch(patches.Rectangle((x, y + h - 3), w, 3, color='red'))
    if fitas.get('C2'): ax.add_patch(patches.Rectangle((x, y), w, 3, color='red'))
    if fitas.get('L1'): ax.add_patch(patches.Rectangle((x, y), 3, h, color='red'))
    if fitas.get('L2'): ax.add_patch(patches.Rectangle((x + w - 3, y), 3, h, color='red'))
    rot = 90 if h > w else 0
    ax.text(x + w/2, y + h/2, nome, ha='center', va='center', fontsize=7, rotation=rot)

# --- ROTAS ---
if menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df_base = pd.read_csv(arquivo, sep=';')
        # Lista de materiais cadastrados para o dropdown
        lista_materiais = st.session_state.estoque['Material'].tolist()
        
        st.session_state.df = st.data_editor(
            df_base, 
            column_config={"Thickness(T)": st.column_config.SelectboxColumn("Material", options=lista_materiais)},
            num_rows="dynamic"
        )
        
        if st.button("Otimizar Chapas"):
            df = st.session_state.df
            df['Width_num'] = df['Width(W)'].astype(str).str.replace(' mm', '').astype(float)
            df['Length_num'] = df['Length(L)'].astype(str).str.replace(' mm', '').astype(float)
            
            for mat in df['Thickness(T)'].unique():
                st.subheader(f"Material: {mat}")
                pecas = df[df['Thickness(T)'] == mat]
                packer = newPacker(rotation=True, mode=PackingMode.Offline)
                for _ in range(10): packer.add_bin(2750, 1840)
                for i, row in pecas.iterrows(): packer.add_rect(row['Width_num']+3, row['Length_num']+3, rid=i)
                packer.pack()
                for b in sorted(list(set([r[0] for r in packer.rect_list()]))):
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.add_patch(patches.Rectangle((0,0), 2750, 1840, fill=False))
                    for r in [rect for rect in packer.rect_list() if rect[0]==b]:
                        desenhar_peca(ax, r[1], r[2], r[3], r[4], {'C1':False}, "Peça")
                    st.pyplot(fig)

elif menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", key="estoque_editor")

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.df is not None:
        if st.button("Calcular Projeto"):
            df_pecas = st.session_state.df
            resumo = []
            for mat in df_pecas['Thickness(T)'].unique():
                info = st.session_state.estoque[st.session_state.estoque['Material'] == mat]
                if not info.empty:
                    preco = info.iloc[0]['Preço_Unit']
                    resumo.append({"Material": mat, "Valor": preco})
            st.table(pd.DataFrame(resumo))
