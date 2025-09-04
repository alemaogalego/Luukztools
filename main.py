import json
import os
import keyboard
import combo
import tkinter as tk
from PIL import Image, ImageTk
import threading
import pyautogui as py

import sys, os

lbl = None  # referência global para o label da mini

def resource_path(relative_path):
    """Acha o arquivo tanto no .py quanto no .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Variáveis globais para armazenar as teclas configuradas
pokestop_key = ""
pokemedi_key = ""
pokeattack_key1 = ""
pokeattack_key2 = ""
pokeattack_key3 = ""
pokeattack_key4 = ""
pokeattack_key5 = ""
pokeattack_key6 = ""
pokeattack_key7 = ""
pokeattack_key8 = ""
pokeattack_key9 = ""
pokeattack_key10 = ""
pokeattack_key11 = ""
pokeattack_key12 = ""

revive_key = ""

# ---- captura da posição (modo configuração) ----
capturando = False
captura_thread = None

# Variável global para controlar o estado do combo
running = False
combo_active = False  # Variável para controlar o estado do botão "Desligado"

# Variáveis globais para armazenar os delays configurados
pokestop_delay = ""
pokemedi_delay = ""
pokeattack_delay1 = ""
pokeattack_delay2 = ""
pokeattack_delay3 = ""
pokeattack_delay4 = ""
pokeattack_delay5 = ""
pokeattack_delay6 = ""
pokeattack_delay7 = ""
pokeattack_delay8 = ""
pokeattack_delay9 = ""
pokeattack_delay10 = ""
pokeattack_delay11 = ""
pokeattack_delay12 = ""

PERFIS_FILE = "perfis.json"
perfil_ativo = "default"
perfis = {}

def carregar_perfis():
    global perfis
    if os.path.exists(PERFIS_FILE):
        with open(PERFIS_FILE, "r") as f:
            perfis = json.load(f)
    else:
        perfis = {"default": {}}

def salvar_perfis():
    with open(PERFIS_FILE, "w") as f:
        json.dump(perfis, f, indent=2)

def aplicar_perfil(nome):
    global perfil_ativo
    global pokestop_key, pokemedi_key, pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4, pokeattack_key5
    global pokeattack_key6, pokeattack_key7, pokeattack_key8, pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12
    global revive_key
    global pokestop_delay, pokemedi_delay, pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5
    global pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12, combo_start_key, lbl

    perfil = perfis.get(nome, {})
    pokestop_key = perfil.get("pokestop_key", "")
    pokemedi_key = perfil.get("pokemedi_key", "")
    pokeattack_key1 = perfil.get("pokeattack_key1", "")
    pokeattack_key2 = perfil.get("pokeattack_key2", "")
    pokeattack_key3 = perfil.get("pokeattack_key3", "")
    pokeattack_key4 = perfil.get("pokeattack_key4", "")
    pokeattack_key5 = perfil.get("pokeattack_key5", "")
    pokeattack_key6 = perfil.get("pokeattack_key6", "")
    pokeattack_key7 = perfil.get("pokeattack_key7", "")
    pokeattack_key8 = perfil.get("pokeattack_key8", "")
    pokeattack_key9 = perfil.get("pokeattack_key9", "")
    pokeattack_key10 = perfil.get("pokeattack_key10", "")
    pokeattack_key11 = perfil.get("pokeattack_key11", "")
    pokeattack_key12 = perfil.get("pokeattack_key12", "")
    revive_key = perfil.get("revive_key", "")
    pokestop_delay = perfil.get("pokestop_delay", "")
    pokemedi_delay = perfil.get("pokemedi_delay", "")
    pokeattack_delay1 = perfil.get("pokeattack_delay1", "")
    pokeattack_delay2 = perfil.get("pokeattack_delay2", "")
    pokeattack_delay3 = perfil.get("pokeattack_delay3", "")
    pokeattack_delay4 = perfil.get("pokeattack_delay4", "")
    pokeattack_delay5 = perfil.get("pokeattack_delay5", "")
    pokeattack_delay6 = perfil.get("pokeattack_delay6", "")
    pokeattack_delay7 = perfil.get("pokeattack_delay7", "")
    pokeattack_delay8 = perfil.get("pokeattack_delay8", "")
    pokeattack_delay9 = perfil.get("pokeattack_delay9", "")
    pokeattack_delay10 = perfil.get("pokeattack_delay10", "")
    pokeattack_delay11 = perfil.get("pokeattack_delay11", "")
    pokeattack_delay12 = perfil.get("pokeattack_delay12", "")
    combo_start_key = perfil.get("combo_start_key", "")
    perfil_ativo = nome
    try:
        if lbl is not None:
            lbl.config(text=f"LukzTools ({perfil_ativo})")
    except Exception as e:
        print(f"Não consegui atualizar o nome na mini: {e}")
    
def salvar_perfil_atual(nome):
    perfis[nome] = {
        "pokestop_key": pokestop_key,
        "pokemedi_key": pokemedi_key,
        "pokeattack_key1": pokeattack_key1,
        "pokeattack_key2": pokeattack_key2,
        "pokeattack_key3": pokeattack_key3,
        "pokeattack_key4": pokeattack_key4,
        "pokeattack_key5": pokeattack_key5,
        "pokeattack_key6": pokeattack_key6,
        "pokeattack_key7": pokeattack_key7,
        "pokeattack_key8": pokeattack_key8,
        "pokeattack_key9": pokeattack_key9,
        "pokeattack_key10": pokeattack_key10,
        "pokeattack_key11": pokeattack_key11,
        "pokeattack_key12": pokeattack_key12,
        "revive_key": revive_key,
        "pokestop_delay": pokestop_delay,
        "pokemedi_delay": pokemedi_delay,
        "pokeattack_delay1": pokeattack_delay1,
        "pokeattack_delay2": pokeattack_delay2,
        "pokeattack_delay3": pokeattack_delay3,
        "pokeattack_delay4": pokeattack_delay4,
        "pokeattack_delay5": pokeattack_delay5,
        "pokeattack_delay6": pokeattack_delay6,
        "pokeattack_delay7": pokeattack_delay7,
        "pokeattack_delay8": pokeattack_delay8,
        "pokeattack_delay9": pokeattack_delay9,
        "pokeattack_delay10": pokeattack_delay10,
        "pokeattack_delay11": pokeattack_delay11,
        "pokeattack_delay12": pokeattack_delay12,
        "combo_start_key": combo_start_key
    }
    salvar_perfis()

def excluir_perfil(nome):
    if nome in perfis and nome != "default":
        del perfis[nome]
        salvar_perfis()

combo_start_key = ""  # Defina a tecla padrão ou carregue do perfil

def start_combo():
    if combo_active:
        combo.combopoke(
            pokestop_key, pokemedi_key,
            pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4, pokeattack_key5,
            pokeattack_key6, pokeattack_key7, pokeattack_key8, pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12,
            pokestop_delay, pokemedi_delay,
            pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5,
            pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12
        )
        print("Combo executado com sucesso!")
        combo.revive(revive_key)
        print("Revive executado!")
    else:
        print("Combo está desligado, não executa!")

def toggle_activation():
    global combo_active
    if combo_active:
        combo_active = False
        button_activation.config(bg="red", text="Desligado")
        keyboard.remove_hotkey(combo_start_key)
        print('Botao para iniciar combo está desativado')
    else:
        combo_active = True
        button_activation.config(bg="green", text="Ativado")
        keyboard.add_hotkey(combo_start_key, start_combo)
        print('Botao para iniciar combo está ativado')

def open_janelacombo():
    def save_key():
        global pokestop_key, pokemedi_key, pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4, revive_key, pokeattack_key5
        global pokeattack_key6, pokeattack_key7, pokeattack_key8, pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12
        global pokestop_delay, pokemedi_delay, pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5
        global pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12
        global combo_start_key

        def get_delay(entry, default=0.5):
            value = entry.get()
            try:
                return float(value)
            except ValueError:
                return default

        pokestop_key = entry_pokestop.get()
        pokestop_delay = get_delay(entry_pokestop_delay)
        pokemedi_key = entry_medicine.get()
        pokemedi_delay = get_delay(entry_medicine_delay)
        pokeattack_key1 = entry_attack1.get()
        pokeattack_delay1 = get_delay(entry_attack1_delay)
        pokeattack_key2 = entry_attack2.get()
        pokeattack_delay2 = get_delay(entry_attack2_delay)
        pokeattack_key3 = entry_attack3.get()
        pokeattack_delay3 = get_delay(entry_attack3_delay)
        pokeattack_key4 = entry_attack4.get()
        pokeattack_delay4 = get_delay(entry_attack4_delay)
        pokeattack_key5 = entry_attack5.get()
        pokeattack_delay5 = get_delay(entry_attack5_delay)
        pokeattack_key6 = entry_attack6.get()
        pokeattack_delay6 = get_delay(entry_attack6_delay)
        pokeattack_key7 = entry_attack7.get()
        pokeattack_delay7 = get_delay(entry_attack7_delay)
        pokeattack_key8 = entry_attack8.get()
        pokeattack_delay8 = get_delay(entry_attack8_delay)
        pokeattack_key9 = entry_attack9.get()
        pokeattack_delay9 = get_delay(entry_attack9_delay)
        pokeattack_key10 = entry_attack10.get()
        pokeattack_delay10 = get_delay(entry_attack10_delay)
        pokeattack_key11 = entry_attack11.get()
        pokeattack_delay11 = get_delay(entry_attack11_delay)
        pokeattack_key12 = entry_attack12.get()
        pokeattack_delay12 = get_delay(entry_attack12_delay)
        revive_key = entry_revive.get()
        combo_start_key = entry_iniciar_combo.get()
        print("Teclas e delays configurados!")
        salvar_perfil_atual(perfil_ativo)  # <-- Adicione esta linha para salvar as hotkeys no perfil ativo

    # Cria uma nova janela
    new_window = tk.Toplevel()
    new_window.title("Configuração do Combo")
    new_window.geometry("350x600")  # Define o tamanho da nova janela

    # Adiciona um rótulo na nova janela
    tk.Label(new_window, text="Bem-vindo à configuração do Combo!", font=("Arial", 12)).pack(pady=10)

    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Combo Start Key  
    frame_combo_start = tk.Frame(new_window)
    frame_combo_start.pack(pady=5)
    tk.Label(frame_combo_start, text="combo_start:").pack(side="left", padx=5)
    entry_combo_start = tk.Entry(frame_combo_start, width=8)
    entry_combo_start.insert(0, combo_start_key)  # Valor padrão
    entry_combo_start.pack(side="left", padx=5)

    
    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Pokestop
    frame_pokestop = tk.Frame(new_window)
    frame_pokestop.pack(pady=5)
    tk.Label(frame_pokestop, text="Pokestop:").pack(side="left", padx=5)
    entry_pokestop = tk.Entry(frame_pokestop, width=8)
    entry_pokestop.insert(0, pokestop_key)  # Valor padrão
    entry_pokestop.pack(side="left", padx=5)
    tk.Label(frame_pokestop, text="Delay:").pack(side="left", padx=2)
    entry_pokestop_delay = tk.Entry(frame_pokestop, width=5)
    entry_pokestop_delay.insert(0, str(pokestop_delay))
    entry_pokestop_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Medicine
    frame_medicine = tk.Frame(new_window)
    frame_medicine.pack(pady=5)
    tk.Label(frame_medicine, text="Medicine:").pack(side="left", padx=5)
    entry_medicine = tk.Entry(frame_medicine, width=8)
    entry_medicine.insert(0, pokemedi_key)  # Valor padrão
    entry_medicine.pack(side="left", padx=5)
    tk.Label(frame_medicine, text="Delay:").pack(side="left", padx=2)
    entry_medicine_delay = tk.Entry(frame_medicine, width=5)
    entry_medicine_delay.insert(0, str(pokemedi_delay))
    entry_medicine_delay.pack(side="left", padx=2)
    

    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para revive
    frame_revive = tk.Frame(new_window)
    frame_revive.pack(pady=5)
    tk.Label(frame_revive, text="Revive:").pack(side="left", padx=5)
    entry_revive = tk.Entry(frame_revive)
    entry_revive.insert(0, revive_key)
    entry_revive.pack(side="left", padx=5)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 1
    frame_attack1 = tk.Frame(new_window)
    frame_attack1.pack(pady=5)
    tk.Label(frame_attack1, text="Attack 1:").pack(side="left", padx=5)
    entry_attack1 = tk.Entry(frame_attack1, width=8)
    entry_attack1.insert(0, pokeattack_key1)  # Valor padrão
    entry_attack1.pack(side="left", padx=5)
    tk.Label(frame_attack1, text="Delay:").pack(side="left", padx=2)
    entry_attack1_delay = tk.Entry(frame_attack1, width=5)
    entry_attack1_delay.insert(0, str(pokeattack_delay1))
    entry_attack1_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 2
    frame_attack2 = tk.Frame(new_window)
    frame_attack2.pack(pady=5)
    tk.Label(frame_attack2, text="Attack 2:").pack(side="left", padx=5)
    entry_attack2 = tk.Entry(frame_attack2, width=8)
    entry_attack2.insert(0, pokeattack_key2)  # Valor padrão
    entry_attack2.pack(side="left", padx=5)
    tk.Label(frame_attack2, text="Delay:").pack(side="left", padx=2)
    entry_attack2_delay = tk.Entry(frame_attack2, width=5)
    entry_attack2_delay.insert(0, str(pokeattack_delay2))
    entry_attack2_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 3
    frame_attack3 = tk.Frame(new_window)
    frame_attack3.pack(pady=5)
    tk.Label(frame_attack3, text="Attack 3:").pack(side="left", padx=5)
    entry_attack3 = tk.Entry(frame_attack3, width=8)
    entry_attack3.insert(0, pokeattack_key3)  # Valor padrão
    entry_attack3.pack(side="left", padx=5)
    tk.Label(frame_attack3, text="Delay:").pack(side="left", padx=2)
    entry_attack3_delay = tk.Entry(frame_attack3, width=5)
    entry_attack3_delay.insert(0, str(pokeattack_delay3))
    entry_attack3_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 4
    frame_attack4 = tk.Frame(new_window)
    frame_attack4.pack(pady=5)
    tk.Label(frame_attack4, text="Attack 4:").pack(side="left", padx=5)
    entry_attack4 = tk.Entry(frame_attack4, width=8)
    entry_attack4.insert(0, pokeattack_key4)  # Valor padrão
    entry_attack4.pack(side="left", padx=5)
    tk.Label(frame_attack4, text="Delay:").pack(side="left", padx=2)
    entry_attack4_delay = tk.Entry(frame_attack4, width=5)
    entry_attack4_delay.insert(0, str(pokeattack_delay4))
    entry_attack4_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 5
    frame_attack5 = tk.Frame(new_window)
    frame_attack5.pack(pady=5)
    tk.Label(frame_attack5, text="Attack 5:").pack(side="left", padx=5)
    entry_attack5 = tk.Entry(frame_attack5, width=8)
    entry_attack5.insert(0, pokeattack_key5)  # Valor padrão
    entry_attack5.pack(side="left", padx=5)
    tk.Label(frame_attack5, text="Delay:").pack(side="left", padx=2)
    entry_attack5_delay = tk.Entry(frame_attack5, width=5)
    entry_attack5_delay.insert(0, str(pokeattack_delay5))
    entry_attack5_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 6
    frame_attack6 = tk.Frame(new_window)
    frame_attack6.pack(pady=5)
    tk.Label(frame_attack6, text="Attack 6:").pack(side="left", padx=5)
    entry_attack6 = tk.Entry(frame_attack6, width=8)
    entry_attack6.insert(0, pokeattack_key6)  # Valor padrão
    entry_attack6.pack(side="left", padx=5)
    tk.Label(frame_attack6, text="Delay:").pack(side="left", padx=2)
    entry_attack6_delay = tk.Entry(frame_attack6, width=5)
    entry_attack6_delay.insert(0, str(pokeattack_delay6))
    entry_attack6_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 7
    frame_attack7 = tk.Frame(new_window)
    frame_attack7.pack(pady=5)
    tk.Label(frame_attack7, text="Attack 7:").pack(side="left", padx=5)
    entry_attack7 = tk.Entry(frame_attack7, width=8)
    entry_attack7.insert(0, pokeattack_key7)  # Valor padrão
    entry_attack7.pack(side="left", padx=5)
    tk.Label(frame_attack7, text="Delay:").pack(side="left", padx=2)
    entry_attack7_delay = tk.Entry(frame_attack7, width=5)
    entry_attack7_delay.insert(0, str(pokeattack_delay7))
    entry_attack7_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 8
    frame_attack8 = tk.Frame(new_window)
    frame_attack8.pack(pady=5)
    tk.Label(frame_attack8, text="Attack 8:").pack(side="left", padx=5)
    entry_attack8 = tk.Entry(frame_attack8, width=8)
    entry_attack8.insert(0, pokeattack_key8)  # Valor padrão
    entry_attack8.pack(side="left", padx=5)
    tk.Label(frame_attack8, text="Delay:").pack(side="left", padx=2)
    entry_attack8_delay = tk.Entry(frame_attack8, width=5)
    entry_attack8_delay.insert(0, str(pokeattack_delay8))
    entry_attack8_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 9
    frame_attack9 = tk.Frame(new_window)
    frame_attack9.pack(pady=5)
    tk.Label(frame_attack9, text="Attack 9:").pack(side="left", padx=5)
    entry_attack9 = tk.Entry(frame_attack9, width=8)
    entry_attack9.insert(0, pokeattack_key9)  # Valor padrão
    entry_attack9.pack(side="left", padx=5)
    tk.Label(frame_attack9, text="Delay:").pack(side="left", padx=2)
    entry_attack9_delay = tk.Entry(frame_attack9, width=5)
    entry_attack9_delay.insert(0, str(pokeattack_delay9))
    entry_attack9_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 10
    frame_attack10 = tk.Frame(new_window)
    frame_attack10.pack(pady=5)
    tk.Label(frame_attack10, text="Attack 10:").pack(side="left", padx=5)
    entry_attack10 = tk.Entry(frame_attack10, width=8)
    entry_attack10.insert(0, pokeattack_key10)  # Valor padrão
    entry_attack10.pack(side="left", padx=5)
    tk.Label(frame_attack10, text="Delay:").pack(side="left", padx=2)
    entry_attack10_delay = tk.Entry(frame_attack10, width=5)
    entry_attack10_delay.insert(0, str(pokeattack_delay10))
    entry_attack10_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 11
    frame_attack11 = tk.Frame(new_window)
    frame_attack11.pack(pady=5)
    tk.Label(frame_attack11, text="Attack 11:").pack(side="left", padx=5)
    entry_attack11 = tk.Entry(frame_attack11, width=8)
    entry_attack11.insert(0, pokeattack_key11)  # Valor padrão
    entry_attack11.pack(side="left", padx=5)
    tk.Label(frame_attack11, text="Delay:").pack(side="left", padx=2)
    entry_attack11_delay = tk.Entry(frame_attack11, width=5)
    entry_attack11_delay.insert(0, str(pokeattack_delay11))
    entry_attack11_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 12
    frame_attack12 = tk.Frame(new_window)
    frame_attack12.pack(pady=5)
    tk.Label(frame_attack12, text="Attack 12:").pack(side="left", padx=5)
    entry_attack12 = tk.Entry(frame_attack12, width=8)
    entry_attack12.insert(0, pokeattack_key12)  # Valor padrão
    entry_attack12.pack(side="left", padx=5)
    tk.Label(frame_attack12, text="Delay:").pack(side="left", padx=2)
    entry_attack12_delay = tk.Entry(frame_attack12, width=5)
    entry_attack12_delay.insert(0, str(pokeattack_delay12))
    entry_attack12_delay.pack(side="left", padx=2)


    # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Iniciar Combo
    frame_iniciar_combo = tk.Frame(new_window)
    frame_iniciar_combo.pack(pady=5)
    tk.Label(frame_iniciar_combo, text="Iniciar Combo:").pack(side="left", padx=5)
    entry_iniciar_combo = tk.Entry(frame_iniciar_combo, width=8)
    entry_iniciar_combo.insert(0, combo_start_key)  # Valor padrão
    entry_iniciar_combo.pack(side="left", padx=5)

    # Adiciona um botão para salvar a configuração
    tk.Button(new_window, text="Salvar", command=save_key).pack(pady=10)

def _loop_captura():
    """Loop que espera a tecla 'h' e grava pyautogui.position() em combo.set_pos_poke."""
    global capturando
    while capturando:
        key = keyboard.read_event(suppress=True)
        if not capturando:
            break

        # só reage se for key down
        if key.event_type != keyboard.KEY_DOWN:
            continue

        if key.name == 'h':  # salvar pos_poke
            x, y = py.position()
            combo.set_pos_poke(x, y)
            print(f"pos_poke atualizado: ({x}, {y})")

        elif key.name == 'j':  # salvar center
            x, y = py.position()
            combo.set_center(x, y)
            print(f"center atualizado: ({x}, {y})")

def main():
    global button_combo, button_activation, perfil_label, lbl
    carregar_perfis()
    aplicar_perfil(perfil_ativo)

    root = tk.Tk()
    root.title("LukzTools Interface")
    root.geometry("400x350")
    root.resizable(False, False)

    
    # Carrega o ícone
    icon_img = Image.open(resource_path("logo.jpg"))
    icon_img = icon_img.resize((32, 32))  # Tamanho padrão de ícone
    icon_photo = ImageTk.PhotoImage(icon_img)
    root.iconphoto(True, icon_photo)

    # Carrega a imagem de fundo
    bg_image = Image.open(resource_path("imgfundo.jpg"))
    bg_image = bg_image.resize((400, 350))
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_label.image = bg_photo

    perfil_label = tk.Label(root, text=f"Perfil ativo: {perfil_ativo}", font=("Arial", 12), fg="blue", bg="#ffffff")
    perfil_label.pack(pady=10)
    
    # Área de log
    log_text = tk.Text(root, height=1.2, width=45, state="disabled", bg="#f0f0f0")
    log_text.pack(pady=5)

    def log_message(msg):
        log_text.config(state="normal")
        log_text.delete("1.0", tk.END)  # limpa tudo antes
        log_text.insert(tk.END, msg + "\n")
        log_text.config(state="disabled")

    class TextRedirector:
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, msg):
            if msg.strip():  # evita linhas vazias
                log_message(msg.strip())

        def flush(self):  # necessário para compatibilidade
            pass

    # Redireciona os prints para a área de log
    sys.stdout = TextRedirector(log_text)
    sys.stderr = TextRedirector(log_text)
    
    def abrir_configuracao():
        cfg = tk.Toplevel(root)             # cfg só existe aqui dentro
        cfg.title("Configuração")
        cfg.geometry("500x200")
        cfg.resizable(False, False)

        tk.Label(cfg, text="Modo Captura do revive e pos_center", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(cfg, text="Clique em Ativar e depois pressione 'h' e na foto do pokemon para revive \n" 
                 "O mesmo para pressione 'j' para perto do seu personagem onde quiser salvar o clique.", justify="center").pack()

        status_var = tk.StringVar(value="Desativado")

        def start_captura():
            nonlocal status_var
            global capturando, captura_thread
            if capturando:
                return
            capturando = True
            status_var.set("Ativado (aperte 'h')")
            captura_thread = threading.Thread(target=_loop_captura, daemon=True)
            captura_thread.start()
            print("Modo captura iniciado — aperte 'h' para gravar o revive e 'j' para gravar o center perto do seu personagem.")

        def stop_captura():
            nonlocal status_var
            global capturando
            if not capturando:
                return
            capturando = False
            status_var.set("Desativado")
            print("Modo captura finalizado.")

        tk.Button(cfg, text="▶ Ativar captura (h = poke, j = center)", command=start_captura).pack(pady=10)
        tk.Button(cfg, text="■ Desativar captura", command=stop_captura).pack()

        tk.Label(cfg, textvariable=status_var, fg="blue").pack(pady=8)

        def on_close():
            # garante que a thread saia do loop na próxima tecla ou imediatamente se não estiver esperando
            stop_captura()
            cfg.destroy()

        cfg.protocol("WM_DELETE_WINDOW", on_close)

    btn_cfg = tk.Button(root, text="⚙ Configuração", command=abrir_configuracao)
    btn_cfg.place(x=8, y=8)  # canto superior-esquerdo (ajuste como quiser)
    
    def atualizar_perfil_label():
        perfil_label.config(text=f"Perfil ativo: {perfil_ativo}")

    # Controle de janelas
    janela_criar_perfil = None
    janela_selecionar_perfil = None
    janela_excluir_perfil = None
    janela_combo = None  # Adicione esta linha

    def open_janelacombo():
        nonlocal janela_combo
        if janela_combo is not None and janela_combo.winfo_exists():
            janela_combo.lift()
            return

        def save_key():
            global pokestop_key, pokemedi_key, pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4, revive_key, pokeattack_key5
            global pokeattack_key6, pokeattack_key7, pokeattack_key8, pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12
            global pokestop_delay, pokemedi_delay, pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5
            global pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12
            global combo_start_key

            def get_delay(entry, default=0.5):
                value = entry.get()
                try:
                    return float(value)
                except ValueError:
                    return default

            pokestop_key = entry_pokestop.get()
            pokestop_delay = get_delay(entry_pokestop_delay)
            pokemedi_key = entry_medicine.get()
            pokemedi_delay = get_delay(entry_medicine_delay)
            pokeattack_key1 = entry_attack1.get()
            pokeattack_delay1 = get_delay(entry_attack1_delay)
            pokeattack_key2 = entry_attack2.get()
            pokeattack_delay2 = get_delay(entry_attack2_delay)
            pokeattack_key3 = entry_attack3.get()
            pokeattack_delay3 = get_delay(entry_attack3_delay)
            pokeattack_key4 = entry_attack4.get()
            pokeattack_delay4 = get_delay(entry_attack4_delay)
            pokeattack_key5 = entry_attack5.get()
            pokeattack_delay5 = get_delay(entry_attack5_delay)
            pokeattack_key6 = entry_attack6.get()
            pokeattack_delay6 = get_delay(entry_attack6_delay)
            pokeattack_key7 = entry_attack7.get()
            pokeattack_delay7 = get_delay(entry_attack7_delay)
            pokeattack_key8 = entry_attack8.get()
            pokeattack_delay8 = get_delay(entry_attack8_delay)
            pokeattack_key9 = entry_attack9.get()
            pokeattack_delay9 = get_delay(entry_attack9_delay)
            pokeattack_key10 = entry_attack10.get()
            pokeattack_delay10 = get_delay(entry_attack10_delay)
            pokeattack_key11 = entry_attack11.get()
            pokeattack_delay11 = get_delay(entry_attack11_delay)
            pokeattack_key12 = entry_attack12.get()
            pokeattack_delay12 = get_delay(entry_attack12_delay)
            revive_key = entry_revive.get()
            combo_start_key = entry_iniciar_combo.get()
            print("Teclas e delays configurados!")
            salvar_perfil_atual(perfil_ativo)

        janela_combo = tk.Toplevel(root)
        janela_combo.title("Configuração do Combo")
        janela_combo.geometry("350x600")
        janela_combo.resizable(False, False)
        janela_combo.iconphoto(True, icon_photo)
        

        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Pokestop
        frame_pokestop = tk.Frame(janela_combo)
        frame_pokestop.pack(pady=5)
        tk.Label(frame_pokestop, text="Pokestop:").pack(side="left", padx=5)
        entry_pokestop = tk.Entry(frame_pokestop, width=8)
        entry_pokestop.insert(0, pokestop_key)  # Valor padrão
        entry_pokestop.pack(side="left", padx=5)
        tk.Label(frame_pokestop, text="Delay:").pack(side="left", padx=2)
        entry_pokestop_delay = tk.Entry(frame_pokestop, width=5)
        entry_pokestop_delay.insert(0, str(pokestop_delay))
        entry_pokestop_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Medicine
        frame_medicine = tk.Frame(janela_combo)
        frame_medicine.pack(pady=5)
        tk.Label(frame_medicine, text="Medicine:").pack(side="left", padx=5)
        entry_medicine = tk.Entry(frame_medicine, width=8)
        entry_medicine.insert(0, pokemedi_key)  # Valor padrão
        entry_medicine.pack(side="left", padx=5)
        tk.Label(frame_medicine, text="Delay:").pack(side="left", padx=2)
        entry_medicine_delay = tk.Entry(frame_medicine, width=5)
        entry_medicine_delay.insert(0, str(pokemedi_delay))
        entry_medicine_delay.pack(side="left", padx=2)
        

        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para revive
        frame_revive = tk.Frame(janela_combo)
        frame_revive.pack(pady=5)
        tk.Label(frame_revive, text="Revive:").pack(side="left", padx=5)
        entry_revive = tk.Entry(frame_revive)
        entry_revive.insert(0, revive_key)
        entry_revive.pack(side="left", padx=5)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 1
        frame_attack1 = tk.Frame(janela_combo)
        frame_attack1.pack(pady=5)
        tk.Label(frame_attack1, text="Attack 1:").pack(side="left", padx=5)
        entry_attack1 = tk.Entry(frame_attack1, width=8)
        entry_attack1.insert(0, pokeattack_key1)  # Valor padrão
        entry_attack1.pack(side="left", padx=5)
        tk.Label(frame_attack1, text="Delay:").pack(side="left", padx=2)
        entry_attack1_delay = tk.Entry(frame_attack1, width=5)
        entry_attack1_delay.insert(0, str(pokeattack_delay1))
        entry_attack1_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 2
        frame_attack2 = tk.Frame(janela_combo)
        frame_attack2.pack(pady=5)
        tk.Label(frame_attack2, text="Attack 2:").pack(side="left", padx=5)
        entry_attack2 = tk.Entry(frame_attack2, width=8)
        entry_attack2.insert(0, pokeattack_key2)  # Valor padrão
        entry_attack2.pack(side="left", padx=5)
        tk.Label(frame_attack2, text="Delay:").pack(side="left", padx=2)
        entry_attack2_delay = tk.Entry(frame_attack2, width=5)
        entry_attack2_delay.insert(0, str(pokeattack_delay2))
        entry_attack2_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 3
        frame_attack3 = tk.Frame(janela_combo)
        frame_attack3.pack(pady=5)
        tk.Label(frame_attack3, text="Attack 3:").pack(side="left", padx=5)
        entry_attack3 = tk.Entry(frame_attack3, width=8)
        entry_attack3.insert(0, pokeattack_key3)  # Valor padrão
        entry_attack3.pack(side="left", padx=5)
        tk.Label(frame_attack3, text="Delay:").pack(side="left", padx=2)
        entry_attack3_delay = tk.Entry(frame_attack3, width=5)
        entry_attack3_delay.insert(0, str(pokeattack_delay3))
        entry_attack3_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 4
        frame_attack4 = tk.Frame(janela_combo)
        frame_attack4.pack(pady=5)
        tk.Label(frame_attack4, text="Attack 4:").pack(side="left", padx=5)
        entry_attack4 = tk.Entry(frame_attack4, width=8)
        entry_attack4.insert(0, pokeattack_key4)  # Valor padrão
        entry_attack4.pack(side="left", padx=5)
        tk.Label(frame_attack4, text="Delay:").pack(side="left", padx=2)
        entry_attack4_delay = tk.Entry(frame_attack4, width=5)
        entry_attack4_delay.insert(0, str(pokeattack_delay4))
        entry_attack4_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 5
        frame_attack5 = tk.Frame(janela_combo)
        frame_attack5.pack(pady=5)
        tk.Label(frame_attack5, text="Attack 5:").pack(side="left", padx=5)
        entry_attack5 = tk.Entry(frame_attack5, width=8)
        entry_attack5.insert(0, pokeattack_key5)  # Valor padrão
        entry_attack5.pack(side="left", padx=5)
        tk.Label(frame_attack5, text="Delay:").pack(side="left", padx=2)
        entry_attack5_delay = tk.Entry(frame_attack5, width=5)
        entry_attack5_delay.insert(0, str(pokeattack_delay5))
        entry_attack5_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 6
        frame_attack6 = tk.Frame(janela_combo)
        frame_attack6.pack(pady=5)
        tk.Label(frame_attack6, text="Attack 6:").pack(side="left", padx=5)
        entry_attack6 = tk.Entry(frame_attack6, width=8)
        entry_attack6.insert(0, pokeattack_key6)  # Valor padrão
        entry_attack6.pack(side="left", padx=5)
        tk.Label(frame_attack6, text="Delay:").pack(side="left", padx=2)
        entry_attack6_delay = tk.Entry(frame_attack6, width=5)
        entry_attack6_delay.insert(0, str(pokeattack_delay6))
        entry_attack6_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 7
        frame_attack7 = tk.Frame(janela_combo)
        frame_attack7.pack(pady=5)
        tk.Label(frame_attack7, text="Attack 7:").pack(side="left", padx=5)
        entry_attack7 = tk.Entry(frame_attack7, width=8)
        entry_attack7.insert(0, pokeattack_key7)  # Valor padrão
        entry_attack7.pack(side="left", padx=5)
        tk.Label(frame_attack7, text="Delay:").pack(side="left", padx=2)
        entry_attack7_delay = tk.Entry(frame_attack7, width=5)
        entry_attack7_delay.insert(0, str(pokeattack_delay7))
        entry_attack7_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 8
        frame_attack8 = tk.Frame(janela_combo)
        frame_attack8.pack(pady=5)
        tk.Label(frame_attack8, text="Attack 8:").pack(side="left", padx=5)
        entry_attack8 = tk.Entry(frame_attack8, width=8)
        entry_attack8.insert(0, pokeattack_key8)  # Valor padrão
        entry_attack8.pack(side="left", padx=5)
        tk.Label(frame_attack8, text="Delay:").pack(side="left", padx=2)
        entry_attack8_delay = tk.Entry(frame_attack8, width=5)
        entry_attack8_delay.insert(0, str(pokeattack_delay8))
        entry_attack8_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 9
        frame_attack9 = tk.Frame(janela_combo)
        frame_attack9.pack(pady=5)
        tk.Label(frame_attack9, text="Attack 9:").pack(side="left", padx=5)
        entry_attack9 = tk.Entry(frame_attack9, width=8)
        entry_attack9.insert(0, pokeattack_key9)  # Valor padrão
        entry_attack9.pack(side="left", padx=5)
        tk.Label(frame_attack9, text="Delay:").pack(side="left", padx=2)
        entry_attack9_delay = tk.Entry(frame_attack9, width=5)
        entry_attack9_delay.insert(0, str(pokeattack_delay9))
        entry_attack9_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 10
        frame_attack10 = tk.Frame(janela_combo)
        frame_attack10.pack(pady=5)
        tk.Label(frame_attack10, text="Attack 10:").pack(side="left", padx=5)
        entry_attack10 = tk.Entry(frame_attack10, width=8)
        entry_attack10.insert(0, pokeattack_key10)  # Valor padrão
        entry_attack10.pack(side="left", padx=5)
        tk.Label(frame_attack10, text="Delay:").pack(side="left", padx=2)
        entry_attack10_delay = tk.Entry(frame_attack10, width=5)
        entry_attack10_delay.insert(0, str(pokeattack_delay10))
        entry_attack10_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 11
        frame_attack11 = tk.Frame(janela_combo)
        frame_attack11.pack(pady=5)
        tk.Label(frame_attack11, text="Attack 11:").pack(side="left", padx=5)
        entry_attack11 = tk.Entry(frame_attack11, width=8)
        entry_attack11.insert(0, pokeattack_key11)  # Valor padrão
        entry_attack11.pack(side="left", padx=5)
        tk.Label(frame_attack11, text="Delay:").pack(side="left", padx=2)
        entry_attack11_delay = tk.Entry(frame_attack11, width=5)
        entry_attack11_delay.insert(0, str(pokeattack_delay11))
        entry_attack11_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Attack 12
        frame_attack12 = tk.Frame(janela_combo)
        frame_attack12.pack(pady=5)
        tk.Label(frame_attack12, text="Attack 12:").pack(side="left", padx=5)
        entry_attack12 = tk.Entry(frame_attack12, width=8)
        entry_attack12.insert(0, pokeattack_key12)  # Valor padrão
        entry_attack12.pack(side="left", padx=5)
        tk.Label(frame_attack12, text="Delay:").pack(side="left", padx=2)
        entry_attack12_delay = tk.Entry(frame_attack12, width=5)
        entry_attack12_delay.insert(0, str(pokeattack_delay12))
        entry_attack12_delay.pack(side="left", padx=2)


        # Cria um frame para alinhar o rótulo e a entrada horizontalmente para Iniciar Combo
        frame_iniciar_combo = tk.Frame(janela_combo)
        frame_iniciar_combo.pack(pady=5)
        tk.Label(frame_iniciar_combo, text="Iniciar Combo:").pack(side="left", padx=5)
        entry_iniciar_combo = tk.Entry(frame_iniciar_combo, width=8)
        entry_iniciar_combo.insert(0, combo_start_key)  # Valor padrão
        entry_iniciar_combo.pack(side="left", padx=5)

        # Adiciona um botão para salvar a configuração
        tk.Button(janela_combo, text="Salvar", command=save_key).pack(pady=10)

        def on_close():
            nonlocal janela_combo
            janela_combo.destroy()
            janela_combo = None
        janela_combo.protocol("WM_DELETE_WINDOW", on_close)

    def selecionar_perfil():
        nonlocal janela_selecionar_perfil
        if janela_selecionar_perfil is not None and janela_selecionar_perfil.winfo_exists():
            janela_selecionar_perfil.lift()
            return
        def aplicar_e_fechar():
            nonlocal janela_selecionar_perfil
            nome = var_perfil.get()
            if nome in perfis:
                aplicar_perfil(nome)
                atualizar_perfil_label()
                print(f"Perfil selecionado: {nome}")   # <-- log aqui
                janela_selecionar_perfil.destroy()
                janela_selecionar_perfil = None
        janela_selecionar_perfil = tk.Toplevel(root)
        janela_selecionar_perfil.title("Selecionar Perfil")
        janela_selecionar_perfil.geometry("350x200")
        janela_selecionar_perfil.resizable(False, False)
        janela_selecionar_perfil.iconphoto(True, icon_photo)

        # Adiciona a imagem de fundo
        selecionar_bg_img = Image.open(resource_path("selecionar.jpg"))
        selecionar_bg_img = selecionar_bg_img.resize((350, 200))
        selecionar_bg_photo = ImageTk.PhotoImage(selecionar_bg_img)
        bg_label = tk.Label(janela_selecionar_perfil, image=selecionar_bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = selecionar_bg_photo

        tk.Label(janela_selecionar_perfil, text="Selecione o perfil:", font=("Arial", 12)).pack(pady=20)
        var_perfil = tk.StringVar(janela_selecionar_perfil)
        var_perfil.set(perfil_ativo)
        option_menu = tk.OptionMenu(janela_selecionar_perfil, var_perfil, *perfis.keys())
        option_menu.pack(pady=10)
        tk.Button(janela_selecionar_perfil, text="Aplicar", command=aplicar_e_fechar).pack(pady=20)
        def on_close():
            nonlocal janela_selecionar_perfil
            janela_selecionar_perfil.destroy()
            janela_selecionar_perfil = None
        janela_selecionar_perfil.protocol("WM_DELETE_WINDOW", on_close)

    def criar_perfil():
        nonlocal janela_criar_perfil
        if janela_criar_perfil is not None and janela_criar_perfil.winfo_exists():
            janela_criar_perfil.lift()
            return
        def criar_e_fechar():
            nonlocal janela_criar_perfil
            nome = entry_novo.get()
            if nome and nome not in perfis:
                salvar_perfil_atual(nome)
                aplicar_perfil(nome)
                atualizar_perfil_label()
                print(f"Perfil criado: {nome}")
                janela_criar_perfil.destroy()
                janela_criar_perfil = None
        janela_criar_perfil = tk.Toplevel(root)
        janela_criar_perfil.title("Criar Perfil")
        janela_criar_perfil.geometry("350x200")
        janela_criar_perfil.resizable(False, False)
        janela_criar_perfil.iconphoto(True, icon_photo)
        perfil_bg_img = Image.open(resource_path("perfiltela.png"))
        perfil_bg_img = perfil_bg_img.resize((350, 200))
        perfil_bg_photo = ImageTk.PhotoImage(perfil_bg_img)
        bg_label = tk.Label(janela_criar_perfil, image=perfil_bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = perfil_bg_photo
        tk.Label(janela_criar_perfil, text="Nome do novo perfil:", font=("Arial", 12)).pack(pady=20)
        entry_novo = tk.Entry(janela_criar_perfil, font=("Arial", 14))
        entry_novo.pack(pady=10)
        tk.Button(janela_criar_perfil, text="Criar", command=criar_e_fechar, font=("Arial", 12)).pack(pady=20)
        def on_close():
            nonlocal janela_criar_perfil
            janela_criar_perfil.destroy()
            janela_criar_perfil = None
        janela_criar_perfil.protocol("WM_DELETE_WINDOW", on_close)

    def excluir_perfil_ui():
        nonlocal janela_excluir_perfil
        if janela_excluir_perfil is not None and janela_excluir_perfil.winfo_exists():
            janela_excluir_perfil.lift()
            return
        def excluir_e_fechar():
            nonlocal janela_excluir_perfil
            nome = var_excluir.get()
            if nome in perfis and nome != "default":
                excluir_perfil(nome)
                print(f"Perfil excluído: {nome}")   # <-- log aqui
                if perfil_ativo == nome:
                    aplicar_perfil("default")
                    atualizar_perfil_label()
                janela_excluir_perfil.destroy()
                janela_excluir_perfil = None
        janela_excluir_perfil = tk.Toplevel(root)
        janela_excluir_perfil.title("Excluir Perfil")
        janela_excluir_perfil.geometry("350x200")
        janela_excluir_perfil.resizable(False, False)
        janela_excluir_perfil.iconphoto(True, icon_photo)

        # Adiciona a imagem de fundo
        excluir_bg_img = Image.open(resource_path("excluir.jpg"))
        excluir_bg_img = excluir_bg_img.resize((350, 200))
        excluir_bg_photo = ImageTk.PhotoImage(excluir_bg_img)
        bg_label = tk.Label(janela_excluir_perfil, image=excluir_bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = excluir_bg_photo

        tk.Label(janela_excluir_perfil, text="Selecione o perfil para excluir:").pack(pady=20)
        perfis_excluiveis = [p for p in perfis.keys() if p != "default"]
        if not perfis_excluiveis:
            tk.Label(janela_excluir_perfil, text="Nenhum perfil para excluir.").pack(pady=10)
            return
        var_excluir = tk.StringVar(janela_excluir_perfil)
        var_excluir.set(perfis_excluiveis[0])
        option_menu = tk.OptionMenu(janela_excluir_perfil, var_excluir, *perfis_excluiveis)
        option_menu.pack(pady=10)
        tk.Button(janela_excluir_perfil, text="Excluir", command=excluir_e_fechar, font=("Arial", 12)).pack(pady=20)
        def on_close():
            nonlocal janela_excluir_perfil
            janela_excluir_perfil.destroy()
            janela_excluir_perfil = None
        janela_excluir_perfil.protocol("WM_DELETE_WINDOW", on_close)

    button_combo = tk.Button(
        root,
        text="Combo",
        font=("Arial", 14),
        bg="black",
        fg="white",
        command=open_janelacombo,
        relief="groove",
        borderwidth=5
    )
    button_combo.place(relx=0.3, rely=0.5, anchor="center")

    button_activation = tk.Button(
        root,
        text="Desligado",
        font=("Arial", 14),
        bg="red",
        fg="white",
        command=toggle_activation,
        relief="groove",
        borderwidth=5
    )
    button_activation.place(relx=0.7, rely=0.5, anchor="center")

    # Alinhe todos os botões na mesma linha (por exemplo, rely=0.8)
    tk.Button(root, text="👤 Criar Perfil", command=criar_perfil).place(relx=0.2, rely=0.8, anchor="center")
    tk.Button(root, text="📁 Selecionar Perfil", command=selecionar_perfil).place(relx=0.5, rely=0.8, anchor="center")
    tk.Button(root, text="🗑️ Excluir Perfil", command=excluir_perfil_ui).place(relx=0.8, rely=0.8, anchor="center")

# ========== MINI OVERLAY ==========
    # Funções de minimizar/restaurar/arrastar
    def minimizar_personalizado(event=None):
        try:
            if root.state() == "iconic":
                root.withdraw()
                mini.deiconify()
                mini.lift()
                mini.attributes("-topmost", True)
        except Exception as e:
            print(f"Falha ao minimizar personalizado: {e}")

    def restaurar():
        try:
            mini.withdraw()
            root.deiconify()
            root.state("normal")
            root.lift()
            root.attributes("-topmost", True)
            root.after(100, lambda: root.attributes("-topmost", False))
        except Exception as e:
            print(f"Falha ao restaurar: {e}")

    _drag_data = {"x": 0, "y": 0}
    def _start_move(e):
        _drag_data["x"] = e.x
        _drag_data["y"] = e.y

    def _do_move(e):
        dx = e.x - _drag_data["x"]
        dy = e.y - _drag_data["y"]
        x = mini.winfo_x() + dx
        y = mini.winfo_y() + dy
        mini.geometry(f"+{x}+{y}")

    # Janela mini (sempre no topo, sem borda)
    mini = tk.Toplevel(root)
    mini.withdraw()
    mini.overrideredirect(True)
    mini.attributes("-topmost", True)
    mini.geometry("160x80+1200+680")  # aumentei altura p/ caber o círculo
    mini.configure(bg="#1e293b")      # fundo azul escuro elegante
    mini.attributes("-alpha", 0.9)    # semi-transparente (glass effect)

    # fundo arredondado fake
    bg = tk.Canvas(mini, width=140, height=80, bg="#1e293b", highlightthickness=0)
    bg.pack(fill="both", expand=True)

    # Label no topo
    lbl = tk.Label(mini, text=f"LukzTools ({perfil_ativo})",
                   bg="#1e293b", fg="white", font=("Arial", 10, "bold"))
    lbl.place(relx=0.5, rely=0.25, anchor="center")

    # Botão circular
    circle_btn = tk.Canvas(mini, width=40, height=40, bg="#1e293b", highlightthickness=0)
    circle_btn.place(relx=0.5, rely=0.7, anchor="center")

    circle_btn.create_oval(2, 2, 38, 38, fill="#3874d4", outline="")  # círculo azul
    circle_btn.create_text(20, 20, text="🔼", fill="white", font=("Arial", 14, "bold"))

    def on_restore(event=None):
        restaurar()

    circle_btn.bind("<Button-1>", on_restore)

    # mover mini com o mouse
    def _start_move(event):
        mini.x = event.x
        mini.y = event.y

    def _do_move(event):
        x = mini.winfo_x() + (event.x - mini.x)
        y = mini.winfo_y() + (event.y - mini.y)
        mini.geometry(f"+{x}+{y}")

    mini.bind("<ButtonPress-1>", _start_move)
    mini.bind("<B1-Motion>", _do_move)
    
    
    # --- Função para atualizar o nome dinamicamente ---

    def atualizar_mini_label():
        global lbl
        try:
            if lbl is not None:
                lbl.config(text=f"LukzTools ({perfil_ativo})")
        except Exception as e:
            print(f"Não consegui atualizar o nome na mini: {e}")
        
        
    # Intercepta minimizar da janela principal
    def _on_unmap(e):
        root.after(10, minimizar_personalizado)
    root.bind("<Unmap>", _on_unmap)
    
    # ==================================

    root.mainloop()

if __name__ == "__main__":
    main()