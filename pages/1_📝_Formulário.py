import streamlit as st
from src.utils import obter_dias_do_mes, preparar_registros_para_envio
from src.database import adicionar_dataframe_na_planilha
from datetime import datetime
import calendar
from src.components import configurar_pagina, renderizar_seletor_calendario

configurar_pagina("CleanLog - Lançamento Mensal", "centered")


st.title("📝 Form. Fechamento Mensal")
with st.container(border=True):
    col_nome, col_mes, col_ano = st.columns([2, 1, 1])

    colaborador = col_nome.text_input(
        "Nome do Colaborador", placeholder="Ex: João Silva"
    )
    lista_meses = [calendar.month_name[i].capitalize() for i in range(1, 13)]
    mes_selecionado = col_mes.selectbox(
        "Mês", lista_meses, index=datetime.now().month - 1
    )
    ano_selecionado = col_ano.number_input("Ano", value=datetime.now().year)

    with st.container(border=True):
        renderizar_seletor_calendario([lista_meses, mes_selecionado, ano_selecionado])

    if st.button("Enviar para Planilha", type="primary", use_container_width=True):
        if not colaborador:
            st.error("Informe o nome do colaborador antes de continuar.")
        elif len(colaborador) < 3:
            st.warning("O nome do colaborador deve conter pelo menos 3 caracteres.")
        else:
            data_final_selecionada = st.session_state.get("calendario_nativo")

            if not data_final_selecionada:
                st.error("Por favor, selecione uma data no calendário antes de enviar.")
                st.stop()

            ano_proc = data_final_selecionada.year
            mes_nome_proc = lista_meses[data_final_selecionada.month - 1]
            ultimo_dia_proc = obter_dias_do_mes(ano_proc, mes_nome_proc, lista_meses)

            df_envio = preparar_registros_para_envio(
                colaborador, mes_nome_proc, ano_proc, ultimo_dia_proc, st.session_state
            )

            if df_envio.empty:
                st.warning(
                    "Nenhum turno marcado para o mês selecionado. Verifique os lançamentos."
                )
            else:
                try:
                    adicionar_dataframe_na_planilha(df_envio)
                    st.success(
                        f"Dados de {colaborador} enviados para o Google Sheets com sucesso! ✅"
                    )
                except Exception as erro:
                    st.error(f"Falha ao enviar para o Google Sheets: {erro}")

