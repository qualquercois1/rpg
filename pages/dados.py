import streamlit as st
import random
import time

st.set_page_config(page_title="Rolador de Dados", page_icon="🎲")
st.title("🎲 Rolador de Dados")
st.markdown("Um utilitário simples para quando você esquecer seus dados físicos!")

if 'dice_results' not in st.session_state:
    st.session_state.dice_results = []

def roll_dice(num_dice, num_sides):
    if num_dice <= 0 or num_sides <= 0:
        return None, 0
    
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    total = sum(rolls)
    return rolls, total

st.header("Rolagem Rápida")
st.markdown("Clique para rolar um único dado.")

col1, col2, col3, col4, col5 = st.columns(5)
dice_types = [4, 6, 8, 10, 12, 20]

buttons = {
    'd4': col1.button("Rolar d4", use_container_width=True),
    'd6': col2.button("Rolar d6", use_container_width=True),
    'd8': col3.button("Rolar d8", use_container_width=True),
    'd10': col4.button("Rolar d10", use_container_width=True),
    'd12': col5.button("Rolar d12", use_container_width=True),
    'd20': col1.button("Rolar d20", use_container_width=True, type="primary"), 
}

result_placeholder = st.empty()

for dice_name, clicked in buttons.items():
    if clicked:
        num_sides = int(dice_name[1:])
        rolls, total = roll_dice(1, num_sides)

        with result_placeholder.container():
            st.subheader(f"Rolando d{num_sides}...")
            time.sleep(0.5) 
            st.header(f"Resultado: {total}")

            st.session_state.dice_results.insert(0, f"d{num_sides}: {total}")


st.divider()

st.header("Rolagem Customizada")
col_num, col_sides = st.columns(2)

num_dice = col_num.number_input("Quantidade de Dados", min_value=1, value=1, step=1)
num_sides = col_sides.number_input("Número de Lados (d...)", min_value=2, value=20, step=1)

if st.button("Rolar Customizado"):
    rolls, total = roll_dice(num_dice, num_sides)
    
    with result_placeholder.container():
        st.subheader(f"Rolando {num_dice}d{num_sides}...")
        time.sleep(0.5)
        st.header(f"Resultado: {total}")
        if num_dice > 1:
            st.caption(f"Rolagens individuais: {', '.join(map(str, rolls))}")
        
        st.session_state.dice_results.insert(0, f"{num_dice}d{num_sides}: {total} ({rolls})")

if st.session_state.dice_results:
    st.divider()
    st.subheader("Histórico de Rolagens")
    
    if st.button("Limpar Histórico"):
        st.session_state.dice_results = []
        st.rerun() 

    for result in st.session_state.dice_results[:10]:
        st.code(result)