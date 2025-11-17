import streamlit as st

st.set_page_config(
    page_title="Gerador de Personagens RPG com IA",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("Bem-vindo ao Gerador de Personagens RPG! 🎲")

st.markdown("""
Esta aplicação foi criada para ajudar Mestres de RPG e Jogadores a quebrar o bloqueio criativo. 
Usando o poder da Inteligência Artificial do **Google Gemini**, este gerador cria fichas de personagens
completas, incluindo histórias de fundo, personalidades e detalhes temáticos.
""")


st.image("imgs/rpg-de-mesa.webp", 
         caption="Sua próxima aventura começa aqui.",
         width='stretch')

st.header("Como Funciona?")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Insira sua Chave 🔑")
    st.markdown("""
    Para que a IA funcione, você precisa de uma chave de API do Google Gemini.
    - Vá ao [Google AI Studio](https://aistudio.google.com/app/apikey).
    - Crie uma nova chave.
    - Copie e cole na **barra lateral à esquerda**.
    *(Sua chave não é salva e fica apenas no seu navegador durante a sessão)*
    """)

with col2:
    st.subheader("2. Gere seu Personagem 📜")
    st.markdown("""
    - Navegue até a página **'Gerador'** na barra lateral.
    - Escolha um tema de cenário (como Arcanopunk ou Fantasia).
    - Preencha os campos que desejar.
    - **Deixe em branco qualquer campo que você queira que a IA invente!**
    - Clique em 'Gerar Personagem' e veja a mágica acontecer.
    """)

st.info("Pronto para começar? Navegue até a página **'Gerador'** na barra lateral! 👈")