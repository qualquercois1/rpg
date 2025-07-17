import streamlit as st

st.set_page_config(
    page_title="Gerador",
    page_icon="🎲",
    layout="centered"
)

themes = [
    {
        'titulo': 'Revolta Arcanopunk',
        'descricao': 'Em uma cidade onde a tecnologia a vapor e a magia rúnica competem, os jogadores são membros da resistência contra um império tecnológico que busca erradicar a magia.'
    },
    {
        'titulo': 'Os Ecos do Cataclismo',
        'descricao': 'Mil anos após uma guerra divina que quebrou o mundo, pequenas comunidades sobrevivem em uma terra com anomalias mágicas e ruínas de uma civilização grandiosa.'
    },
    {
        'titulo': 'Crônicas do Mar de Serpentes',
        'descricao': 'A Era de Ouro da Pirataria, mas os mitos são reais: sereias, krakens e ilhas amaldiçoadas existem e são perigos constantes.'
    },
    {
        'titulo': 'O Limiar do Vazio',
        'descricao': 'Em um futuro distante, a tripulação de uma nave de exploração encontra algo incompreensível que desafia as leis da física e da sanidade.'
    },
    {
        'titulo': 'Sementes do Amanhã',
        'descricao': 'Em um futuro otimista pós-colapso, a humanidade reconstrói o mundo de forma sustentável, focando em cooperação e tecnologia limpa.'
    },
    {
        'titulo': 'Aleatório',
        'descricao': 'Pode ser qualquer coisa'
    }
]

if 'theme_index' not in st.session_state:
    st.session_state.theme_index = 0

st.title('Gerador')

with st.expander('Gerador', expanded=True):
    st.subheader('Formulario')
    st.info('Os campos são opcionais.')

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input('Nome')

        idade = st.number_input('Idade', format='%d', step=1)

        cor_olhos = st.selectbox(
            'Cor dos olhos',
            ['', 'Azul', 'Castanho', 'Verde', 'Preto', 'Branco', 'Cinza', 'Lilás', 'Outro...']
        )

        classe = st.selectbox(
            'Classe:',
            ["", "Guerreiro(a)", "Mago(a)", "Ladrão(a)", "Clérigo(a)", "Bárbaro(a)", "Bardo", "Patrulheiro(a)", "Druida", "Outro..."]
        )
        if classe == 'Outro...':
            classe = st.text_input('Digite a Classe desejada')

        

    with col2:
        altura = st.number_input("Altura", placeholder="Ex: 1,80m", min_value=0.0, step=0.1)

        fisico = st.selectbox(
            "Fisico",
            ["", "Magro(a)", "Atlético(a)", "Robusto(a)", "Normal"]
        )

        raca = st.selectbox(
            'Raça',
            ["", "Humano(a)", "Elfo(a)", "Anão(ã)", "Orc", "Halfling", "Meio-Elfo(a)", "Draconato(a)", "Outro..."]
        )
        if raca == 'Outro...':
            raca = st.text_input('Digite a raça desejada')

        regiao = st.selectbox(
            "Região",
            ["", "As Terras Partidas de Vor'Thal", 
            "O Sussurro Verdejante de Sylanar", 
            "Os Cânions de Ferro e Fogo de Kaz'Dur", 
            "O Arquipélago da Maré de Cristal",
            "As Planícies Desoladas do Crepúsculo Eterno",
            "Outro..."]
        )

        if regiao == 'Outro...':
            regiao = st.text_input('Digite a região desejada')

    st.markdown("<h1 style='text-align: center;'>📜 Explore Temas 📜</h1>", unsafe_allow_html=True)

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
    st.markdown(f"<p style='text-align: center; font-size: 20px;'>{page_indicator}</p>", unsafe_allow_html=True)

    enviar = st.button('Enviar', use_container_width=True)

if enviar:
    tema_selecionado = themes[st.session_state.theme_index]

    dados_finais = {
        "Tema": tema_selecionado['titulo'],
        "Nome": nome,
        "Idade": idade,
        "Cor dos Olhos": cor_olhos,
        "Classe": classe,
        "Altura": altura,
        "Físico": fisico,
        "Raça": raca,
        "Região": regiao,
    }

    st.success("Dados prontos para a geração!")

    with st.spinner("Construindo prompt e chamando a IA..."):
        prompt_para_ia = "Crie um personagem com os seguintes detalhes:\n"
        for key, value in dados_finais.items():
            if value: # Adiciona ao prompt apenas os campos preenchidos
                prompt_para_ia += f"- {key}: {value}\n"
        
        # Apenas para demonstração, vamos exibir o prompt que seria enviado.
        # Aqui você chamaria a sua função: response = generate_content_from_gemini(prompt_para_ia)
        st.code(prompt_para_ia, language='text')
        st.info("O prompt acima seria enviado para a IA para gerar a descrição completa do personagem.")
