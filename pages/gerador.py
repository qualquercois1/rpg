import streamlit as st

st.set_page_config(
    page_title="Gerador",
    page_icon="🎲",
    layout="centered"
)

st.title('Gerador')

with st.form('Gerador'):
    st.subheader('Formulario')
    st.info('Os campos são opcionais.')

    col1, col2 = st.columns(2)
    with col1:
        classe = st.selectbox(
            'Escolha uma classe:',
            ['Opção 1', 'Opção 2', 'Opção 3']
        )
    with col2:
        email = st.text_input('E-mail')

    enviar = st.form_submit_button('Enviar')

if enviar:
    st.success(f"Obrigado! Sua mensagem foi enviada com sucesso.")
