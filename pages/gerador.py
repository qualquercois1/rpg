import streamlit as st
import google.generativeai as genai
import json
import time

st.set_page_config(
    page_title="Gerador de Personagem RPG",
    page_icon="🎲",
    layout="centered"
)

if 'theme_index' not in st.session_state:
    st.session_state.theme_index = 0
if 'page' not in st.session_state:
    st.session_state.page = 'formulario' 
if 'character_report' not in st.session_state:
    st.session_state.character_report = "" 

themes = [
    {'titulo': 'Revolta Arcanopunk', 'descricao': 'Em uma cidade onde a tecnologia a vapor e a magia rúnica competem, os jogadores são membros da resistência contra um império tecnológico que busca erradicar a magia.'},
    {'titulo': 'Os Ecos do Cataclismo', 'descricao': 'Mil anos após uma guerra divina que quebrou o mundo, pequenas comunidades sobrevivem em uma terra com anomalias mágicas e ruínas de uma civilização grandiosa.'},
    {'titulo': 'Crônicas do Mar de Serpentes', 'descricao': 'A Era de Ouro da Pirataria, mas os mitos são reais: sereias, krakens e ilhas amaldiçoadas existem e são perigos constantes.'},
    {'titulo': 'O Limiar do Vazio', 'descricao': 'Em um futuro distante, a tripulação de uma nave de exploração encontra algo incompreensível que desafia as leis da física e da sanidade.'},
    {'titulo': 'Sementes do Amanhã', 'descricao': 'Em um futuro otimista pós-colapso, a humanidade reconstrói o mundo de forma sustentável, focando em cooperação e tecnologia limpa.'},
    {'titulo': 'Aleatório', 'descricao': 'Pode ser qualquer coisa'}
]


def gerar_relatorio_gemini(api_key, dados):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    Você é um mestre de RPG experiente e criativo.
    Sua tarefa é gerar um personagem completo baseado nos dados parciais fornecidos abaixo.

    REGRAS IMPORTANTES:
    1. O tema do jogo é: "{dados['Tema']}". Tudo deve se encaixar neste cenário.
    2. Analise os dados fornecidos no JSON abaixo.
    3. SE um campo estiver vazio (""), 0, ou nulo, VOCÊ DEVE INVENTAR um valor que faça sentido com o Tema e com o resto do personagem.
    4. SE um campo já estiver preenchido pelo usuário, você DEVE respeitá-lo e mantê-lo.
    5. Gere um relatório final rico em detalhes, usando formatação Markdown para ficar bonito (negrito, itálico, listas, títulos).
    6. O relatório deve incluir: Nome, Detalhes Físicos, Background/História (como ele se encaixa no tema), Personalidade e um pequeno Inventário inicial sugerido.

    DADOS DO USUÁRIO (JSON):
    {json.dumps(dados, ensure_ascii=False)}

    Gere agora o relatório do personagem:
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar personagem: {e}"

