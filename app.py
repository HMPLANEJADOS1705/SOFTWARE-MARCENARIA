import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(layout="wide", page_title="Painel de Produção Profissional")

st.title("🛠️ Painel de Produção Profissional (v4.0)")

# Sidebar com as ferramentas
with st.sidebar:
    st.header("Ferramentas Profissionais")
    st.button("Cadastro de Materiais")
    st.button("Cadastro de Clientes")
    st.info("Relatório de Projetos (v1.0) ativo")

# --- LÓGICA DE CÁLCULO ---
st.subheader("Entrada de Dados")
col1, col2, col3 = st.columns(3)
with col1:
    comp = st.number_input("Comprimento (mm)", value=1200)
with col2:
    larg = st.number_input("Largura (mm)", value=600)
with col3:
    qtd = st.number_input("Quantidade", value=1)

# Cálculo de Fita (Exemplo: borda em todo o perímetro)
metragem_fita = ((comp * 2) + (larg * 2)) / 1000

# --- EXIBIÇÃO ---
col_tabela, col_grafico = st.columns([2, 1])

with col_tabela:
    st.subheader("Tabela de Peças e Materiais")
    data = {
        "Peça": ["Lateral Esquerda", "Lateral Direita", "Fundo Gaveta"],
        "Material": ["MDF Branco", "MDF Branco", "MDF Branco"],
        "Metragem Fita (ml)": [metragem_fita, metragem_fita, 1.0]
    }
    df = pd.DataFrame(data)
    st.table(df)

with col_grafico:
    st.subheader("Custos Reais")
    custos = {"Material": 1200, "Mão de Obra": 800, "Ferragens": 550}
    st.bar_chart(custos)

# Ação Final
from fpdf import FPDF
import io

def gerar_pdf_proposta(dados_projeto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Cabeçalho
    pdf.cell(200, 10, txt="PROPOSTA COMERCIAL - MARCENARIA 4.0", ln=True, align='C')
    pdf.ln(10)
    
    # Conteúdo (Exemplo)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Cliente: Sr. Ricardo", ln=True)
    pdf.cell(200, 10, txt=f"Valor Total: R$ 2.550,00", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt="Esta proposta inclui material, ferragens e mão de obra detalhados no projeto.")
    
    # Retorna o PDF como bytes para o Streamlit
    return pdf.output()

# --- No seu código Streamlit ---
pdf_bytes = gerar_pdf_proposta(None) # Aqui passaremos os dados reais depois

st.download_button(
    label="📄 Baixar Proposta em PDF",
    data=bytes(pdf_bytes),
    file_name="proposta_ricardo.pdf",
    mime="application/pdf"
)
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- ESTRUTURA DE ABAS ---
tab1, tab2 = st.tabs(["📊 Painel de Produção", "🧩 Mapa de Corte (Otimização)"])

with tab1:
    st.header("Painel de Produção Profissional")
    # Aqui você mantém o código que já tem (Tabela, Gráficos, etc.)
    st.write("Seu painel principal continua aqui.")

with tab2:
    st.header("Visualização de Corte (Simulação)")
    st.info("Aqui iremos exibir o desenho das peças na chapa de MDF.")
    
    # Exemplo visual simples de uma chapa (2750 x 1840)
    fig, ax = plt.subplots(figsize=(10, 5))
    chapa = patches.Rectangle((0, 0), 2750, 1840, linewidth=2, edgecolor='black', facecolor='#f0f0f0')
    ax.add_patch(chapa)
    
    # Exemplo de uma peça sendo desenhada na chapa
    peca = patches.Rectangle((100, 100), 1200, 600, linewidth=1, edgecolor='blue', facecolor='skyblue', label="Lateral Esquerda")
    ax.add_patch(peca)
    
    ax.set_xlim(0, 3000)
    ax.set_ylim(0, 2000)
    ax.set_aspect('equal')
    ax.set_title("Layout da Chapa (Simulação)")
    
    st.pyplot(fig)

