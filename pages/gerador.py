import streamlit as st
import google.generativeai as genai
import json
import time
import re 
import streamlit.components.v1 as components 
import os
import base64
from fpdf import FPDF 

if 'theme_index' not in st.session_state:
    st.session_state.theme_index = 0
if 'page' not in st.session_state:
    st.session_state.page = 'formulario' 
if 'character_data' not in st.session_state:
    st.session_state.character_data = None 

themes = [
    {'titulo': 'Revolta Arcanopunk', 'descricao': 'Em uma cidade onde a tecnologia a vapor e a magia rúnica competem, os jogadores são membros da resistência contra um império tecnológico que busca erradicar a magia.'},
    {'titulo': 'Os Ecos do Cataclismo', 'descricao': 'Mil anos após uma guerra divina que quebrou o mundo, pequenas comunidades sobrevivem em uma terra com anomalias mágicas e ruínas de uma civilização grandiosa.'},
    {'titulo': 'Crônicas do Mar de Serpentes', 'descricao': 'A Era de Ouro da Pirataria, mas os mitos são reais: sereias, krakens e ilhas amaldiçoadas existem e são perigos constantes.'},
    {'titulo': 'O Limiar do Vazio', 'descricao': 'Em um futuro distante, a tripulação de uma nave de exploração encontra algo incompreensível que desafia as leis da física e da sanidade.'},
    {'titulo': 'Sementes do Amanhã', 'descricao': 'Em um futuro otimista pós-colapso, a humanidade reconstrói o mundo de forma sustentável, focando em cooperação e tecnologia limpa.'},
    {'titulo': 'Aleatório', 'descricao': 'Pode ser qualquer coisa'}
]

def get_image_base64(path):
    """Lê uma imagem local e converte para base64 para embutir no HTML."""
    try:
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Erro ao carregar imagem: {e}")
        return ""