if st.session_state.page == 'formulario':
    st.title('Gerador de Personagem 🎲')


    with st.sidebar:
        st.header("Configurações")
        api_key = st.text_input("Insira sua Gemini API Key", type="password")
        st.markdown("[Obtenha sua chave aqui](https://aistudio.google.com/app/apikey)")
        st.warning("Necessário para gerar o personagem.")

    with st.expander('Gerador', expanded=True):
        st.subheader('Características Principais')
        st.info('Deixe em branco ou 0 para que a IA decida por você!')

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input('Nome')
            idade = st.number_input('Idade', format='%d', step=1, min_value=0)
            cor_olhos = st.selectbox('Cor dos olhos', ['', 'Azul', 'Castanho', 'Verde', 'Preto', 'Branco', 'Cinza', 'Lilás', 'Outro...'])
            if cor_olhos == 'Outro...': cor_olhos = st.text_input('Digite a cor dos olhos')

            classe = st.selectbox('Classe:', ["", "Guerreiro(a)", "Mago(a)", "Ladrão(a)", "Clérigo(a)", "Bárbaro(a)", "Bardo", "Patrulheiro(a)", "Druida", "Outro..."])
            if classe == 'Outro...': classe = st.text_input('Digite a Classe desejada')

        with col2:
            altura = st.number_input("Altura (metros)", placeholder="Ex: 1.80", min_value=0.0, step=0.01, format="%.2f")
            fisico = st.selectbox("Físico", ["", "Magro(a)", "Atlético(a)", "Robusto(a)", "Normal", "Outro..."])
            if fisico == 'Outro...': fisico = st.text_input('Digite o tipo físico')

            raca = st.selectbox('Raça', ["", "Humano(a)", "Elfo(a)", "Anão(ã)", "Orc", "Halfling", "Meio-Elfo(a)", "Draconato(a)", "Outro..."])
            if raca == 'Outro...': raca = st.text_input('Digite a raça desejada')

            regiao = st.selectbox("Região de Origem", ["", "As Terras Partidas de Vor'Thal", "O Sussurro Verdejante de Sylanar", "Os Cânions de Ferro e Fogo de Kaz'Dur", "O Arquipélago da Maré de Cristal", "As Planícies Desoladas do Crepúsculo Eterno", "Outro..."])
            if regiao == 'Outro...': regiao = st.text_input('Digite a região desejada')

        st.markdown("<h1 style='text-align: center;'>📜 Escolha o Tema 📜</h1>", unsafe_allow_html=True)

        new_col1, new_col2, new_col3 = st.columns([1,5,1])
        with new_col1:
            if st.button("⬅️ Anterior", use_container_width=True):
                st.session_state.theme_index = (st.session_state.theme_index - 1) % len(themes)
        with new_col3:
            if st.button("Próximo ➡️", use_container_width=True):
                st.session_state.theme_index = (st.session_state.theme_index + 1) % len(themes)
        with new_col2:
            current_theme = themes[st.session_state.theme_index]
            st.subheader(f"_{current_theme['titulo']}_")
            st.markdown(f"**Descrição:** {current_theme['descricao']}")

        st.markdown("---")
        page_indicator = " ".join(["●" if i == st.session_state.theme_index else "○" for i in range(len(themes))])
        st.markdown(f"<p style='text-align: center; font-size: 20px; color: grey;'>{page_indicator}</p>", unsafe_allow_html=True)

        if st.button('🔮 Gerar Personagem 🔮', use_container_width=True, type="primary"):
            if not api_key:
                st.error("Por favor, insira sua chave de API do Gemini na barra lateral.")
            else:
                dados_finais = {
                    "Tema": themes[st.session_state.theme_index]['titulo'],
                    "Descricao_Tema": themes[st.session_state.theme_index]['descricao'],
                    "Nome": nome,
                    "Idade": idade if idade > 0 else "", 
                    "Cor dos Olhos": cor_olhos,
                    "Classe": classe,
                    "Altura": f"{altura:.2f}m" if altura > 0 else "",
                    "Fisico": fisico,
                    "Raca": raca,
                    "Regiao": regiao,
                }

                with st.spinner('Consultando os oráculos digitais...'):
                    relatorio = gerar_relatorio_gemini(api_key, dados_finais)
                    st.session_state.character_report = relatorio
                    st.session_state.page = 'relatorio' 
                    st.rerun() 

elif st.session_state.page == 'relatorio':
    st.title("Ficha de Personagem")

    if st.button("⬅️ Criar Novo Personagem"):
        st.session_state.page = 'formulario'
        st.rerun()

    st.divider()

    with st.container():
        st.markdown(st.session_state.character_report)

    st.divider()
    st.download_button(
        label="💾 Baixar Ficha (TXT)",
        data=st.session_state.character_report,
        file_name="ficha_personagem.md",
        mime="text/markdown"
    )