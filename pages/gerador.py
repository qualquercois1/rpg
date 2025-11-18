import streamlit as st
import google.generativeai as genai
import json
import time
import re 
import streamlit.components.v1 as components 

# --- Configuração de Estado ---
if 'theme_index' not in st.session_state:
    st.session_state.theme_index = 0
if 'page' not in st.session_state:
    st.session_state.page = 'formulario' 
if 'character_data' not in st.session_state:
    st.session_state.character_data = None # Mudado de string para objeto/dict

# --- Temas ---
themes = [
    {'titulo': 'Revolta Arcanopunk', 'descricao': 'Em uma cidade onde a tecnologia a vapor e a magia rúnica competem, os jogadores são membros da resistência contra um império tecnológico que busca erradicar a magia.'},
    {'titulo': 'Os Ecos do Cataclismo', 'descricao': 'Mil anos após uma guerra divina que quebrou o mundo, pequenas comunidades sobrevivem em uma terra com anomalias mágicas e ruínas de uma civilização grandiosa.'},
    {'titulo': 'Crônicas do Mar de Serpentes', 'descricao': 'A Era de Ouro da Pirataria, mas os mitos são reais: sereias, krakens e ilhas amaldiçoadas existem e são perigos constantes.'},
    {'titulo': 'O Limiar do Vazio', 'descricao': 'Em um futuro distante, a tripulação de uma nave de exploração encontra algo incompreensível que desafia as leis da física e da sanidade.'},
    {'titulo': 'Sementes do Amanhã', 'descricao': 'Em um futuro otimista pós-colapso, a humanidade reconstrói o mundo de forma sustentável, focando em cooperação e tecnologia limpa.'},
    {'titulo': 'Aleatório', 'descricao': 'Pode ser qualquer coisa'}
]

# --- Função da API Gemini (JSON) ---
def gerar_personagem_json(api_key, dados):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro') 

    # Prompt focado em JSON
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
        
        # Log de tokens
        if hasattr(response, 'usage_metadata'):
            print(f"\n[TOKENS] Prompt: {response.usage_metadata.prompt_token_count} | Resposta: {response.usage_metadata.candidates_token_count}")
        
        # Limpeza básica para garantir JSON válido (caso a IA mande Markdown)
        texto_limpo = response.text.strip()
        if texto_limpo.startswith("```json"):
            texto_limpo = texto_limpo[7:]
        if texto_limpo.endswith("```"):
            texto_limpo = texto_limpo[:-3]
            
        return json.loads(texto_limpo) # Retorna um dicionário Python
    
    except Exception as e:
        print(f"\n[ERRO] {e}\n")
        return None

def formatar_relatorio_markdown(data):
    """Converte o JSON do personagem em um texto Markdown bonito para exibir/baixar."""
    if not data: return ""
    
    attrs = data.get('atributos', {})
    
    md = f"""# 📜 Ficha de Personagem: {data.get('nome', 'Desconhecido')}

**Raça:** {data.get('raca')} | **Classe:** {data.get('classe')}

---
### 📊 Atributos
* **Força:** {attrs.get('forca', 0)}
* **Agilidade:** {attrs.get('agilidade', 0)}
* **Vitalidade:** {attrs.get('vitalidade', 0)}
* **Inteligência:** {attrs.get('inteligencia', 0)}
* **Sobrevivência:** {attrs.get('sobrevivencia', 0)}
* **Magia:** {attrs.get('magia', 0)}

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
        
    return md

# ===================================================================
# --- PÁGINA 1: FORMULÁRIO ---
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

        # --- NOVA SEÇÃO DE ATRIBUTOS ---
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

        # Navegação do Tema
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
                    # Chama a nova função que retorna JSON
                    personagem_json = gerar_personagem_json(api_key, dados_finais)
                    
                    if personagem_json:
                        st.session_state.character_data = personagem_json
                        st.session_state.page = 'relatorio' 
                        st.rerun()
                    else:
                        st.error("Erro ao gerar o personagem. Tente novamente.")

# ===================================================================
# --- PÁGINA 2: RELATÓRIO (JSON -> GRAPHIC) ---
# ===================================================================
elif st.session_state.page == 'relatorio':

    # --- NOVA FUNÇÃO DE GRÁFICO (ACEITA O JSON DIRETO) ---
    def build_hexagon_html(attrs):
        """Gera o HTML completo para o gráfico de hexágono."""
        
        # Pega os valores diretamente do dicionário de atributos
        f = attrs.get('forca', 5)
        a = attrs.get('agilidade', 5)
        i = attrs.get('inteligencia', 5)
        v = attrs.get('vitalidade', 5)
        s = attrs.get('sobrevivencia', 5)
        m = attrs.get('magia', 5)

        # HTML/CSS/JS (Inalterado, apenas a injeção de dados mudou)
        html_string = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hexagono</title>
            <style>
                body {{margin: 0; padding: 0; background-color: #3b3b3b;}}
                canvas {{
                    display: block;
                    margin: 0 auto;
                    width: 100%;
                    max-width: 1280px; 
                    background-color: #161616;
                }}
            </style>
        </head>
        <body>
        <canvas id="canvas"></canvas>
        <script>
            var canvas = document.getElementById('canvas');
            canvas.width = canvas.clientWidth || 600;
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
                    container.font = "20px Inter";
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

            // --- INJEÇÃO DE DADOS DO JSON ---
            meter({f}, {a}, {i}, {v}, {s}, {m});
            
        </script>
        </body>
        </html>
        """
        return html_string
    
    # --- LÓGICA PRINCIPAL ---
    st.title("Ficha de Personagem")

    if st.button("⬅️ Criar Novo Personagem"):
        st.session_state.page = 'formulario'
        st.rerun()

    st.divider()

    data = st.session_state.character_data
    
    if data:
        # 1. Gráfico (Usando os dados do JSON diretamente)
        try:
            # Acessa os atributos de forma segura
            attrs = data.get('atributos', {})
            hexagon_html = build_hexagon_html(attrs)
            
            st.subheader("Gráfico de Atributos")
            components.html(hexagon_html, height=620, scrolling=False) 
            
        except Exception as e:
            st.error(f"Erro ao gerar o gráfico: {e}")

        st.divider()
        
        # 2. Relatório de Texto (Formatado a partir do JSON)
        st.subheader("Relatório Completo")
        relatorio_markdown = formatar_relatorio_markdown(data)
        
        with st.container():
            st.markdown(relatorio_markdown)

        st.divider()
        st.download_button(
            label="💾 Baixar Ficha (TXT)",
            data=relatorio_markdown,
            file_name=f"ficha_{data.get('nome', 'personagem').replace(' ', '_').lower()}.md",
            mime="text/markdown"
        )
    else:
        st.error("Nenhum dado de personagem encontrado.")