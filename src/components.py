from datetime import date, datetime
import streamlit as st
import plotly.express as px
from src.utils import formatar_horario, obter_dias_do_mes, lista_meses


def configurar_pagina(titulo_pagina: str, layout: str = "wide"):
    """Configura o layout e trava o acesso para usuários não logados."""
    if not st.session_state.get("authentication_status"):
        st.error("🚫 Acesso negado. Faça login na página inicial.")
        st.link_button("Ir para o Login", "/")
        st.stop()
    st.set_page_config(page_title=titulo_pagina, layout=layout)

def exibir_metricas_dashboard(df_filtrado):
    """Renderiza os cartões de métricas principais."""
    st.divider()
    custo_total = (
        df_filtrado["Custo_Dia"].sum() if "Custo_Dia" in df_filtrado.columns else 0.0
    )
    if custo_total > 0:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Horas", f"{df_filtrado['Total_Horas_Dia'].sum():.1f}h ⏳")
        m2.metric("Custo Total", f"R$ {custo_total:.2f} 💰")
        m3.metric("Dias Trabalhados", f"{df_filtrado['Data'].nunique()} 📅")
        return
    m1, m2 = st.columns(2)
    m1.metric("Total de Horas", f"{df_filtrado['Total_Horas_Dia'].sum():.1f}h ⏳")
    m2.metric("Dias Trabalhados", f"{df_filtrado['Data'].nunique()} 📅")


def exibir_graficos_principais(df_filtrado, df_expandido, func_sel):
    """Desenha os gráficos de evolução e pizza."""
    st.write("### 📈 Análise de Operação")
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_evolucao = px.line(
            df_filtrado,
            x="Data",
            y="Total_Horas_Dia",
            color="Funcionário" if func_sel == "Todos" else None,
            title="Evolução de Horas",
            markers=True,
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)
    with col2:
        if not df_expandido.empty:
            df_exp_f = df_expandido[
                df_expandido["Funcionário"].isin(df_filtrado["Funcionário"].unique())
            ]
            periodo = df_exp_f.groupby("Periodo").size().reset_index(name="Qtd")
            fig_pizza = px.pie(
                periodo, values="Qtd", names="Periodo", title="Turnos", hole=0.5
            )
            st.plotly_chart(fig_pizza, use_container_width=True)


