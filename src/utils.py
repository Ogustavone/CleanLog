import calendar
import pandas as pd
import re


def formatar_horario(objeto_horario):
    if objeto_horario and hasattr(objeto_horario, "strftime"):
        return objeto_horario.strftime("%H:%M")
    return "00:00"

def converter_horas_para_decimal(valor):
    if valor in {"Não", "N/A", "", None} or not isinstance(valor, str):
        return 0.0

    try:
        if ":" in valor:
            horas, minutos = map(int, valor.split(":"))
            return horas + minutos / 60
        return float(valor)
    except ValueError:
        return 0.0


def formatar_unidades_para_tabela(unidade_bruta):
    if not unidade_bruta or unidade_bruta == "N/A":
        return "N/A"

    partes = str(unidade_bruta).split(", ")
    unidades_formatadas = []

    for parte in partes:
        if ":" not in parte:
            continue

        periodo, unidade, _ = parte.split(":")
        unidades_formatadas.append(f"{periodo.capitalize()}-{unidade}")

    return ", ".join(unidades_formatadas)


def obter_dias_do_mes(ano, nome_mes, lista_meses):
    indice_mes = lista_meses.index(nome_mes) + 1
    _, ultimo_dia = calendar.monthrange(ano, indice_mes)
    return ultimo_dia


def preparar_registros_para_envio(nome_funcionario, mes, ano, ultimo_dia, estado):
    registros = []
    usuario = estado.get("email", "nao_identificado")

    for dia in range(1, ultimo_dia + 1):
        dados_dia = estado.get(f"dados_dia_{dia}", {})
        tem_manha = dados_dia.get("am_check", False)
        tem_tarde = dados_dia.get("pm_check", False)
        tem_extra = dados_dia.get("ext_check", False)

        if not (tem_manha or tem_tarde or tem_extra):
            continue

        unidades = []
        if tem_manha:
            unidade = dados_dia.get("am_ru", "N/A")
            setor = dados_dia.get("am_set", "N/A") or "N/A"
            unidades.append(f"manha:{unidade}:{setor}")

        if tem_tarde:
            unidade = dados_dia.get("pm_ru", "N/A")
            setor = dados_dia.get("pm_set", "N/A") or "N/A"
            unidades.append(f"tarde:{unidade}:{setor}")

        unidades_str = ", ".join(unidades) if unidades else "N/A"
        data_formatada = f"{dia:02d}/{mes}/{ano}"
        id_unico = f"{nome_funcionario}_{data_formatada}".replace(" ", "_").replace("/", "_").lower()

        registros.append({
            "ID": id_unico,
            "Data": data_formatada,
            "Funcionário": nome_funcionario,
            "Unidades": unidades_str,
            "Horas_trabalhadas": dados_dia.get("reg_val", "00:00"),
            "Horas_extra": dados_dia.get("ext_val", "00:00") if tem_extra else "00:00",
            "Observação": dados_dia.get("ext_obs", ""),
            "Enviado_por": usuario,
        })

    return pd.DataFrame(registros)

def obter_dias_do_mes(ano, nome_mes, lista_meses):
    indice_mes = lista_meses.index(nome_mes) + 1
    _, ultimo_dia = calendar.monthrange(ano, indice_mes)
    return ultimo_dia

def formatar_unidades_para_tabela(unidade_bruta):
    if not unidade_bruta or unidade_bruta == "N/A": return "N/A"
    partes = str(unidade_bruta).split(", ")
    unidades_formatadas = []
    for parte in partes:
        if ":" not in parte: continue
        periodo, unidade, _ = parte.split(":")
        unidades_formatadas.append(f"{periodo.capitalize()}-{unidade}")
    return ", ".join(unidades_formatadas)

def processar_dados_dashboard(df, valor_hora):
    df = df.copy()
    df['Horas_Reg_Num'] = df['Horas_trabalhadas'].apply(converter_horas_para_decimal)
    df['Horas_Ext_Num'] = df['Horas_extra'].apply(converter_horas_para_decimal)
    df['Total_Horas_Dia'] = df['Horas_Reg_Num'] + df['Horas_Ext_Num']
    df['Custo_Dia'] = df['Total_Horas_Dia'] * valor_hora
    df['Data_dt'] = pd.to_datetime(df['Data'], format="%d/%m/%Y", errors='coerce')
    return df.sort_values('Data_dt')

def expandir_unidades(dataframe):
    linhas = []
    for _, entrada in dataframe.iterrows():
        unidades = str(entrada['Unidades']).split(", ")
        for unidade in unidades:
            if ":" not in unidade: continue
            partes = unidade.split(":")
            if len(partes) != 3: continue
            linha_expandida = entrada.to_dict()
            linha_expandida['Periodo'] = partes[0].capitalize()
            linha_expandida['Unidade_Indiv'] = partes[1]
            linha_expandida['Setor_Indiv'] = partes[2]
            linhas.append(linha_expandida)
    return pd.DataFrame(linhas)

def formatar_data_para_status(data_obj):
    """Converte um objeto datetime.date em string para chave de status (ex: 'status_2026_03_15')"""
    if not data_obj:
        return ""
    return data_obj.strftime("status_%Y_%m_%d")
    
def validar_email(email):
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(padrao, email))
