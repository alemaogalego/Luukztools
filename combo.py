import keyboard
import time
import pyautogui as py
import ctypes


def _win_move_click(x, y, button='left'):
    """Move + click atômico via Win32 API — sem chance do mouse escapar."""
    ctypes.windll.user32.SetCursorPos(int(x), int(y))
    if button == 'right':
        ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
        ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
    else:
        ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP


def _win_move(x, y):
    """Move mouse sem clicar — Win32 API."""
    ctypes.windll.user32.SetCursorPos(int(x), int(y))


def combopoke(
    pokestop_key, pokemedi_key,
    pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4, pokeattack_key5,
    pokeattack_key6, pokeattack_key7, pokeattack_key8, pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12,
    pokestop_delay, pokemedi_delay,
    pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5,
    pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12
):
    # Executa o combo apenas para teclas válidas
    if pokestop_key:
        keyboard.press_and_release(pokestop_key)  # Pressiona e solta a tecla
        time.sleep(pokestop_delay)
    if pokemedi_key:
        keyboard.press_and_release(pokemedi_key)  # Pressiona e solta a tecla
        time.sleep(pokemedi_delay)
    if pokeattack_key1:
        keyboard.press_and_release(pokeattack_key1)  # Pressiona e solta a tecla
        time.sleep(pokeattack_delay1)
    if pokeattack_key2:
        keyboard.press_and_release(pokeattack_key2)  # Pressiona e solta a tecla
        time.sleep(pokeattack_delay2)
    if pokeattack_key3:
        keyboard.press_and_release(pokeattack_key3)  # Pressiona e solta a tecla
        time.sleep(pokeattack_delay3)
    if pokeattack_key4:
        keyboard.press_and_release(pokeattack_key4)  # Pressiona e solta a tecla
        time.sleep(pokeattack_delay4)
    if pokeattack_key5:
        keyboard.press_and_release(pokeattack_key5)  # Pressiona e solta a tecla
        time.sleep(pokeattack_delay5)
    if pokeattack_key6:
        keyboard.press_and_release(pokeattack_key6)  # Pressiona e solta a tecla
        time.sleep(pokeattack_delay6)     
    if pokeattack_key7:
        keyboard.press_and_release(pokeattack_key7)  # Pressiona e solta a tecla
        time.sleep(pokeattack_delay7)                         
    if pokeattack_key8:
        keyboard.press_and_release(pokeattack_key8) # Pressiona e solta a tecla
        time.sleep(pokeattack_delay8)
    if pokeattack_key9:
        keyboard.press_and_release(pokeattack_key9) # Pressiona e solta a tecla         
        time.sleep(pokeattack_delay9)
    if pokeattack_key10:
        keyboard.press_and_release(pokeattack_key10)    # Pressiona e solta a tecla
        time.sleep(pokeattack_delay10)         
    if pokeattack_key11:
        keyboard.press_and_release(pokeattack_key11)    # Pressiona e solta a tecla
        time.sleep(pokeattack_delay11)         
    if pokeattack_key12:
        keyboard.press_and_release(pokeattack_key12)    # Pressiona e solta a tecla
        time.sleep(pokeattack_delay12)
    print("Combo executado")
    # py.moveTo(pos_poke)
    # py.click(button='right')
    return True



def catchloot():
    keyboard.press_and_release('space')
    time.sleep(0.5)

pos_poke = (32, 59)

def set_pos_poke(x, y):
    """Atualiza a posição global usada pelo revive/clicks."""
    global pos_poke
    pos_poke = (int(x), int(y))
    return pos_poke


pos_center = (956, 346)

def set_center(x, y):
    """Atualiza a posição global usada pelo revive/clicks (center)."""
    global pos_center
    pos_center = (int(x), int(y))
    return pos_center


def revive(revive_key):
    if revive_key:
        py.moveTo(pos_poke)
        py.click(button='right')
        keyboard.press_and_release(revive_key)
        py.moveTo(pos_poke)
        py.click(button='right')
        time.sleep(0.8)
        keyboard.press_and_release("e")
        py.moveTo(pos_center)
    return True


def combo_hunt_dynamic(attacks):
    """
    Executa combo Hunt Normal com lista dinâmica de ações.
    attacks: lista de dicts [{"key": "q", "delay": 0.5, "type": "atk"}, ...]
    - type "atk": pressiona key + delay
    - type "revive": executa rotina completa de revive (right-click, key, right-click, e, move)
    - type "medicine"/"pokestop": pressiona key + delay
    """
    for atk in attacks:
        key = atk.get("key", "")
        delay = atk.get("delay", 0.5)
        tipo = atk.get("type", "atk")

        if not key:
            continue

        if tipo == "revive":
            revive(key)
        else:
            keyboard.press_and_release(key)
            time.sleep(delay)

    print("Combo Hunt executado")
    return True


def combo_nightmare(nightmare_attacks):
    """
    Executa combo no modo Nightmare.
    nightmare_attacks: lista de dicts [{"key1": "alt", "key2": "1", "delay": 0.5, "type": "pokeball"}, ...]
    - type "pokeball": pressiona key1+key2 juntos (combo key para troca de pokémon)
    - type "attack": pressiona key1 sozinha (ataque normal)
    - type "revive": executa rotina completa de revive
    - type "medicine"/"pokestop": pressiona key + delay
    """
    for atk in nightmare_attacks:
        key1 = atk.get("key1", "")
        key2 = atk.get("key2", "")
        delay = atk.get("delay", 0.5)
        tipo = atk.get("type", "attack")

        if not key1:
            continue

        if tipo == "revive":
            revive(key1)
        elif tipo == "pokeball" and key2:
            # Troca de pokémon: combo key (ex: alt+1)
            keyboard.press_and_release(f"{key1}+{key2}")
            time.sleep(delay)
        else:
            # Ataque normal: tecla única
            keyboard.press_and_release(key1)
            time.sleep(delay)

    print("Combo Nightmare executado")
    return True