def exibir_graficos_secundarios(df_filtrado, df_expandido):
    """Desenha comparativos e turnos por unidade."""
    col1, col2 = st.columns(2)
    with col1:
        comp = (
            df_filtrado.groupby("Funcionário")[["Horas_Reg_Num", "Horas_Ext_Num"]]
            .sum()
            .reset_index()
        )
        fig_bar = px.bar(
            comp,
            x="Funcionário",
            y=["Horas_Reg_Num", "Horas_Ext_Num"],
            title="Regulares vs Extras",
            barmode="group",
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        if not df_expandido.empty:
            df_exp_f = df_expandido[
                df_expandido["Funcionário"].isin(df_filtrado["Funcionário"].unique())
            ]
            un = df_exp_f.groupby("Unidade_Indiv").size().reset_index(name="Qtd")
            fig_un = px.bar(un, x="Unidade_Indiv", y="Qtd", title="Turnos por Unidade")
            st.plotly_chart(fig_un, use_container_width=True)


def renderizar_seletor_calendario(contexto: list):
    _, mes_selecionado_nome, ano_selecionado = contexto
    indice_mes = lista_meses.index(mes_selecionado_nome) + 1
    data_foco_inicial = date(ano_selecionado, indice_mes, 1)
    
    st.markdown("#### 📅 Selecione o dia no calendário:")
    data_selecionada = st.date_input(
        "Data de Lançamento",
        value=data_foco_inicial,
        min_value=date(2020, 1, 1),
        max_value=date(2030, 12, 31),
        key="calendario",
        format="DD/MM/YYYY",
        label_visibility="collapsed",
    )

    if data_selecionada:
        dia_sel = data_selecionada.day
        status_chave = f"status_{dia_sel}"
        status_atual = st.session_state.get(status_chave, "")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info(
                f"Data selecionada: **{data_selecionada.strftime('%d/%m/%Y')}** {status_atual}"
            )
        with c2:
            if st.button(
                "Abrir Lançamento 🚀", use_container_width=True, type="primary"
            ):
                abrir_popup_dia(dia_sel, mes_selecionado_nome)


def renderizar_seletor_data():
    """Renderiza os seletores de data para exportação.
    Retorna: [dia_inicial, dia_final], [mes_inicial, mes_final], ano
    """
    date_today = date.today()

    c1, c2 = st.columns([1, 2])
    mes_inicial = c2.selectbox(
        "Do Mês:", lista_meses, index=date_today.month - 2
    ).lower()
    mes_final = c2.selectbox(
        "Até Mês:", lista_meses, index=date_today.month - 1
    ).lower()

    ultimo_dia_ini = obter_dias_do_mes(
        date_today.year, mes_inicial.lower(), lista_meses
    )
    ultimo_dia_fim = obter_dias_do_mes(
        date_today.year, mes_final.lower(), lista_meses
    )

    dia_inicial = c1.number_input(
        "Do dia:", min_value=1, max_value=ultimo_dia_ini, value=1
    )
    dia_final = c1.number_input(
        "Até dia:", min_value=1, max_value=ultimo_dia_fim, value=date_today.day
    )

    ano = st.number_input(
        "Ano",
        min_value=date_today.year - 5,
        max_value=date_today.year + 5,
        value=date_today.year,
    )

    return [dia_inicial, dia_final], [mes_inicial, mes_final], ano


@st.dialog("Lançamento de Turnos")
def abrir_popup_dia(dia, mes):
    UNIDADES_RU = ["RU-1", "RU-2", "RU-3", "RU-4", "RU-5", "RU-6", "RU-7"]

    def obter_indice_unidade(selecao):
        return UNIDADES_RU.index(selecao) if selecao in UNIDADES_RU else 0

    st.write(f"### 🗓️ {dia} de {mes}")
    chaves_dados = f"dados_dia_{dia}"
    if chaves_dados not in st.session_state:
        st.session_state[chaves_dados] = {}
    dados_atuais = st.session_state[chaves_dados]
    turnos = [("🌅 Manhã", "am"), ("🌇 Tarde", "pm")]
    colunas = st.columns(2)

    for idx, (rotulo, sigla) in enumerate(turnos):
        with colunas[idx]:
            st.markdown(f"#### {rotulo}")
            trabalhou = st.checkbox(
                "Trabalhou",
                key=f"temp_check_{sigla}_{dia}",
                value=dados_atuais.get(f"{sigla}_check", False),
            )
            st.selectbox(
                "Unidade",
                UNIDADES_RU,
                key=f"temp_ru_{sigla}_{dia}",
                disabled=not trabalhou,
                index=obter_indice_unidade(dados_atuais.get(f"{sigla}_ru", "RU-1")),
            )
            st.text_input(
                "Setor",
                placeholder="Ex: Copa",
                key=f"temp_set_{sigla}_{dia}",
                disabled=not trabalhou,
                value=dados_atuais.get(f"{sigla}_set", ""),
            )

    st.divider()
    st.markdown("#### ⏰ Turno realizado")
    st.time_input(
        "Horas trabalhadas",
        value=datetime.strptime(dados_atuais.get("reg_val", "00:00"), "%H:%M").time(),
        key=f"reg_val_{dia}",
    )
    st.markdown("#### 🚀 Turno Extra")
    extra_ativo = st.checkbox(
        "Houve turno extra?",
        key=f"ext_check_{dia}",
        value=dados_atuais.get("ext_check", False),
    )

    col_ext_1, col_ext_2 = st.columns([1, 2])
    col_ext_1.time_input(
        "Horas Extras",
        value=datetime.strptime(dados_atuais.get("ext_val", "00:00"), "%H:%M").time(),
        key=f"ext_val_{dia}",
        disabled=not extra_ativo,
    )
    col_ext_2.text_input(
        "Observação",
        placeholder="Ex: Dobra",
        key=f"ext_obs_{dia}",
        disabled=not extra_ativo,
        value=dados_atuais.get("ext_obs", ""),
    )

    if st.button("Salvar Registro", use_container_width=True):
        registro_manha = formatar_horario(st.session_state[f"reg_val_{dia}"])
        registro_extra = formatar_horario(st.session_state[f"ext_val_{dia}"])
        st.session_state[chaves_dados] = {
            "am_check": st.session_state[f"temp_check_am_{dia}"],
            "am_ru": st.session_state[f"temp_ru_am_{dia}"],
            "am_set": st.session_state[f"temp_set_am_{dia}"],
            "pm_check": st.session_state[f"temp_check_pm_{dia}"],
            "pm_ru": st.session_state[f"temp_ru_pm_{dia}"],
            "pm_set": st.session_state[f"temp_set_pm_{dia}"],
            "ext_check": st.session_state[f"ext_check_{dia}"],
            "reg_val": registro_manha,
            "ext_val": registro_extra,
            "ext_obs": st.session_state[f"ext_obs_{dia}"],
        }
        st.session_state[f"status_{dia}"] = "✅"
        st.rerun()