def create_pdf(data):
    """Gera um arquivo PDF com os dados do personagem."""
    pdf = FPDF()
    pdf.add_page()
    
    # Configuração de Fonte (Arial/Helvetica padrão)
    pdf.set_font("Helvetica", size=12)

    # Título (Nome)
    pdf.set_font("Helvetica", style="B", size=20)
    title = data.get('nome', 'Desconhecido')
    pdf.cell(0, 10, txt=title.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    
    # Subtítulo (Raça | Classe)
    pdf.set_font("Helvetica", style="I", size=12)
    subtitle = f"{data.get('raca')} | {data.get('classe')}"
    pdf.cell(0, 10, txt=subtitle.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    pdf.ln(5)

    # Imagem (Se existir)
    img_path = "imgs/userIcon.png"
    if os.path.exists(img_path):
        # Centraliza a imagem (A4 width ~210mm. Imagem 40mm. X = (210-40)/2 = 85)
        pdf.image(img_path, x=85, w=40)
        pdf.ln(5)

    # Seções de Texto
    sections = [
        ("Detalhes Físicos", data.get('detalhes_fisicos')),
        ("História", data.get('historia')),
        ("Personalidade", data.get('personalidade'))
    ]

    for title, content in sections:
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(0, 10, txt=title.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, txt=str(content).encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    # Inventário
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Inventário", ln=True)
    pdf.set_font("Helvetica", size=11)
    for item in data.get('inventario', []):
        text = f"- {item}"
        pdf.cell(0, 6, txt=text.encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.ln(5)

    # Atributos
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Atributos", ln=True)
    pdf.set_font("Helvetica", size=11)
    
    attrs = data.get('atributos', {})
    # Formata em duas colunas simples
    col_width = pdf.w / 2.5
    row_height = 6
    
    attr_list = list(attrs.items())
    for i in range(0, len(attr_list), 2):
        # Coluna 1
        key1, val1 = attr_list[i]
        text1 = f"{key1.capitalize()}: {val1}"
        pdf.cell(col_width, row_height, txt=text1.encode('latin-1', 'replace').decode('latin-1'), border=1)
        
        # Coluna 2 (se existir)
        if i + 1 < len(attr_list):
            key2, val2 = attr_list[i+1]
            text2 = f"{key2.capitalize()}: {val2}"
            pdf.cell(col_width, row_height, txt=text2.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=True)
        else:
            pdf.ln(row_height)

    return pdf.output(dest='S').encode('latin-1')

def gerar_personagem_json(api_key, dados):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro') 

    prompt = f"""
    Você é um mestre de RPG experiente e criativo.
    Sua tarefa é gerar um personagem completo baseado nos dados parciais fornecidos e retornar APENAS um JSON válido.

    DADOS DE ENTRADA:
    {json.dumps(dados, ensure_ascii=False)}

    REGRAS DE NEGÓCIO:
    1. O tema é: "{dados['Tema']}". Tudo deve se encaixar neste cenário.
    2. Invente valores criativos para campos vazios/zero. Respeite campos preenchidos.
    3. ATRIBUTOS: 
       - São 6: forca, agilidade, vitalidade, inteligencia, sobrevivencia, magia.
       - A soma TOTAL dos 6 atributos deve ser EXATAMENTE 30.
       - O máximo de um único atributo é 10.
       - Se vierem zerados, distribua os 30 pontos aleatoriamente. Se vierem parciais, complete para somar 30.

    FORMATO DE SAÍDA (JSON OBRIGATÓRIO):
    Responda APENAS com um JSON cru (sem markdown ```json) seguindo exatamente esta estrutura:
    {{
        "nome": "String",
        "classe": "String",
        "raca": "String",
        "detalhes_fisicos": "String (descrição visual)",
        "historia": "String (background detalhado)",
        "personalidade": "String",
        "inventario": ["Item 1", "Item 2", "Item 3"],
        "atributos": {{
            "forca": Int,
            "agilidade": Int,
            "vitalidade": Int,
            "inteligencia": Int,
            "sobrevivencia": Int,
            "magia": Int
        }}
    }}
    """

    try:
        response = model.generate_content(prompt)
        
        if hasattr(response, 'usage_metadata'):
            print(f"\n[TOKENS] Prompt: {response.usage_metadata.prompt_token_count} | Resposta: {response.usage_metadata.candidates_token_count}")
        
        texto_limpo = response.text.strip()
        if texto_limpo.startswith("```json"):
            texto_limpo = texto_limpo[7:]
        if texto_limpo.endswith("```"):
            texto_limpo = texto_limpo[:-3]
            
        return json.loads(texto_limpo) 
    
    except Exception as e:
        print(f"\n[ERRO] {e}\n")
        return None

def formatar_relatorio_markdown(data):
    """Converte o JSON do personagem em um texto Markdown para o arquivo de download."""
    if not data: return ""
    
    attrs = data.get('atributos', {})
    
    md = f"""# 📜 Ficha de Personagem: {data.get('nome', 'Desconhecido')}

**Raça:** {data.get('raca')} | **Classe:** {data.get('classe')}

---
### 👤 Detalhes Físicos
{data.get('detalhes_fisicos')}

### 📖 História
{data.get('historia')}

### 🧠 Personalidade
{data.get('personalidade')}

### 🎒 Inventário Inicial
"""
    for item in data.get('inventario', []):
        md += f"* {item}\n"

    md += f"""
---
### 📊 Atributos
* **Força:** {attrs.get('forca', 0)}
* **Agilidade:** {attrs.get('agilidade', 0)}
* **Vitalidade:** {attrs.get('vitalidade', 0)}
* **Inteligência:** {attrs.get('inteligencia', 0)}
* **Sobrevivência:** {attrs.get('sobrevivencia', 0)}
* **Magia:** {attrs.get('magia', 0)}
"""
        
    return md

# ===================================================================
#                           FORMULARIO
# ===================================================================

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

        # ATRIBUTOS
        st.divider()
        st.subheader("Atributos (Total 30 Pontos)")
        st.info("Distribua 30 pontos. Cada atributo pode ter no máximo 10. Deixe em 0 para a IA gerar.")

        attr_col1, attr_col2, attr_col3 = st.columns(3)
        with attr_col1:
            forca = st.number_input("Força", min_value=0, max_value=10, step=1, format="%d")
            agilidade = st.number_input("Agilidade", min_value=0, max_value=10, step=1, format="%d")
        with attr_col2:
            vitalidade = st.number_input("Vitalidade", min_value=0, max_value=10, step=1, format="%d")
            inteligencia = st.number_input("Inteligência", min_value=0, max_value=10, step=1, format="%d")
        with attr_col3:
            sobrevivencia = st.number_input("Sobrevivência", min_value=0, max_value=10, step=1, format="%d")
            magia = st.number_input("Magia", min_value=0, max_value=10, step=1, format="%d")
        
        st.markdown("<h1 style='text-align: center;'>📜 Escolha o Tema 📜</h1>", unsafe_allow_html=True)

        # NAVEGADOR DE TEMAS
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
            
            total_pontos = forca + agilidade + vitalidade + inteligencia + sobrevivencia + magia
            if total_pontos > 30:
                st.error(f"Erro: Você distribuiu {total_pontos} pontos. O máximo permitido é 30.")
            elif not api_key:
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
                    "Forca": forca if forca > 0 else "",
                    "Agilidade": agilidade if agilidade > 0 else "",
                    "Vitalidade": vitalidade if vitalidade > 0 else "",
                    "Inteligencia": inteligencia if inteligencia > 0 else "",
                    "Sobrevivencia": sobrevivencia if sobrevivencia > 0 else "",
                    "Magia": magia if magia > 0 else "",
                    "TotalPontosUsuario": total_pontos if total_pontos > 0 else ""
                }

                with st.spinner('Consultando os oráculos digitais...'):
                    personagem_json = gerar_personagem_json(api_key, dados_finais)
                    
                    if personagem_json:
                        st.session_state.character_data = personagem_json
                        st.session_state.page = 'relatorio' 
                        st.rerun()
                    else:
                        st.error("Erro ao gerar o personagem. Tente novamente.")

# ===================================================================
#                           RELATORIO
# ===================================================================
elif st.session_state.page == 'relatorio':

    def build_full_report_html(data):
        """Gera um HTML ÚNICO contendo todo o relatório visual + gráfico."""
        
        attrs = data.get('atributos', {})
        f = attrs.get('forca', 5)
        a = attrs.get('agilidade', 5)
        i = attrs.get('inteligencia', 5)
        v = attrs.get('vitalidade', 5)
        s = attrs.get('sobrevivencia', 5)
        m = attrs.get('magia', 5)

        # Prepara o inventário como lista HTML
        inventario_lis = "".join([f"<li>🎒 {item}</li>" for item in data.get('inventario', [])])
        
        # Carrega a imagem e converte para base64
        # Caminho da imagem conforme solicitado: imgs/userIcon.png
        img_src = get_image_base64("imgs/userIcon.png")
        img_tag = f'<img src="{img_src}" class="char-img" />' if img_src else '<div style="text-align:center; color: #555;">(Imagem não encontrada)</div>'

        html_string = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ficha de Personagem</title>
            <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap)" rel="stylesheet">
            <style>
                body {{
                    margin: 0; 
                    padding: 10px; /* Reduzi o padding do body */
                    background-color: transparent; 
                    font-family: 'Inter', sans-serif;
                    color: #fff;
                }}
                .char-card {{
                    background-color: #1a1c24;
                    border: 1px solid #2b2d35;
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
                    /* MUDANÇA AQUI: de 800px para 100% para ocupar toda a largura disponível */
                    max-width: 100%; 
                    margin: 0 auto;
                }}
                .char-header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 1px solid #333;
                    padding-bottom: 20px;
                }}
                .char-title {{
                    margin: 0;
                    font-size: 2.5em;
                    color: #fff;
                }}
                .char-subtitle {{
                    margin: 5px 0 20px 0;
                    color: #bbb;
                    font-size: 1.2em;
                    font-style: italic;
                }}
                .char-img {{
                    width: 150px;
                    height: 150px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 3px solid #bbff00;
                    margin-bottom: 10px;
                }}
                .char-section-title {{
                    margin-top: 30px;
                    margin-bottom: 15px;
                    color: #bbff00;
                    font-size: 1.4em;
                    font-weight: bold;
                    border-bottom: 1px solid #444;
                    padding-bottom: 5px;
                }}
                .char-text {{
                    color: #ddd;
                    line-height: 1.6;
                    text-align: justify;
                    margin-bottom: 20px;
                }}
                .char-list {{
                    list-style-type: none;
                    padding: 0;
                    color: #ddd;
                }}
                .char-list li {{
                    padding: 8px 0;
                    border-bottom: 1px solid #333;
                }}
                /* MUDANÇA AQUI: Grid responsivo com auto-fit */
                .attr-grid {{
                    display: grid;
                    /* Cria colunas de no mínimo 140px, preenchendo o espaço */
                    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                    gap: 15px;
                    text-align: center;
                    margin-bottom: 40px;
                }}
                .attr-box {{
                    background-color: #2b2d35;
                    padding: 15px;
                    border-radius: 10px;
                    border: 1px solid #444;
                }}
                .attr-val {{
                    font-size: 1.8em;
                    font-weight: bold;
                    color: #fff;
                }}
                .attr-label {{
                    font-size: 0.8em;
                    color: #aaa;
                    margin-top: 5px;
                }}
                canvas {{
                    display: block;
                    margin: 0 auto;
                    width: 100%;
                    max-width: 600px; /* Mantém o gráfico sob controle */
                }}
            </style>
        </head>
        <body>
        
        <div class="char-card">
            <!-- CABEÇALHO (Dentro do Card) -->
            <div class="char-header">
                {img_tag}
                <h1 class="char-title">{data.get('nome', 'Sem Nome')}</h1>
                <p class="char-subtitle">{data.get('raca')} | {data.get('classe')}</p>
            </div>

            <!-- CONTEÚDO (Dentro do Card) -->
            <div class="char-section-title">👤 Detalhes Físicos</div>
            <div class="char-text">{data.get('detalhes_fisicos')}</div>

            <div class="char-section-title">📖 História</div>
            <div class="char-text">{data.get('historia')}</div>

            <div class="char-section-title">🧠 Personalidade</div>
            <div class="char-text">{data.get('personalidade')}</div>

            <div class="char-section-title">🎒 Inventário</div>
            <ul class="char-list">
                {inventario_lis}
            </ul>

            <div class="char-section-title">📊 Atributos</div>
            <div class="attr-grid">
                <div class="attr-box"><div class="attr-val">{attrs.get('forca', 0)}</div><div class="attr-label">FORÇA</div></div>
                <div class="attr-box"><div class="attr-val">{attrs.get('agilidade', 0)}</div><div class="attr-label">AGILIDADE</div></div>
                <div class="attr-box"><div class="attr-val">{attrs.get('vitalidade', 0)}</div><div class="attr-label">VITALIDADE</div></div>
                <div class="attr-box"><div class="attr-val">{attrs.get('inteligencia', 0)}</div><div class="attr-label">INTELIGÊNCIA</div></div>
                <div class="attr-box"><div class="attr-val">{attrs.get('sobrevivencia', 0)}</div><div class="attr-label">SOBREVIVÊNCIA</div></div>
                <div class="attr-box"><div class="attr-val">{attrs.get('magia', 0)}</div><div class="attr-label">MAGIA</div></div>
            </div>

            <!-- GRÁFICO (Dentro do Card) -->
            <div style="text-align: center; margin-bottom: 20px;">
                <canvas id="canvas"></canvas>
            </div>
        </div>

        <script>
            var canvas = document.getElementById('canvas');
            // Ajusta o tamanho interno do canvas para alta resolução
            canvas.width = 600;
            canvas.height = 600; 

            var container = canvas.getContext("2d");
            var screen_width = canvas.width;
            var screen_height = canvas.height;
            var radius = 80;
            var point = {{ tamanho : 20 }};

            function verticeAccountX (position, angle, radius) {{
                var radian = angle * (Math.PI / 180);
                return position + (radius * (Math.cos(radian)));
            }}

            function verticeAccountY (position, angle, radius) {{
                var radian = angle * (Math.PI / 180);
                return position + (radius * (Math.sin(radian)));
            }}

            function drawLine(v1x, v1y, v2x, v2y, color) {{
                container.strokeStyle = color;
                container.lineWidth = 2;
                container.beginPath();
                container.moveTo(v1x, v1y);
                container.lineTo(v2x, v2y);
                container.stroke();
            }}

            function makeHexagon(centerX, centerY, radius, color) {{
                var vertice_x = verticeAccountX(centerX, 0, radius);
                var vertice_y = verticeAccountY(centerY, 0, radius);
                var vertices = [{{x:vertice_x, y:vertice_y}}];
                for(var i=1; i<=6; i++) {{
                    var antigo_vertice_x = vertice_x;
                    var antigo_vertice_y = vertice_y;
                    vertice_x = verticeAccountX(centerX, i*60, radius);
                    vertice_y = verticeAccountY(centerY, i*60, radius);
                    drawLine(antigo_vertice_x, antigo_vertice_y, vertice_x, vertice_y, color);
                    var newVertice = {{ x: vertice_x, y: vertice_y }};
                    vertices.push(newVertice);
                }}
                return vertices;
            }}

            function lerp(start, end, value) {{
                var t = value/10.0;
                if (t < 0) t = 0;
                if (t > 1) t = 1; 
                return start + (end - start) * t;
            }}

            function meter(forca, agilidade, inteligencia, vitalidade, sobrevivencia, magia) {{
                var vertices_internal = null;
                var vertices_external = null;
                var attributes = [forca, agilidade, inteligencia, vitalidade, sobrevivencia, magia];
                var attributeNames = ["FOR", "AGI", "INT", "VIT", "SOB", "MAG"];

                for(var j=1; j<=3; j++) {{
                    var tempVertices = makeHexagon(screen_width/2, screen_height/2, radius*j, "#ff7300c9");
                    if(j == 1) {{ vertices_internal = tempVertices; }} 
                    else if (j == 3) {{ vertices_external = tempVertices; }}
                }}

                for(var j=0; j<6; j++) {{
                    var initial_point_x = vertices_internal[j].x;
                    var initial_point_y = vertices_internal[j].y;
                    var end_point_x = vertices_external[j].x;
                    var end_point_y = vertices_external[j].y;
                    var textX = end_point_x;
                    var textY = end_point_y;
                    var nameLabel = attributeNames[j]; 
                    var valueLabel = attributes[j];

                    container.fillStyle = "#ffffffff"; 
                    container.font = "20px Inter, sans-serif";
                    if (j === 0 || j === 1 || j === 5) {{
                        container.textAlign = "left";
                        textX += 20; 
                    }} else {{
                        container.textAlign = "right";
                        textX -= 20;
                    }}
                    var gap = 4;
                    var y_name = textY - (gap / 2); 
                    var y_value = textY + (gap / 2);
                    container.textBaseline = "bottom"; 
                    container.fillText(nameLabel, textX, y_name);
                    container.textBaseline = "top"; 
                    container.fillText(valueLabel, textX, y_value);
                }}

                var attributeVertices = [];
                for (var j = 0; j < 6; j++) {{
                    var startX = vertices_internal[j].x;
                    var startY = vertices_internal[j].y;
                    var endX = vertices_external[j].x;
                    var endY = vertices_external[j].y;
                    var attrValue = attributes[j];
                    var pointX = lerp(startX, endX, attrValue);
                    var pointY = lerp(startY, endY, attrValue);
                    attributeVertices.push({{ x: pointX, y: pointY }});
                }}

                container.beginPath();
                container.moveTo(attributeVertices[0].x, attributeVertices[0].y);
                for (var j = 1; j < 6; j++) {{
                    container.lineTo(attributeVertices[j].x, attributeVertices[j].y);
                }}
                container.lineTo(attributeVertices[0].x, attributeVertices[0].y); 
                container.strokeStyle = "#bbff00ff";
                container.lineWidth = 3;
                container.stroke();
                container.fillStyle = "rgba(200, 255, 0, 0.58)";
                container.fill();
            }}

            // INJEÇÃO DE DADOS
            meter({f}, {a}, {i}, {v}, {s}, {m});
            
        </script>
        </body>
        </html>
        """
        return html_string

    if st.button("⬅️ Criar Novo Personagem"):
        st.session_state.page = 'formulario'
        st.rerun()

    data = st.session_state.character_data
    
    if data:
        try:
            full_report_html = build_full_report_html(data)
            
            # Exibe o relatório completo (Texto + Imagem + Gráfico) em um único componente
            # Height ajustada para permitir rolagem confortável
            components.html(full_report_html, height=3000) 
            
        except Exception as e:
            st.error(f"Erro ao gerar a visualização: {e}")

        st.divider()
        relatorio_markdown = formatar_relatorio_markdown(data)
        
        # Colunas para botões lado a lado
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            st.download_button(
                label="💾 Baixar Ficha (TXT)",
                data=relatorio_markdown,
                file_name=f"ficha_{data.get('nome', 'personagem').replace(' ', '_').lower()}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        with btn_col2:
            try:
                # Gera o PDF
                pdf_data = create_pdf(data)
                st.download_button(
                    label="📄 Baixar Ficha (PDF)",
                    data=pdf_data,
                    file_name=f"ficha_{data.get('nome', 'personagem').replace(' ', '_').lower()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
                
    else:
        st.error("Nenhum dado de personagem encontrado.")