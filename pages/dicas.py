import streamlit as st

st.set_page_config(page_title="Sobre", page_icon="📜")
st.title("📜 Sobre este Projeto")

st.markdown("""
Este aplicativo é um projeto de código aberto que combina a interface 
do **Streamlit** com o poder de geração de linguagem do **Google Gemini**.
""")

st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.svg", width=300)
st.image("https://images.seeklogo.com/logo-png/51/1/google-gemini-logo-png_seeklogo-515013.png", width=100)


st.divider()

st.header("💡 Dicas para Melhores Resultados")
st.markdown("""
- **Seja Específico (Se Quiser):** Se você quer um "Anão Clérigo de uma montanha de gelo", 
  coloque "Montanha de Gelo" no campo 'Região'. A IA vai usar isso.
- **Seja Vago (Se Quiser):** A mágica acontece quando você deixa campos em branco. Deixar 
  'Nome', 'Classe' e 'Região' vazios, mas escolher o tema "Crônicas do Mar de Serpentes", 
  vai gerar um pirata ou nativo de ilha completo e inesperado!
- **O Tema é Rei:** O tema que você seleciona (Arcanopunk, Pirataria, etc.) é a 
  instrução mais importante que a IA recebe. Todos os campos vazios serão preenchidos 
  de acordo com esse tema.
""")

st.divider()
st.header("Créditos")
st.markdown("""
- **Criado por:** qualquercois1
- **Código-fonte:** https://github.com/qualquercois1
""")