import streamlit as st
import pandas as pd
import numpy as np

# Configuração Profissional da Página
st.set_page_config(page_title="Gestão de Marcenaria PRO", layout="wide")
st.title("🪚 Software de Gestão de Marcenaria Professional")

# Inicialização segura do Cadastro de Materiais
if 'materiais' not in st.session_state:
    st.session_state.materiais = []

# Barra Lateral Esquerda Profissional
menu = st.sidebar.selectbox("Menu Profissional", ["Importar Lista CSV", "Cadastro de Materiais", "Dashboard"])

# --- MENU: DASHBOARD ---
if menu == "Dashboard":
    st.subheader("Resumo Geral")
    st.write("Bem-vindo ao seu painel de controle.")

# --- MENU: CADASTRO DE MATERIAIS ---
elif menu == "Cadastro de Materiais":
    st.subheader("Cadastro de Materiais e Insumos")
    with st.form("form_material_pro"):
        nome_mat = st.text_input("Nome do Material (ex: MDF 15mm)")
        esp_mat = st.number_input("Espessura (mm)", min_value=1, value=15)
        preco_mat = st.number_input("Preço de Custo (R$)", value=0.0)
        markup_mat = st.slider("Markup de Lucro (%)", 0, 100, 30)
        btn_salvar = st.form_submit_button("Salvar")
        
        if btn_salvar and nome_mat:
            st.session_state.materiais.append({"Nome": nome_mat, "Espessura (mm)": esp_mat, "Preço Custo": preco_mat, "Markup": markup_mat})
            st.rerun()

    if st.session_state.materiais:
        st.table(pd.DataFrame(st.session_state.materiais))
        if st.button("Limpar lista de materiais"):
            st.session_state.materiais = []
            st.rerun()

# --- MENU: IMPORTAR CSV E CALCULAR ---
elif menu == "Importar Lista CSV":
    st.subheader("Importar e Pré-visualizar Lista do SketchUp")
    arquivo = st.file_uploader("Arraste seu arquivo CSV aqui", type="csv")
    
    if arquivo:
        # Carrega e exibe a lista ANTES de calcular
        df = pd.read_csv(arquivo, sep=';')
        st.write("Lista de peças encontrada:")
        st.dataframe(df) # Isso traz de volta a pré-visualização que você queria
        
        if st.button("Gerar Orçamento Real"):
            if not st.session_state.materiais:
                st.error("Cadastre materiais primeiro!")
            else:
                total_projeto = 0
                detalhes = []
                
                # Conversão segura das medidas
                df['Width(W)'] = pd.to_numeric(df['Width(W)'].replace(r' mm', '', regex=True))
                df['Length(L)'] = pd.to_numeric(df['Length(L)'].replace(r' mm', '', regex=True))
                
                # Loop de cálculo com padronização de espessura
                for index, row in df.iterrows():
                    # Padroniza: Limpa "mm" e espaços do CSV
                    esp_peca_str = str(row['Thickness(T)']).replace(' mm', '').strip()
                    area_m2 = (row['Width(W)'] * row['Length(L)'] * row['Copies']) / 1_000_000 # mm² p/ m²
                    
                    mat_usado = "Não encontrado"
                    custo_linha = 0
                    
                    # Procura o material que tenha a espessura numérico exata
                    for mat in st.session_state.materiais:
                        if int(esp_peca_str) == mat['Espessura (mm)']:
                            # Cálculo: Área * Preço de Venda
                            preco_venda = mat['Preço Custo'] * (1 + mat['Markup']/100)
                            custo_linha = area_m2 * preco_venda
                            mat_usado = mat['Nome']
                            break
                    
                    total_projeto += custo_linha
                    detalhes.append({'Peça': row['Description'], 'Espessura (mm)': esp_peca_str, 'Material Usado': mat_usado, 'Custo Peça': custo_linha})
                
                st.metric("Valor Total do Projeto (MDF)", f"R$ {total_projeto:,.2f}")
                st.write("Detalhamento por Peça:")
                st.table(pd.DataFrame(detalhes))
