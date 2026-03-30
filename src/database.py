import streamlit as st
from google.oauth2.service_account import Credentials
from gspread import authorize
import pandas as pd


def _obter_cliente_gsheets():
    configuracao = st.secrets["connections"]["gsheets"]
    credenciais = {k: v for k, v in configuracao.items() if k != "spreadsheet"}
    escopos = ["https://www.googleapis.com/auth/spreadsheets"]
    credenciais_servico = Credentials.from_service_account_info(credenciais, scopes=escopos)
    return authorize(credenciais_servico)


def adicionar_dataframe_na_planilha(df):
    if df.empty:
        return

    cliente = _obter_cliente_gsheets()
    url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]
    planilha = cliente.open_by_url(url_planilha)
    aba = planilha.get_worksheet(0)

    valores = aba.get_all_values()

    if not valores:
        aba.append_row(list(df.columns), value_input_option="USER_ENTERED")
    else:
        ids_novos = set(df["ID"].tolist())
        linhas_para_deletar = []

        for indice, linha in enumerate(valores):
            if linha and linha[0] in ids_novos:
                linhas_para_deletar.append(indice + 1)

        for indice in sorted(linhas_para_deletar, reverse=True):
            aba.delete_rows(indice)

    aba.append_rows(df.values.tolist(), value_input_option="USER_ENTERED")


def obter_todos_dados_como_df():
    try:
        cliente = _obter_cliente_gsheets()
        url_planilha = st.secrets["connections"]["gsheets"].get("spreadsheet")
        planilha = cliente.open_by_url(url_planilha)
        aba = planilha.get_worksheet(0)

        registros = aba.get_all_records()
        return pd.DataFrame(registros)
    except Exception as erro:
        st.error(f"Erro ao carregar dados: {erro}")
        return pd.DataFrame()
