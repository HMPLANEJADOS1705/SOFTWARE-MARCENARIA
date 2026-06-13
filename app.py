import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

# Configuração de Layout
st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- BARRA LATERAL (Menu de Navegação) ---
with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])
    st.divider()
    st.write("Versão 1.0 - Alpha")

# --- FUNÇÕES AUXILIARES ---
def desenhar_peca_com_fitas(ax, x, y, w, h, fitas, nome):
    ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='black', facecolor='#E0E0E0'))
    if fitas.get('C1'): ax.add_patch(patches.Rectangle((x, y + h - 3), w, 3, color='red'))
    if fitas.get('C2'): ax.add_patch(patches.Rectangle((x, y), w, 3, color='red'))
    if fitas.get('L1'): ax.add_patch(patches.Rectangle((x, y), 3, h, color='red'))
    if fitas.get('L2'): ax.add_patch(patches.Rectangle((x + w - 3, y), 3, h, color='red'))
    rotacao = 90 if h > w else 0
    ax.text(x + w/2, y + h/2, nome, ha='center', va='center', fontsize=7, rotation=rotacao, color='black')

# --- LÓGICA DO SISTEMA ---
if menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte e Otimização")
    arquivo_csv = st.file_uploader("Carregue seu CSV de peças", type="csv")
    
    if arquivo_csv:
        df = pd.read_csv(arquivo_csv, sep=';')
        # ... (seu código de processamento de dados e otimização aqui) ...
        # DICA: Mantenha o código de otimização aqui, ele já está funcionando perfeitamente!

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.info("Aqui consolidaremos o custo das peças + fita + insumos cadastrados.")
    # Colocaremos aqui o botão para gerar PDF e o resumo financeiro
    if st.button("Gerar Orçamento em PDF"):
        st.write("Funcionalidade em desenvolvimento...")

elif menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos e Chapas")
    st.write("Gerencie aqui suas chapas, fitas e acessórios (puxadores, etc).")
    # Futuramente: st.data_editor para cadastro de preços e medidas de barras
