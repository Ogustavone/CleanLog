# CleanLog

Sistema de formulário e dashboard analítico desenvolvido para gestão de lançamentos mensais, utilizando Google Sheets como base de dados e Streamlit para a interface.

---

## 🚀 Funcionalidades

* **Lançamento Mensal:** Formulário intuitivo para entrada de dados operacionais.
* **Dashboard Analítico:** Visualização de indicadores (KPIs) com gráficos interativos.
* **Persistência:** Integração direta com Google Sheets API.
* **Deploy:** Configurado para rodar via Streamlit Cloud.

## 🛠️ Tecnologias

* **Linguagem:** Python
* **Interface/Dashboard:** Streamlit
* **Manipulação de Dados:** Pandas / Plotly
* **Banco de Dados:** Google Sheets API

## 📁 Estrutura do Projeto

```text
├── pages/
│   ├── 1_📝_Formulário.py  # Formulário de envio (lançamento mensal)
│   └── 2_📊_Dashboard.py   # Gráficos e dados indicadores.
├── src/
│   ├── database.py    # Integração com Google sheets
│   ├── utils.py       # Funções auxiliares e tratamentos
│   └── components.py  # Componentes da interface
├── Início.py
└── requirements.txt
