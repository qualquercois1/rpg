import streamlit as st

st.set_page_config(
    page_title="Gerador",
    page_icon="🎲",
    layout="centered"
)

st.title('Gerador')

with st.expander('Gerador', expanded=True):
    st.subheader('Formulario')
    st.info('Os campos são opcionais.')

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input('Nome')

        classe = st.selectbox(
            'Classe:',
            ["", "Guerreiro(a)", "Mago(a)", "Ladrão(a)", "Clérigo(a)", "Bárbaro(a)", "Bardo", "Patrulheiro(a)", "Druida", "Outro..."]
        )
        if classe == 'Outro...':
            classe = st.text_input('Digite a Classe desejada')

        raca = st.selectbox(
            'Raça',
            ["", "Humano(a)", "Elfo(a)", "Anão(ã)", "Orc", "Halfling", "Meio-Elfo(a)", "Draconato(a)", "Outro..."]
        )
        if raca == 'Outro...':
            raca = st.text_input('Digite a raça desejada')

    with col2:
        altura = st.number_input("Altura", placeholder="Ex: 1,80m", min_value=0.0)

        fisico = st.selectbox(
            "Fisico",
            ["", "Magro(a)", "Atlético(a)", "Robusto(a)", "Normal"]
        )

    enviar = st.button('Enviar')

if enviar:
    st.success(f"Obrigado! Sua mensagem foi enviada com sucesso.")
