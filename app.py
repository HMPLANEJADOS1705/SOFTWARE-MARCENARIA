import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Preço_Unit'])
if 'df' not in st.session_state:
    st.session_state.df = None

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- FUNÇÕES ---
def desenhar_peca(ax, x, y, w, h, fitas, nome):
    ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='black', facecolor='#E0E0E0'))
    # Indicações de Fita (C1, C2, L1, L2)
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
        # Garantir colunas de fita
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df_base.columns: df_base[f] = False
        
        # Dropdown para Material
        lista_materiais = st.session_state.estoque['Material'].tolist() if not st.session_state.estoque.empty else []
        
        st.session_state.df = st.data_editor(
            df_base, 
            column_config={"Thickness(T)": st.column_config.SelectboxColumn("Material", options=lista_materiais)},
            num_rows="dynamic"
        )
        
        # Dentro da aba "Mapa de Corte", após a otimização
        if st.button("Otimizar Chapas"):
            df = st.session_state.df
            # ... (código anterior de cálculo de área) ...
            
            # --- NOVA PRÉVIA DE VALOR ---
            st.subheader("📊 Prévia de Custo")
            total_previa = 0
            for mat in df['Thickness(T)'].unique():
                info = st.session_state.estoque[st.session_state.estoque['Material'] == mat]
                if not info.empty:
                    preco = info.iloc[0]['Preço_Unit']
                    # Cálculo rápido: Área total do material / 5.08
                    area = (df[df['Thickness(T)'] == mat]['Width_num'] * df[df['Thickness(T)'] == mat]['Length_num']).sum() / 1000000
                    custo_parcial = area * (preco / 5.08)
                    total_previa += custo_parcial
                    st.write(f"Material: {mat} | Custo parcial estimado: **R$ {custo_parcial:.2f}**")
            st.metric("Total Estimado", f"R$ {total_previa:.2f}")
            
            # ... (seu código de desenho das chapas continua abaixo) ...

elif menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.write("Gerencie suas chapas e insumos abaixo:")
    
    # Editor de estoque com salvamento via botão
    # Usamos o 'edited_df' para capturar o estado da tabela antes de salvar
    df_estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", key="estoque_editor")
    
    if st.button("💾 Salvar Cadastro"):
        st.session_state.estoque = df_estoque
        st.success("Cadastro salvo com sucesso e disponível para os cálculos!")

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if st.session_state.df is not None and not st.session_state.estoque.empty:
        # Seleção de estratégia
        modo_calculo = st.radio("Selecione a estratégia:", ["Por Área Utilizada (m²)", "Por Chapa Inteira"])
        
        if st.button("Gerar Cálculo do Projeto"):
            df_pecas = st.session_state.df
            df_estoque = st.session_state.estoque
            
            # Criamos uma lista para exibir os resultados
            resultados = []
            
            for material_selecionado in df_pecas['Thickness(T)'].unique():
                # Filtra peças deste material
                pecas_do_mat = df_pecas[df_pecas['Thickness(T)'] == material_selecionado]
                
                # Busca info no estoque
                info_est = df_estoque[df_estoque['Material'] == material_selecionado]
                
                if not info_est.empty:
                    preco_unit = info_est.iloc[0]['Preço_Unit']
                    
                    if modo_calculo == "Por Área Utilizada (m²)":
                        # Calcula área total das peças desse material
                        area_total = (pecas_do_mat['Width_num'] * pecas_do_mat['Length_num']).sum() / 1000000
                        # Calcula custo proporcional (considerando a chapa padrão 2.75x1.85 = 5.08m²)
                        valor_final = area_total * (preco_unit / 5.08)
                        resultados.append({"Material": material_selecionado, "Área Total (m²)": round(area_total, 2), "Custo Estimado R$": round(valor_final, 2)})
                    
                    else:
                        # Cálculo simples: assume 1 chapa (ou podemos aprimorar depois)
                        valor_final = preco_unit
                        resultados.append({"Material": material_selecionado, "Base": "Chapa Inteira", "Custo R$": round(valor_final, 2)})
            
            # Exibe tabela final
            st.table(pd.DataFrame(resultados))
            
    else:
        st.warning("⚠️ Atenção: Certifique-se de que o CSV está carregado no 'Mapa de Corte' e o Cadastro de Insumos está salvo.")
