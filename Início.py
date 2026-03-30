import streamlit as st
import streamlit_authenticator as stauth

config = st.secrets.auth.to_dict()
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

authenticator.login(location="main")

status = st.session_state.get("authentication_status")
email = st.session_state.get("email")

if status:
    st.title(f"Bem-vindo ao CleanLog 👋")
    st.write(f"Conectado em: `{email}`")
    st.info("Utilize o menu lateral para navegar.")
    c1, c2 = st.columns([0.1, 0.4])
    with c1:
        authenticator.logout("Sair do Sistema", "main")
    c2.link_button(
        "Acessar Planilha",
        "https://docs.google.com/spreadsheets/d/1o3VlOSfeH4X49O3t4gLWro-LmlUueO9rd8kK3AzmrEc/edit?usp=sharing",
    )

elif status is False:
    st.error("Usuário/Senha incorretos.")
else:
    st.warning("Por favor, identifique-se para acessar o sistema.")

