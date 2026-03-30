from datetime import date
import pandas as pd

import streamlit as st
from src.database import obter_todos_dados_como_df
from src.components import (
    configurar_pagina,
    exibir_metricas_dashboard,
    exibir_graficos_principais,
    exibir_graficos_secundarios,
    renderizar_seletor_data,
)
from src.utils import (
    processar_dados_dashboard,
    expandir_unidades,
    formatar_unidades_para_tabela,
    lista_meses,
)

# 1. Configuração Inicial e Segurança
configurar_pagina("CleanLog - Dashboard Analítico")

st.title("📊 Painel de Indicadores")
df_bruto = obter_todos_dados_como_df()

if df_bruto.empty:
    st.info("💡 Sem dados para exibir. Realize o primeiro lançamento no formulário.")
    st.stop()

# 3. Sidebar: Filtros e Parâmetros
with st.sidebar:
    st.header("🔍 Filtros & Ajustes")
    funcionarios = ["Todos"] + sorted(df_bruto["Funcionário"].unique().tolist())
    funcionario_selecionado = st.selectbox("Colaborador", funcionarios)
    mostrar_valores = st.checkbox("Definir Valores p/ Hora", value=False)
    if mostrar_valores:
        valor_hora = st.number_input(
            "Valor da Hora (R$)", min_value=0.0, value=20.0, step=1.0
        )

# 4. Processamento de Dados (src.utils)
registro = processar_dados_dashboard(df_bruto, valor_hora if mostrar_valores else 0.0)
registro_expandido = expandir_unidades(registro)

# Aplicação do Filtro de Funcionário
filtro = (
    registro
    if funcionario_selecionado == "Todos"
    else registro[registro["Funcionário"] == funcionario_selecionado]
)

# 5. Visualização (src.components)
exibir_metricas_dashboard(filtro)
exibir_graficos_principais(filtro, registro_expandido, funcionario_selecionado)
exibir_graficos_secundarios(filtro, registro_expandido)

# 6. Exportação de Dados
st.divider()
st.write("### 📋 Exportar dados")

dias, meses, ano = renderizar_seletor_data()
meses_map = {nome.lower(): i + 1 for i, nome in enumerate(lista_meses)}

try:
    m_ini = meses[0].lower()
    m_fim = meses[1].lower()
    
    data_inicio_periodo = date(ano, meses_map[m_ini], dias[0])
    data_fim_periodo = date(ano, meses_map[m_fim], dias[1])
    
    df_exportar = filtro.copy()

    def converter_para_date(txt):
        try:
            d, m, a = txt.split("/")
            return date(int(a), meses_map[m.lower()], int(d))
        except:
            return None

    df_exportar["data_comparacao"] = df_exportar["Data"].apply(converter_para_date)
    
    mask = (df_exportar["data_comparacao"] >= data_inicio_periodo) & \
           (df_exportar["data_comparacao"] <= data_fim_periodo)
    
    df_final = df_exportar.loc[mask].drop(columns=["data_comparacao"]).copy()

except Exception as e:
    st.error(f"Erro na conversão de datas: {e}")
    df_final = pd.DataFrame()

# --- EXIBIÇÃO ---
tipo_visao = st.radio(
    "Tipo de Visão", ["Registro Diário", "Visão Geral"], horizontal=True
)
cols_financeiras = ["Custo_Dia", "Total (R$)"]

if df_final.empty:
    st.warning(
        f'⚠️ Nenhum registro encontrado para o período: "{dias[0]} de {meses[0].capitalize()}" a "{dias[1]} de {meses[1].capitalize()}" de {ano}.'
    )
else:
    nome_periodo = f"{dias[0]}{meses[0]}_ate_{dias[1]}{meses[1]}_{ano}"

    if tipo_visao == "Registro Diário":
        diario = df_final.copy()
        diario["Unidades"] = diario["Unidades"].apply(formatar_unidades_para_tabela)
        cols = ["Data", "Funcionário", "Unidades", "Horas_trabalhadas", "Horas_extra"]

        if mostrar_valores:
            cols.append("Custo_Dia")
        st.dataframe(
            diario[cols].style.format({"Custo_Dia": "R$ {:.2f}"})
            if mostrar_valores
            else diario[cols],
            use_container_width=True,
            hide_index=True,
        )

        csv = diario[cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Baixar CSV (Diário)", csv, f"diario_{nome_periodo}.csv", "text/csv"
        )

    else:
        geral = (
            df_final.groupby("Funcionário")
            .agg(
                {
                    "Data": "nunique",
                    "Horas_Reg_Num": "sum",
                    "Horas_Ext_Num": "sum",
                    "Custo_Dia": "sum",
                }
            )
            .reset_index()
        )

        geral.columns = [
            "Funcionário",
            "Dias Trabalhados",
            "H. Regulares",
            "H. Extras",
            "Total (R$)",
        ]
        cols_geral = ["Funcionário", "Dias Trabalhados", "H. Regulares", "H. Extras"]
        if mostrar_valores:
            cols_geral.append("Total (R$)")

        df_geral_final = geral[cols_geral]

        formatos = {"H. Regulares": "{:.1f}h", "H. Extras": "{:.1f}h"}
        if mostrar_valores:
            formatos["Total (R$)"] = "R$ {:.2f}"

        st.dataframe(
            df_geral_final.style.format(formatos),
            use_container_width=True,
            hide_index=True,
        )

        csv = df_geral_final.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Baixar CSV (Geral)", csv, f"fechamento_{nome_periodo}.csv", "text/csv"
        )

