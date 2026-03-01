import json
import os
import random
import keyboard
import combo
import config_window
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import threading
import pyautogui as py
import time
import shutil
import cv2
import numpy as np
import mss
import ctypes

import sys, os

lbl = None  # referência global para o label da mini
update_overlay_status = None  # referência global para atualizar o status do overlay
update_overlay_label = None  # referência global para atualizar o label do overlay
update_overlay_scan = None  # referência global para atualizar pokeball do scan
update_overlay_bot = None  # referência global para atualizar indicador BOT no overlay

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
revive_delay = "0.5"

# Hunt attacks: lista dinâmica [{"key": "q", "delay": 0.5, "type": "atk"}, ...]
hunt_attacks = []

# Nightmare attacks: lista de dicts [{"key1": "alt", "key2": "1", "delay": 0.5}, ...]
nightmare_attacks = []

# Modo de combo ativo: "HUNT NORMAL" ou "NIGHTMARE"
combo_mode_active = "HUNT NORMAL"

# ---- Verificação de Batalha (battle check) ----
# Região da tela onde fica o painel de batalha: (x1, y1, x2, y2)
battle_check_region = None     # None = não configurado
BATTLE_REF_FILE = os.path.join("battle", "battle_empty_ref.png")  # imagem de referência "sem inimigos"
battle_check_enabled = True    # liga/desliga a verificação

# ---- Sistema de Captura (gavetas) ----
# Lista de gavetas: [{"nome": "Pikachu", "ativo": False}, ...]
captura_gavetas = []
captura_modo_ativo = False
captura_scan_habilitado = False  # Botao ligar/desligar: G so funciona se True
captura_thread_scan = None
CAPTURA_DIR = "captura"

# ---- captura da posição (modo configuração) ----
capturando = False
captura_thread = None

# ---- captura battle region (modo configuração separado) ----
capturando_battle = False
captura_battle_thread = None

# Variável global para controlar o estado do combo
running = False
combo_active = False  # Variável para controlar o estado do botão "Desligado"

# ---- Master switch (bot ligado/desligado) ----
bot_active = False
bot_hotkey = "F1"  # hotkey global para ligar/desligar o bot
update_bot_indicator = None  # callback UI para atualizar indicador

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
    global revive_key, revive_delay
    global pokestop_delay, pokemedi_delay, pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5
    global pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12, combo_start_key, lbl
    global nightmare_attacks, hunt_attacks, combo_mode_active
    global bot_hotkey
    global battle_check_region

    perfil = perfis.get(nome, {})
    pokestop_key = perfil.get("pokestop_key", "")
    pokemedi_key = perfil.get("pokemedi_key", "")
    revive_key = perfil.get("revive_key", "")
    revive_delay = perfil.get("revive_delay", "0.5")
    pokestop_delay = perfil.get("pokestop_delay", "")
    pokemedi_delay = perfil.get("pokemedi_delay", "")
    combo_start_key = perfil.get("combo_start_key", "")

    # Carrega hunt_attacks (lista dinâmica) — compatibilidade com formato antigo key1-key12
    hunt_attacks = perfil.get("hunt_attacks", [])
    if not hunt_attacks:
        # Migração: reconstrói a partir de pokeattack_key1..12
        old_keys = [perfil.get(f"pokeattack_key{i}", "") for i in range(1, 13)]
        old_delays = [perfil.get(f"pokeattack_delay{i}", 0.5) for i in range(1, 13)]
        for k, d in zip(old_keys, old_delays):
            if k:
                hunt_attacks.append({"key": k, "delay": d, "type": "atk"})

    # Mantém globals antigos sincronizados (para código legado)
    for i in range(1, 13):
        globals()[f"pokeattack_key{i}"] = hunt_attacks[i-1]["key"] if i-1 < len(hunt_attacks) else ""
        globals()[f"pokeattack_delay{i}"] = hunt_attacks[i-1]["delay"] if i-1 < len(hunt_attacks) else 0.5

    nightmare_attacks = perfil.get("nightmare_attacks", [])
    combo_mode_active = perfil.get("combo_mode_active", "HUNT NORMAL")
    bot_hotkey = perfil.get("bot_hotkey", "F1")
    # Restaura posições do revive/center salvos no perfil
    saved_poke = perfil.get("pos_poke", None)
    if saved_poke:
        combo.set_pos_poke(saved_poke[0], saved_poke[1])
    saved_center = perfil.get("pos_center", None)
    if saved_center:
        combo.set_center(saved_center[0], saved_center[1])
    # Restaura região de battle check
    saved_battle = perfil.get("battle_check_region", None)
    if saved_battle and len(saved_battle) == 4:
        battle_check_region = tuple(saved_battle)
    else:
        battle_check_region = None
    perfil_ativo = nome
    try:
        if update_overlay_label is not None:
            update_overlay_label()
    except Exception as e:
        print(f"Não consegui atualizar o nome na mini: {e}")
    
def salvar_perfil_atual(nome):
    perfis[nome] = {
        "pokestop_key": pokestop_key,
        "pokemedi_key": pokemedi_key,
        "revive_key": revive_key,
        "revive_delay": revive_delay,
        "pokestop_delay": pokestop_delay,
        "pokemedi_delay": pokemedi_delay,
        "combo_start_key": combo_start_key,
        "hunt_attacks": hunt_attacks,
        "nightmare_attacks": nightmare_attacks,
        "combo_mode_active": combo_mode_active,
        "pos_poke": list(combo.pos_poke),
        "pos_center": list(combo.pos_center),
        "bot_hotkey": bot_hotkey,
        "battle_check_region": list(battle_check_region) if battle_check_region else None
    }
    salvar_perfis()

def excluir_perfil(nome):
    if nome in perfis and nome != "default":
        del perfis[nome]
        salvar_perfis()

combo_start_key = ""  # Defina a tecla padrão ou carregue do perfil

def has_enemies():
    """
    Verifica se há inimigos na tela comparando a região de batalha
    com a referência de 'sem inimigos'.
    Retorna True se há inimigos, False se não há.
    Se battle check não configurado, retorna True (assume que tem).
    """
    global battle_check_region
    if not battle_check_enabled:
        return True  # check desabilitado, assume que tem inimigo
    if battle_check_region is None:
        print("⚠ Battle check NÃO configurado! Vá em Ajustes → Ativar Captura → B + N")
        return True  # não configurado, assume que tem
    ref_path = resource_path(BATTLE_REF_FILE)
    if not os.path.exists(ref_path):
        print(f"⚠ Imagem de referência não encontrada: {ref_path}")
        return True  # sem referência, assume que tem

    try:
        ref_img = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
        if ref_img is None:
            print("⚠ Não conseguiu ler imagem de referência!")
            return True
        x1, y1, x2, y2 = battle_check_region
        with mss.mss() as sct:
            monitor = {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}
            raw = sct.grab(monitor)
            frame = np.array(raw)  # BGRA numpy array
            current = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
        # Redimensiona se tamanhos divergem
        if current.shape != ref_img.shape:
            current = cv2.resize(current, (ref_img.shape[1], ref_img.shape[0]))
        # Compara pixel a pixel: conta quantos pixels mudaram significativamente
        diff = cv2.absdiff(current, ref_img)
        # Pixels com diferença > 25 de intensidade contam como "mudados"
        changed = np.count_nonzero(diff > 25)
        total = diff.size
        change_pct = changed / total if total > 0 else 0
        print(f"⚔ Battle check: {change_pct:.1%} pixels alterados (≥2% = tem inimigo)")
        if change_pct < 0.02:
            # Quase idêntico ao vazio → SEM inimigos
            return False
        else:
            # Diferença significativa → TEM inimigos
            return True
    except Exception as e:
        print(f"⚠ Erro battle check: {e}")
        return True  # em caso de erro, assume que tem

def start_combo():
    if not bot_active:
        print("⚠ Bot desligado! Combo não executa.")
        return
    if combo_active:
        # Verifica se tem inimigos antes de combar
        enemies = has_enemies()
        if not enemies:
            print("🚫 Nenhum pokémon à vista! Combo cancelado.")
            return
        print("⚔ Inimigos detectados! Executando combo...")
        if combo_mode_active == "NIGHTMARE":
            combo.combo_nightmare(nightmare_attacks, should_continue=has_enemies)
            print("Combo Nightmare executado!")
        else:
            combo.combo_hunt_dynamic(hunt_attacks, should_continue=has_enemies)
            print("Combo Hunt Normal executado!")
    else:
        print("Combo está desligado, não executa!")

def toggle_bot():
    """Liga/desliga o bot inteiro (master switch)."""
    global bot_active, combo_active, captura_modo_ativo, captura_scan_habilitado
    bot_active = not bot_active
    if not bot_active:
        # Desativar tudo quando desligar o bot
        if combo_active:
            combo_active = False
            try:
                keyboard.remove_hotkey(combo_start_key)
            except Exception:
                pass
            print("Combo desativado (bot desligado)")
            try: update_overlay_status()
            except: pass
        if captura_modo_ativo or captura_scan_habilitado:
            captura_modo_ativo = False
            captura_scan_habilitado = False
            try:
                if update_overlay_scan: update_overlay_scan()
            except Exception:
                pass
            print("Scan de captura desligado (bot desligado)")
    state = "ON" if bot_active else "OFF"
    print(f"🤖 Bot {state}")
    try:
        if update_bot_indicator:
            update_bot_indicator()
    except Exception:
        pass
    try:
        if update_overlay_bot:
            update_overlay_bot()
    except Exception:
        pass

def toggle_activation():
    global combo_active
    if not bot_active:
        print("⚠ Bot desligado! Ligue primeiro com a hotkey global.")
        return
    if combo_active:
        combo_active = False
        keyboard.remove_hotkey(combo_start_key)
        print('Combo desativado')
        try: update_overlay_status()
        except: pass
    else:
        combo_active = True
        keyboard.add_hotkey(combo_start_key, start_combo)
        print('Combo ativado')
        try: update_overlay_status()
        except: pass

def _loop_captura():
    """Loop que espera teclas de configuração: H=poke, J=center."""
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
            # Salva no perfil automaticamente
            salvar_perfil_atual(perfil_ativo)
            print(f"pos_poke salvo no perfil '{perfil_ativo}'")

        elif key.name == 'j':  # salvar center
            x, y = py.position()
            combo.set_center(x, y)
            print(f"center atualizado: ({x}, {y})")
            # Salva no perfil automaticamente
            salvar_perfil_atual(perfil_ativo)
            print(f"pos_center salvo no perfil '{perfil_ativo}'")

def _loop_battle_captura():
    """Loop que espera teclas de configuração: B=top-left, N=bottom-right do painel Batalha."""
    global capturando_battle, battle_check_region
    print("⚔ Modo captura BATTLE ativado — aperte 'B' no canto superior-esquerdo, 'N' no canto inferior-direito.")
    while capturando_battle:
        key = keyboard.read_event(suppress=True)
        if not capturando_battle:
            break

        if key.event_type != keyboard.KEY_DOWN:
            continue

        if key.name == 'b':  # salvar canto superior-esquerdo da região de batalha
            x, y = py.position()
            if battle_check_region is None:
                battle_check_region = (x, y, x + 100, y + 100)
            else:
                battle_check_region = (x, y, battle_check_region[2], battle_check_region[3])
            print(f"⚔ Battle CANTO 1 (top-left): ({x}, {y})")
            print(f"  Agora aperte 'N' no canto inferior-direito da janela Batalha.")

        elif key.name == 'n':  # salvar canto inferior-direito + capturar referência
            x, y = py.position()
            if battle_check_region is None:
                print("⚠ Aperte 'B' primeiro para marcar o canto superior-esquerdo!")
            else:
                battle_check_region = (battle_check_region[0], battle_check_region[1], x, y)
                print(f"⚔ Battle CANTO 2 (bottom-right): ({x}, {y})")
                print(f"  Região: {battle_check_region}")
                # Captura referência de "sem inimigos" agora
                try:
                    x1, y1, x2, y2 = battle_check_region
                    w = x2 - x1
                    h = y2 - y1
                    if w <= 0 or h <= 0:
                        print(f"⚠ Região inválida! w={w}, h={h}. Verifique B e N.")
                    else:
                        with mss.mss() as sct:
                            monitor = {"left": x1, "top": y1, "width": w, "height": h}
                            raw = sct.grab(monitor)
                            frame = np.array(raw)
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
                        ref_path = resource_path(BATTLE_REF_FILE)
                        os.makedirs(os.path.dirname(ref_path), exist_ok=True)
                        cv2.imwrite(ref_path, gray)
                        print(f"📸 Referência 'sem inimigos' salva: {ref_path} ({w}x{h})")
                except Exception as e:
                    print(f"⚠ Erro ao capturar referência: {e}")
                salvar_perfil_atual(perfil_ativo)
                print(f"Battle check salvo no perfil '{perfil_ativo}'")
                # Auto-desativa após configurar
                capturando_battle = False
                print("⚔ Modo captura BATTLE finalizado.")

def main():
    global button_combo, button_activation, perfil_label, lbl
    carregar_perfis()
    aplicar_perfil(perfil_ativo)

    root = tk.Tk()
    root.title("LuukzTools")
    root.geometry("440x680")
    root.resizable(False, False)
    root.configure(bg="#dc2626")

    # Carrega o ícone
    icon_img = Image.open(resource_path("logo.jpg"))
    icon_img = icon_img.resize((32, 32))
    icon_photo = ImageTk.PhotoImage(icon_img)
    root.iconphoto(True, icon_photo)

    # ═══════════════════════════════════════════
    # 🔴 POKÉDEX TOP — INDICATORS BAR
    # ═══════════════════════════════════════════

    top_bar = tk.Frame(root, bg="#dc2626", height=52)
    top_bar.pack(fill="x", padx=8, pady=(8, 0))
    top_bar.pack_propagate(False)

    # Grande LED azul com anel branco
    led_big = tk.Canvas(top_bar, width=48, height=48, bg="#dc2626", highlightthickness=0)
    led_big.pack(side="left", padx=(6, 10))
    # Anel branco externo
    led_big.create_oval(2, 2, 46, 46, fill="white", outline="#e0e0e0", width=2)
    # LED cyan interno com glow
    led_big_inner = led_big.create_oval(7, 7, 41, 41, fill="#22d3ee", outline="white", width=3)
    # Brilho/reflexo
    led_big.create_oval(14, 10, 28, 22, fill="#80eeff", outline="")

    # Pequenos LEDs (vermelho, amarelo, verde)
    small_leds = []
    for color, border in [("#ef4444", "#991b1b"), ("#facc15", "#a16207"), ("#22c55e", "#166534")]:
        led_sm = tk.Canvas(top_bar, width=12, height=12, bg="#dc2626", highlightthickness=0)
        led_sm.pack(side="left", padx=2, pady=16)
        oval_id = led_sm.create_oval(1, 1, 11, 11, fill=color, outline=border, width=1)
        small_leds.append((led_sm, oval_id))

    # Botão config no canto direito do top_bar
    btn_cfg_top = tk.Button(top_bar, text="\u2699", font=("Segoe UI Emoji", 16),
                            bg="#8b1115", fg="white", activebackground="#eab308",
                            activeforeground="black", bd=1, relief="solid",
                            highlightbackground="#991b1b", width=2, height=1,
                            cursor="hand2", command=lambda: abrir_configuracao())
    btn_cfg_top.pack(side="right", padx=8)

    # Borda inferior vermelha escura (separador sutil)
    tk.Frame(root, bg="#b91c1c", height=2).pack(fill="x", padx=8)

    # ═══════════════════════════════════════════
    # 📺 INNER SCREEN CONTAINER
    # ═══════════════════════════════════════════

    screen_border = tk.Frame(root, bg="#3f3f46", bd=0)
    screen_border.pack(fill="both", expand=True, padx=16, pady=(8, 6))

    screen = tk.Frame(screen_border, bg="#27272a")
    screen.pack(fill="both", expand=True, padx=4, pady=4)

    # Wrapper frames para alternar entre tela principal e config
    main_content_frame = tk.Frame(screen, bg="#27272a")
    main_content_frame.pack(fill="both", expand=True)
    config_content_frame = tk.Frame(screen, bg="#121214")
    # config_content_frame NÃO é packed inicialmente
    create_profile_frame = tk.Frame(screen, bg="#121214")
    # create_profile_frame NÃO é packed inicialmente
    select_profile_frame = tk.Frame(screen, bg="#121214")
    # select_profile_frame NÃO é packed inicialmente
    delete_profile_frame = tk.Frame(screen, bg="#121214")
    # delete_profile_frame NÃO é packed inicialmente
    combo_setup_frame = tk.Frame(screen, bg="#121214")
    # combo_setup_frame NÃO é packed inicialmente
    capture_setup_frame = tk.Frame(screen, bg="#121214")
    # capture_setup_frame NÃO é packed inicialmente

    # ── Profile Header ──
    perfil_header = tk.Frame(main_content_frame, bg="#27272a")
    perfil_header.pack(fill="x", padx=10, pady=(10, 4))

    # Linha superior: perfil label + BOT ON/OFF
    perfil_bar = tk.Frame(perfil_header, bg="#27272a")
    perfil_bar.pack(fill="x", padx=0, pady=(4, 4))

    # Lado esquerdo: Ⓡ PROFILE
    perfil_left = tk.Frame(perfil_bar, bg="#27272a")
    perfil_left.pack(side="left", padx=6)
    tk.Label(perfil_left, text="Ⓡ", font=("Consolas", 10),
             bg="#27272a", fg="#22d3ee").pack(side="left")
    perfil_label = tk.Label(perfil_left, text=f" {perfil_ativo.upper()}",
                            font=("Consolas", 11, "bold italic"),
                            fg="#22d3ee", bg="#27272a")
    perfil_label.pack(side="left")

    # Lado direito: BOT ON/OFF com dot piscante
    bot_indicator_frame = tk.Frame(perfil_bar, bg="#27272a")
    bot_indicator_frame.pack(side="right", padx=6)
    bot_dot_lbl = tk.Label(bot_indicator_frame, text="●", font=("Consolas", 7),
                           bg="#27272a", fg="#f87171")
    bot_dot_lbl.pack(side="left", padx=(0, 3))
    scan_status_lbl = tk.Label(bot_indicator_frame, text="BOT OFF",
                               font=("Consolas", 9, "bold"),
                               bg="#27272a", fg="#f87171")
    scan_status_lbl.pack(side="left")
    # Referência para update (mantém compatibilidade)
    scan_icon_lbl = bot_dot_lbl

    # Blinking do BOT indicator
    def _blink_bot_indicator():
        try:
            cur_fg = bot_dot_lbl.cget("fg")
            if bot_active:
                # Verde piscante
                new_fg = "#27272a" if cur_fg == "#34d399" else "#34d399"
                bot_dot_lbl.config(fg=new_fg)
            else:
                # Vermelho piscante
                new_fg = "#27272a" if cur_fg == "#f87171" else "#f87171"
                bot_dot_lbl.config(fg=new_fg)
        except Exception:
            pass
        root.after(600, _blink_bot_indicator)
    _blink_bot_indicator()

    # Separador
    tk.Frame(perfil_header, bg="#3f3f46", height=1).pack(fill="x", padx=4, pady=(0, 4))

    # Linha de botões de perfil: +  ▷  🗑
    perfil_btns_row = tk.Frame(perfil_header, bg="#27272a")
    perfil_btns_row.pack(fill="x", padx=4, pady=(0, 6))

    for txt, cmd, act_bg in [("＋", lambda: criar_perfil(), "#eab308"), ("▷", lambda: selecionar_perfil(), "#3b82f6"), ("🗑", lambda: excluir_perfil_ui(), "#ef4444")]:
        _bf = tk.Frame(perfil_btns_row, bg="#3f3f46")
        _bf.pack(side="left", expand=True, fill="x", padx=2)
        _b = tk.Button(_bf, text=txt, font=("Consolas", 11, "bold"),
                       bg="#27272a", fg="#a1a1aa", activebackground=act_bg,
                       activeforeground="black" if act_bg == "#eab308" else "white",
                       bd=0, pady=4, cursor="hand2",
                       command=cmd)
        _b.pack(fill="x", padx=1, pady=1)

    # Log mini (hidden - will use full log)
    log_history = []

    # Invisible mini log widget (needed for TextRedirector compatibility)
    _log_mini_frame = tk.Frame(main_content_frame, bg="#27272a", height=1)
    log_text = tk.Text(_log_mini_frame, height=1, width=1, state="disabled",
                       bg="#27272a", fg="#27272a", font=("Consolas", 1),
                       bd=0, relief="flat")
    log_text.pack()

    def abrir_log_completo():
        log_win = tk.Toplevel(root)
        log_win.title("📋 Log Completo")
        log_win.geometry("520x400")
        log_win.resizable(True, True)
        log_win.configure(bg="#1e1e2e")

        header = tk.Frame(log_win, bg="#1e1e2e")
        header.pack(fill="x", padx=10, pady=(10, 5))
        tk.Label(header, text="📋 Log de Eventos", font=("Consolas", 12, "bold"),
                 fg="#00d4ff", bg="#1e1e2e").pack(side="left")

        def limpar_log():
            log_history.clear()
            log_area.config(state="normal")
            log_area.delete("1.0", tk.END)
            log_area.config(state="disabled")

        tk.Button(header, text="🗑 Limpar", font=("Consolas", 9), bg="#ff3b3b",
                  fg="white", bd=0, padx=8, pady=2, command=limpar_log).pack(side="right")

        log_area = tk.Text(log_win, wrap="word", state="disabled",
                           bg="#12121a", fg="#c0c0c0", font=("Consolas", 9),
                           insertbackground="white", selectbackground="#7c3aed",
                           bd=0, padx=8, pady=8)
        log_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tag para colorir erros
        log_area.tag_config("error", foreground="#ff5555")
        log_area.tag_config("info", foreground="#00ff88")

        # Preenche com histórico
        log_area.config(state="normal")
        for entry in log_history:
            tag = "error" if any(w in entry.lower() for w in ["erro", "error", "falha", "exception"]) else "info"
            log_area.insert(tk.END, entry + "\n", tag)
        log_area.see(tk.END)
        log_area.config(state="disabled")

        # Atualiza em tempo real
        def refresh_log():
            if not log_win.winfo_exists():
                return
            log_area.config(state="normal")
            current_lines = int(log_area.index("end-1c").split(".")[0])
            # Insere apenas linhas novas
            for entry in log_history[current_lines - 1:]:
                tag = "error" if any(w in entry.lower() for w in ["erro", "error", "falha", "exception"]) else "info"
                log_area.insert(tk.END, entry + "\n", tag)
            log_area.see(tk.END)
            log_area.config(state="disabled")
            log_win.after(500, refresh_log)

        refresh_log()

    # Click no BOT indicator abre log
    bot_indicator_frame.bind("<Button-1>", lambda e: abrir_log_completo())
    for child in bot_indicator_frame.winfo_children():
        child.bind("<Button-1>", lambda e: abrir_log_completo())

    def log_message(msg):
        log_history.append(msg)
        # Feed hidden mini widget (compatibility)
        log_text.config(state="normal")
        log_text.delete("1.0", tk.END)
        log_text.insert(tk.END, msg + "\n")
        log_text.config(state="disabled")
        # Feed visible log panel
        try:
            log_panel_text.config(state="normal")
            color_tag = "err" if any(w in msg.lower() for w in ["erro", "error", "falha"]) else "ok"
            log_panel_text.insert(tk.END, msg + "\n", color_tag)
            log_panel_text.see(tk.END)
            log_panel_text.config(state="disabled")
        except Exception:
            pass

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
    
    _janela_cfg_ref = [None]
    _config_built = [False]
    _config_widgets = {}  # para guardar referências dos widgets de config
    _capturing_hotkey = [False]

    def _on_hotkey_changed(old_key, new_key):
        """Re-registra a hotkey global do bot."""
        global bot_hotkey
        try:
            keyboard.remove_hotkey(old_key)
        except Exception:
            pass
        bot_hotkey = new_key
        keyboard.add_hotkey(new_key, toggle_bot, suppress=False)

    def _voltar_da_configuracao():
        """Volta da tela de config para a tela principal."""
        config_content_frame.pack_forget()
        main_content_frame.pack(fill="both", expand=True)

    def _build_config_ui():
        """Constrói a UI de configuração dentro de config_content_frame (uma vez só)."""
        if _config_built[0]:
            return

        _BG = "#121214"
        _CARD = "#1a1a1e"
        _BORDER = "#27272a"
        _TEXT = "#d4d4d8"
        _DIM = "#71717a"
        _CYAN = "#22d3ee"
        _YELLOW = "#eab308"
        _GREEN = "#16a34a"
        _RED = "#dc2626"

        # ── HEADER ──
        header = tk.Frame(config_content_frame, bg=_BG)
        header.pack(fill="x", padx=16, pady=(14, 0))

        btn_voltar = tk.Button(
            header, text="❮  VOLTAR", font=("Consolas", 9, "bold"),
            bg=_BG, fg=_DIM, bd=0, cursor="hand2",
            activebackground=_BG, activeforeground="white",
            command=_voltar_da_configuracao
        )
        btn_voltar.pack(side="left")

        title_frame = tk.Frame(header, bg=_BG)
        title_frame.pack(side="right")
        tk.Label(title_frame, text="⚙", font=("Segoe UI Emoji", 12),
                 bg=_BG, fg=_CYAN).pack(side="left", padx=(0, 4))
        tk.Label(title_frame, text="AJUSTES", font=("Consolas", 13, "bold italic"),
                 bg=_BG, fg=_CYAN).pack(side="left")

        tk.Frame(config_content_frame, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── SCROLL AREA ──
        _cfg_scroll_outer = tk.Frame(config_content_frame, bg=_BG)
        _cfg_scroll_outer.pack(fill="both", expand=True)

        _cfg_canvas = tk.Canvas(_cfg_scroll_outer, bg=_BG, highlightthickness=0)
        _cfg_scrollbar = tk.Scrollbar(_cfg_scroll_outer, orient="vertical", command=_cfg_canvas.yview)
        content = tk.Frame(_cfg_canvas, bg=_BG)

        content.bind("<Configure>",
                      lambda e: _cfg_canvas.configure(scrollregion=_cfg_canvas.bbox("all")))
        _cfg_canvas.create_window((0, 0), window=content, anchor="nw")
        _cfg_canvas.configure(yscrollcommand=_cfg_scrollbar.set)

        _cfg_canvas.pack(side="left", fill="both", expand=True)
        _cfg_scrollbar.pack(side="right", fill="y")

        def _cfg_resize(event):
            _cfg_canvas.itemconfig(_cfg_canvas.find_all()[0], width=event.width)
        _cfg_canvas.bind("<Configure>", _cfg_resize)

        def _cfg_mousewheel(event):
            _cfg_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        _cfg_canvas.bind_all("<MouseWheel>", _cfg_mousewheel)

        # ═══ SEÇÃO 1: HOTKEY GLOBAL ═══
        _cfg_section_label(content, "⌨  HOTKEY GLOBAL", _YELLOW)

        hotkey_card = tk.Frame(content, bg=_CARD, highlightbackground=_BORDER,
                               highlightthickness=1)
        hotkey_card.pack(fill="x", pady=(6, 0))

        hotkey_inner = tk.Frame(hotkey_card, bg=_CARD)
        hotkey_inner.pack(fill="x", padx=12, pady=10)

        lbl_frame = tk.Frame(hotkey_inner, bg=_CARD)
        lbl_frame.pack(side="left")
        tk.Label(lbl_frame, text="LIGAR / DESLIGAR BOT",
                 font=("Consolas", 9, "bold"), bg=_CARD, fg="white").pack(anchor="w")
        tk.Label(lbl_frame, text="ALTERNA ESTADO DO PROGRAMA",
                 font=("Consolas", 7), bg=_CARD, fg=_DIM).pack(anchor="w")

        hotkey_var = tk.StringVar(value=bot_hotkey)
        _config_widgets["hotkey_var"] = hotkey_var

        def _start_hotkey_capture():
            if _capturing_hotkey[0]:
                return
            _capturing_hotkey[0] = True
            hotkey_var.set("...")
            btn_hotkey.config(fg="#ef4444")
            def on_key(event):
                if event.event_type == keyboard.KEY_DOWN:
                    hotkey_var.set(event.name.upper())
                    btn_hotkey.config(fg=_YELLOW)
                    _capturing_hotkey[0] = False
                    keyboard.unhook(hook_ref[0])
            hook_ref = [keyboard.hook(on_key)]

        btn_hotkey = tk.Button(
            hotkey_inner, textvariable=hotkey_var,
            font=("Consolas", 11, "bold"), bg="#18181b", fg=_YELLOW,
            bd=1, relief="solid", padx=12, pady=4, cursor="hand2",
            activebackground="#27272a", activeforeground=_YELLOW,
            command=_start_hotkey_capture
        )
        btn_hotkey.pack(side="right")

        # ═══ SEÇÃO 2: CAPTURA REVIVE & POS ═══
        _cfg_section_label(content, "◎  CAPTURA REVIVE & POS", _CYAN)

        cap_card = tk.Frame(content, bg=_CARD, highlightbackground=_BORDER,
                            highlightthickness=1)
        cap_card.pack(fill="x", pady=(6, 0))

        info_frame = tk.Frame(cap_card, bg="#0a0a0c", highlightbackground=_BORDER,
                              highlightthickness=1)
        info_frame.pack(fill="x", padx=10, pady=(10, 6))

        info_inner = tk.Frame(info_frame, bg="#0a0a0c")
        info_inner.pack(fill="x", padx=8, pady=8)
        tk.Label(info_inner, text="ℹ", font=("Segoe UI Emoji", 11),
                 bg="#0a0a0c", fg=_CYAN).pack(side="left", padx=(0, 8))
        tk.Label(info_inner,
                 text="Clique em ATIVAR, pressione 'H' na foto do\npokemon e 'J' perto do seu personagem para\nsalvar o clique.",
                 font=("Consolas", 8), bg="#0a0a0c", fg="#a1a1aa",
                 justify="left").pack(side="left")

        status_var = tk.StringVar(value="DESATIVADO")
        _config_widgets["status_var"] = status_var

        def _start_captura_cfg():
            if capturando:
                return
            _set_capturando(True)
            status_var.set("AGUARDANDO TECLAS...")
            print("Modo captura iniciado — aperte 'h' para revive, 'j' para center.")

        def _stop_captura_cfg():
            if not capturando:
                return
            _set_capturando(False)
            status_var.set("DESATIVADO")
            print("Modo captura finalizado.")

        btn_ativar = tk.Button(
            cap_card, text="◎  ATIVAR CAPTURA (H=POKE, J=CENTER)",
            font=("Consolas", 9, "bold"), bg="#27272a", fg="white",
            activebackground=_CYAN, activeforeground="black",
            bd=0, pady=8, cursor="hand2",
            command=_start_captura_cfg
        )
        btn_ativar.pack(fill="x", padx=10, pady=(8, 4))

        _des_frame = tk.Frame(cap_card, bg=_RED, bd=0, highlightthickness=0)
        _des_frame.pack(fill="x", padx=10, pady=(0, 8))
        btn_desativar = tk.Button(
            _des_frame, text="⚡  DESATIVAR CAPTURA",
            font=("Consolas", 9, "bold"), bg="#0a0a0c", fg=_RED,
            activebackground="#1a0505",
            bd=0, relief="flat", pady=6, cursor="hand2",
            highlightthickness=0,
            command=_stop_captura_cfg
        )
        btn_desativar.pack(fill="both", expand=True, padx=2, pady=2)

        status_frame = tk.Frame(cap_card, bg=_CARD)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))
        tk.Frame(status_frame, bg=_BORDER, height=1).pack(fill="x", pady=(0, 6))
        sf = tk.Frame(status_frame, bg=_CARD)
        sf.pack()
        tk.Label(sf, text="STATUS:", font=("Consolas", 8),
                 bg=_CARD, fg=_DIM).pack(side="left", padx=(0, 6))
        status_lbl = tk.Label(sf, textvariable=status_var,
                              font=("Consolas", 10, "bold italic"),
                              bg=_CARD, fg=_RED)
        status_lbl.pack(side="left")

        def _update_status_color(*_):
            val = status_var.get()
            status_lbl.config(fg=_RED if val == "DESATIVADO" else _GREEN)
        status_var.trace_add("write", _update_status_color)

        # ═══ SEÇÃO 3: CONFIGURAÇÃO BATTLE ═══
        _ORANGE = "#f97316"
        _cfg_section_label(content, "⚔  CONFIGURAÇÃO BATTLE", _ORANGE)

        battle_card = tk.Frame(content, bg=_CARD, highlightbackground=_BORDER,
                               highlightthickness=1)
        battle_card.pack(fill="x", pady=(6, 0))

        # Info box battle
        battle_info_frame = tk.Frame(battle_card, bg="#0a0a0c", highlightbackground=_BORDER,
                                     highlightthickness=1)
        battle_info_frame.pack(fill="x", padx=10, pady=(10, 6))

        battle_info_inner = tk.Frame(battle_info_frame, bg="#0a0a0c")
        battle_info_inner.pack(fill="x", padx=8, pady=8)
        tk.Label(battle_info_inner, text="⚔", font=("Segoe UI Emoji", 11),
                 bg="#0a0a0c", fg=_ORANGE).pack(side="left", padx=(0, 8))
        tk.Label(battle_info_inner,
                 text="SEM inimigos na tela, clique ATIVAR.\nAperte 'B' no canto top-left do painel\nBatalha e 'N' no canto bottom-right.",
                 font=("Consolas", 8), bg="#0a0a0c", fg="#a1a1aa",
                 justify="left").pack(side="left")

        # Status battle
        battle_status_var = tk.StringVar(value="NÃO CONFIGURADO" if battle_check_region is None else "CONFIGURADO ✅")
        _config_widgets["battle_status_var"] = battle_status_var

        def _start_battle_captura():
            global capturando_battle, captura_battle_thread
            if capturando_battle:
                return
            capturando_battle = True
            battle_status_var.set("AGUARDANDO B + N...")
            captura_battle_thread = threading.Thread(target=_loop_battle_captura_wrapper, daemon=True)
            captura_battle_thread.start()

        def _loop_battle_captura_wrapper():
            """Wrapper que chama o loop e atualiza status ao terminar."""
            _loop_battle_captura()
            try:
                if battle_check_region is not None:
                    battle_status_var.set("CONFIGURADO ✅")
                else:
                    battle_status_var.set("NÃO CONFIGURADO")
            except Exception:
                pass

        def _stop_battle_captura():
            global capturando_battle
            if not capturando_battle:
                return
            capturando_battle = False
            battle_status_var.set("CONFIGURADO ✅" if battle_check_region is not None else "NÃO CONFIGURADO")
            print("⚔ Modo captura BATTLE desativado.")

        btn_battle_ativar = tk.Button(
            battle_card, text="⚔  ATIVAR CAPTURA (B=TOP-LEFT, N=BOTTOM-RIGHT)",
            font=("Consolas", 8, "bold"), bg="#27272a", fg="white",
            activebackground=_ORANGE, activeforeground="black",
            bd=0, pady=8, cursor="hand2",
            command=_start_battle_captura
        )
        btn_battle_ativar.pack(fill="x", padx=10, pady=(8, 4))

        _battle_des_frame = tk.Frame(battle_card, bg=_ORANGE, bd=0, highlightthickness=0)
        _battle_des_frame.pack(fill="x", padx=10, pady=(0, 8))
        btn_battle_desativar = tk.Button(
            _battle_des_frame, text="⚡  DESATIVAR CAPTURA BATTLE",
            font=("Consolas", 9, "bold"), bg="#0a0a0c", fg=_ORANGE,
            activebackground="#1a0a05",
            bd=0, relief="flat", pady=6, cursor="hand2",
            highlightthickness=0,
            command=_stop_battle_captura
        )
        btn_battle_desativar.pack(fill="both", expand=True, padx=2, pady=2)

        # Status label battle
        battle_sf = tk.Frame(battle_card, bg=_CARD)
        battle_sf.pack(fill="x", padx=10, pady=(0, 10))
        tk.Frame(battle_sf, bg=_BORDER, height=1).pack(fill="x", pady=(0, 6))
        bsf = tk.Frame(battle_sf, bg=_CARD)
        bsf.pack()
        tk.Label(bsf, text="STATUS:", font=("Consolas", 8),
                 bg=_CARD, fg=_DIM).pack(side="left", padx=(0, 6))
        battle_status_lbl = tk.Label(bsf, textvariable=battle_status_var,
                                     font=("Consolas", 10, "bold italic"),
                                     bg=_CARD, fg=_ORANGE)
        battle_status_lbl.pack(side="left")

        def _update_battle_status_color(*_):
            val = battle_status_var.get()
            if "CONFIGURADO" in val and "NÃO" not in val:
                battle_status_lbl.config(fg=_GREEN)
            elif "AGUARDANDO" in val:
                battle_status_lbl.config(fg=_ORANGE)
            else:
                battle_status_lbl.config(fg=_RED)
        battle_status_var.trace_add("write", _update_battle_status_color)
        _update_battle_status_color()

        # ── FOOTER: SALVAR + RESET ──
        tk.Frame(config_content_frame, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(8, 0))

        footer = tk.Frame(config_content_frame, bg=_BG)
        footer.pack(fill="x", padx=16, pady=(8, 12))

        def _salvar_cfg():
            new_key = hotkey_var.get().strip()
            if not new_key or new_key == "...":
                return
            old_key = bot_hotkey
            _on_hotkey_changed(old_key, new_key)
            perfil = perfis.get(perfil_ativo, {})
            perfil["bot_hotkey"] = new_key
            perfis[perfil_ativo] = perfil
            salvar_perfis()
            print(f"✅ Configs salvas! Hotkey bot: {new_key}")

        btn_salvar = tk.Button(
            footer, text="💾  SALVAR CONFIGS",
            font=("Consolas", 10, "bold"), bg=_GREEN, fg="white",
            activebackground="#15803d", bd=0, pady=8, cursor="hand2",
            command=_salvar_cfg
        )
        btn_salvar.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def _reset_cfg():
            hotkey_var.set("F1")
            _stop_captura_cfg()

        btn_reset = tk.Button(
            footer, text="↻", font=("Consolas", 14, "bold"),
            bg="#27272a", fg=_DIM, activebackground="#3f3f46",
            bd=1, relief="solid", padx=8, pady=4, cursor="hand2",
            command=_reset_cfg
        )
        btn_reset.pack(side="right")

        # Speaker dots
        dots = tk.Frame(config_content_frame, bg=_BG)
        dots.pack(pady=(0, 6))
        for _ in range(3):
            tk.Canvas(dots, width=5, height=5, bg=_BG, highlightthickness=0)\
              .pack(side="left", padx=2)

        _config_built[0] = True

    def _cfg_section_label(parent, text, color):
        f = tk.Frame(parent, bg=parent.cget("bg"))
        f.pack(fill="x", pady=(12, 0))
        bar = tk.Frame(f, bg=color, width=3, height=16)
        bar.pack(side="left", padx=(0, 8))
        bar.pack_propagate(False)
        tk.Label(f, text=text, font=("Consolas", 9, "bold"),
                 bg=parent.cget("bg"), fg="#a1a1aa").pack(side="left")

    def abrir_configuracao():
        """Mostra a tela de configuração dentro da mesma janela."""
        _build_config_ui()
        # Atualiza hotkey_var com valor atual
        if "hotkey_var" in _config_widgets:
            _config_widgets["hotkey_var"].set(bot_hotkey)
        main_content_frame.pack_forget()
        config_content_frame.pack(fill="both", expand=True)

    # ═══════════════════════════════════════════════════════
    # ⚔ SETUP COMBO — tela inline
    # ═══════════════════════════════════════════════════════
    _combo_setup_built = [False]
    _combo_setup_widgets = {}

    def _voltar_do_combo_setup():
        """Volta da tela de setup combo para a tela principal."""
        combo_setup_frame.pack_forget()
        main_content_frame.pack(fill="both", expand=True)

    def _build_combo_setup_ui():
        """Constrói a UI de Setup Combo dentro de combo_setup_frame (uma vez só)."""
        if _combo_setup_built[0]:
            return

        _BG = "#121214"
        _CARD = "#1a1a1e"
        _BORDER = "#27272a"
        _DIM = "#71717a"
        _YELLOW = "#eab308"
        _GREEN = "#10b981"
        _RED = "#ef4444"
        _CYAN = "#22d3ee"
        _BLUE = "#3b82f6"
        _ORANGE = "#f97316"

        # Estado local
        attack_rows = []
        nightmare_rows = []
        combo_mode_var = [combo_mode_active]  # "HUNT NORMAL" ou "NIGHTMARE"
        plus_menu_visible = [False]

        # ── HEADER ──
        header = tk.Frame(combo_setup_frame, bg=_BG)
        header.pack(fill="x", padx=16, pady=(14, 0))

        btn_voltar = tk.Button(
            header, text="❮  VOLTAR", font=("Consolas", 9, "bold"),
            bg=_BG, fg=_DIM, bd=0, cursor="hand2",
            activebackground=_BG, activeforeground="white",
            command=_voltar_do_combo_setup
        )
        btn_voltar.pack(side="left")

        title_frame = tk.Frame(header, bg=_BG)
        title_frame.pack(side="right")
        tk.Label(title_frame, text="⚔", font=("Segoe UI Emoji", 12),
                 bg=_BG, fg=_YELLOW).pack(side="left", padx=(0, 4))
        tk.Label(title_frame, text="SETUP COMBO", font=("Consolas", 13, "bold italic"),
                 bg=_BG, fg=_YELLOW).pack(side="left")

        tk.Frame(combo_setup_frame, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── SCROLLABLE MAIN AREA ──
        scroll_outer = tk.Frame(combo_setup_frame, bg=_BG)
        scroll_outer.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        main_canvas = tk.Canvas(scroll_outer, bg=_BG, highlightthickness=0)
        main_scrollbar = tk.Scrollbar(scroll_outer, orient="vertical", command=main_canvas.yview)
        scroll_content = tk.Frame(main_canvas, bg=_BG)

        scroll_content.bind("<Configure>",
                            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")

        def _resize_scroll(event):
            main_canvas.itemconfig(main_canvas.find_all()[0], width=event.width)
        main_canvas.bind("<Configure>", _resize_scroll)

        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ════════════════════════════════════════
        # SEÇÃO 1: TECLAS DE SUPORTE
        # ════════════════════════════════════════
        support_card = tk.Frame(scroll_content, bg="#0d0d0f",
                                highlightbackground=_BORDER, highlightthickness=1)
        support_card.pack(fill="x", padx=16, pady=(10, 0))

        # — Combo Start —
        cs_frame = tk.Frame(support_card, bg="#0d0d0f")
        cs_frame.pack(fill="x", padx=12, pady=(10, 6))
        cs_left = tk.Frame(cs_frame, bg="#0d0d0f")
        cs_left.pack(side="left")
        tk.Label(cs_left, text="🎮", font=("Segoe UI Emoji", 10),
                 bg="#0d0d0f", fg=_YELLOW).pack(side="left", padx=(0, 6))
        tk.Label(cs_left, text="COMBO START", font=("Consolas", 9, "bold"),
                 bg="#0d0d0f", fg=_YELLOW).pack(side="left")
        entry_combo_start = tk.Entry(cs_frame, width=5, font=("Consolas", 10, "bold"),
                                     bg="#18181b", fg=_YELLOW, insertbackground=_YELLOW,
                                     bd=1, relief="solid", justify="center")
        entry_combo_start.pack(side="right", padx=(0, 4))
        _combo_setup_widgets["entry_combo_start"] = entry_combo_start

        tk.Frame(support_card, bg=_BORDER, height=1).pack(fill="x", padx=10, pady=4)

        # — Pokestop —
        ps_frame = tk.Frame(support_card, bg="#0d0d0f")
        ps_frame.pack(fill="x", padx=12, pady=(2, 4))
        ps_left = tk.Frame(ps_frame, bg="#0d0d0f")
        ps_left.pack(side="left")
        tk.Label(ps_left, text="📍", font=("Segoe UI Emoji", 10),
                 bg="#0d0d0f", fg=_RED).pack(side="left", padx=(0, 6))
        tk.Label(ps_left, text="POKESTOP", font=("Consolas", 9, "bold"),
                 bg="#0d0d0f", fg=_RED).pack(side="left")
        ps_right = tk.Frame(ps_frame, bg="#0d0d0f")
        ps_right.pack(side="right")
        entry_pokestop_delay = tk.Entry(ps_right, width=4, font=("Consolas", 10, "bold"),
                                        bg="#18181b", fg=_CYAN, insertbackground=_CYAN,
                                        bd=1, relief="solid", justify="center")
        entry_pokestop_delay.pack(side="right", padx=(4, 4))
        entry_pokestop_key = tk.Entry(ps_right, width=5, font=("Consolas", 10, "bold"),
                                      bg="#18181b", fg="white", insertbackground="white",
                                      bd=1, relief="solid", justify="center")
        entry_pokestop_key.pack(side="right", padx=(0, 4))
        _combo_setup_widgets["entry_pokestop_key"] = entry_pokestop_key
        _combo_setup_widgets["entry_pokestop_delay"] = entry_pokestop_delay

        # — Medicine —
        med_frame = tk.Frame(support_card, bg="#0d0d0f")
        med_frame.pack(fill="x", padx=12, pady=(2, 4))
        med_left = tk.Frame(med_frame, bg="#0d0d0f")
        med_left.pack(side="left")
        tk.Label(med_left, text="💊", font=("Segoe UI Emoji", 10),
                 bg="#0d0d0f", fg=_GREEN).pack(side="left", padx=(0, 6))
        tk.Label(med_left, text="MEDICINE", font=("Consolas", 9, "bold"),
                 bg="#0d0d0f", fg=_GREEN).pack(side="left")
        med_right = tk.Frame(med_frame, bg="#0d0d0f")
        med_right.pack(side="right")
        entry_medicine_delay = tk.Entry(med_right, width=4, font=("Consolas", 10, "bold"),
                                        bg="#18181b", fg=_CYAN, insertbackground=_CYAN,
                                        bd=1, relief="solid", justify="center")
        entry_medicine_delay.pack(side="right", padx=(4, 4))
        entry_medicine_key = tk.Entry(med_right, width=5, font=("Consolas", 10, "bold"),
                                      bg="#18181b", fg="white", insertbackground="white",
                                      bd=1, relief="solid", justify="center")
        entry_medicine_key.pack(side="right", padx=(0, 4))
        _combo_setup_widgets["entry_medicine_key"] = entry_medicine_key
        _combo_setup_widgets["entry_medicine_delay"] = entry_medicine_delay

        # — Revive (abaixo da Medicine) —
        rev_frame = tk.Frame(support_card, bg="#0d0d0f")
        rev_frame.pack(fill="x", padx=12, pady=(2, 10))
        rev_left = tk.Frame(rev_frame, bg="#0d0d0f")
        rev_left.pack(side="left")
        tk.Label(rev_left, text="💙", font=("Segoe UI Emoji", 10),
                 bg="#0d0d0f", fg=_BLUE).pack(side="left", padx=(0, 6))
        tk.Label(rev_left, text="REVIVE", font=("Consolas", 9, "bold"),
                 bg="#0d0d0f", fg=_BLUE).pack(side="left")
        rev_right = tk.Frame(rev_frame, bg="#0d0d0f")
        rev_right.pack(side="right")
        entry_revive_delay = tk.Entry(rev_right, width=4, font=("Consolas", 10, "bold"),
                                      bg="#18181b", fg=_CYAN, insertbackground=_CYAN,
                                      bd=1, relief="solid", justify="center")
        entry_revive_delay.pack(side="right", padx=(4, 4))
        entry_revive_key = tk.Entry(rev_right, width=5, font=("Consolas", 10, "bold"),
                                    bg="#18181b", fg="white", insertbackground="white",
                                    bd=1, relief="solid", justify="center")
        entry_revive_key.pack(side="right", padx=(0, 4))
        _combo_setup_widgets["entry_revive_key"] = entry_revive_key
        _combo_setup_widgets["entry_revive_delay"] = entry_revive_delay

        # ════════════════════════════════════════
        # SEÇÃO 2: TOGGLE HUNT NORMAL / NIGHTMARE
        # ════════════════════════════════════════
        mode_outer = tk.Frame(scroll_content, bg=_CARD,
                              highlightbackground=_BORDER, highlightthickness=1)
        mode_outer.pack(fill="x", padx=16, pady=(8, 0))

        mode_inner = tk.Frame(mode_outer, bg=_CARD)
        mode_inner.pack(fill="x", padx=4, pady=4)

        # Containers para os dois modos
        hunt_container = tk.Frame(scroll_content, bg=_BG)
        nightmare_container = tk.Frame(scroll_content, bg=_BG)

        def _select_hunt():
            combo_mode_var[0] = "HUNT NORMAL"
            btn_hunt.config(bg="#064e3b", fg=_GREEN, highlightbackground="#10b981",
                            highlightthickness=1)
            btn_nightmare.config(bg=_CARD, fg="#3f3f46", highlightbackground=_CARD,
                                 highlightthickness=0)
            nightmare_container.pack_forget()
            nm_seq_label.pack_forget()
            hunt_container.pack(fill="x", padx=16, pady=(0, 0), after=mode_outer)
            hunt_seq_label.pack(fill="x", padx=16, pady=(8, 2), after=mode_outer)
            # Re-pack plus menu frame
            _repack_plus_menu()

        def _select_nightmare():
            combo_mode_var[0] = "NIGHTMARE"
            btn_nightmare.config(bg="#450a0a", fg=_RED, highlightbackground="#dc2626",
                                 highlightthickness=1)
            btn_hunt.config(bg=_CARD, fg="#3f3f46", highlightbackground=_CARD,
                            highlightthickness=0)
            hunt_container.pack_forget()
            hunt_seq_label.pack_forget()
            nightmare_container.pack(fill="x", padx=16, pady=(0, 0), after=mode_outer)
            nm_seq_label.pack(fill="x", padx=16, pady=(8, 2), after=mode_outer)
            _repack_plus_menu()

        btn_hunt = tk.Button(mode_inner, text="●  HUNT NORMAL",
                             font=("Consolas", 9, "bold"),
                             bg="#064e3b", fg=_GREEN,
                             highlightbackground="#10b981", highlightthickness=1,
                             activebackground="#064e3b", activeforeground="white",
                             bd=0, pady=8, cursor="hand2",
                             command=_select_hunt)
        btn_hunt.pack(side="left", fill="x", expand=True, padx=(0, 2))

        btn_nightmare = tk.Button(mode_inner, text="💀  NIGHTMARE",
                                  font=("Consolas", 9, "bold"),
                                  bg=_CARD, fg="#3f3f46",
                                  highlightbackground=_CARD, highlightthickness=0,
                                  activebackground="#450a0a", activeforeground=_RED,
                                  bd=0, pady=8, cursor="hand2",
                                  command=_select_nightmare)
        btn_nightmare.pack(side="left", fill="x", expand=True, padx=(2, 0))

        _combo_setup_widgets["btn_hunt"] = btn_hunt
        _combo_setup_widgets["btn_nightmare"] = btn_nightmare

        # ════════════════════════════════════════
        # SEÇÃO 3: SEQUÊNCIA CUSTOMIZADA
        # ════════════════════════════════════════
        # --- Hunt Normal ---
        hunt_seq_label = tk.Frame(scroll_content, bg=_BG)
        hl = tk.Frame(hunt_seq_label, bg=_BG)
        hl.pack(fill="x", padx=4)
        tk.Label(hl, text="SEQUÊNCIA CUSTOMIZADA",
                 font=("Consolas", 7, "bold"), bg=_BG, fg="#52525b").pack(side="left")

        hunt_attacks_frame = tk.Frame(hunt_container, bg=_BG)
        hunt_attacks_frame.pack(fill="x", padx=4, pady=(4, 0))

        _combo_setup_widgets["hunt_attacks_frame"] = hunt_attacks_frame
        _combo_setup_widgets["attack_rows"] = attack_rows

        def _hunt_renumber():
            for i, r in enumerate(attack_rows):
                r["label"].config(text=str(i + 1))

        def _add_hunt_attack(key_val="", delay_val="0.5", row_type="atk"):
            """Adiciona linha de ataque ao Hunt Normal.
            row_type: 'atk', 'revive', 'medicine', 'pokestop'"""
            if len(attack_rows) >= 100:
                print("Máximo de 100 ataques!")
                return

            row_bg = "#18181b"
            type_colors = {
                "atk": _GREEN,
                "revive": _BLUE,
                "medicine": "#34d399",
                "pokestop": _RED,
            }
            accent = type_colors.get(row_type, _GREEN)

            row_frame = tk.Frame(hunt_attacks_frame, bg=row_bg,
                                 highlightbackground=_BORDER, highlightthickness=1)
            row_frame.pack(fill="x", pady=3, padx=2)

            # Barra lateral colorida
            bar = tk.Frame(row_frame, bg=accent, width=3)
            bar.pack(side="left", fill="y")

            inner = tk.Frame(row_frame, bg=row_bg)
            inner.pack(side="left", fill="x", expand=True, padx=8, pady=6)

            idx = len(attack_rows) + 1
            lbl_num = tk.Label(inner, text=str(idx), font=("Consolas", 9, "bold"),
                               bg=row_bg, fg="#52525b", width=2)
            lbl_num.pack(side="left", padx=(0, 6))

            type_labels = {"atk": "ATK:", "revive": "REV:", "medicine": "MED:", "pokestop": "PKS:"}
            tk.Label(inner, text=type_labels.get(row_type, "ATK:"),
                     font=("Consolas", 7, "bold"), bg=row_bg, fg="#52525b").pack(side="left", padx=(0, 2))

            entry_key = tk.Entry(inner, width=5, font=("Consolas", 10, "bold"),
                                 bg="#0a0a0c", fg="white", insertbackground="white",
                                 bd=1, relief="solid", justify="center")
            entry_key.insert(0, key_val)
            entry_key.pack(side="left", padx=(0, 8))

            tk.Label(inner, text="⏱", font=("Segoe UI Emoji", 8),
                     bg=row_bg, fg="#3f3f46").pack(side="left", padx=(0, 2))

            entry_delay = tk.Entry(inner, width=4, font=("Consolas", 10, "bold"),
                                   bg="#0a0a0c", fg=_CYAN, insertbackground=_CYAN,
                                   bd=1, relief="solid", justify="center")
            entry_delay.insert(0, str(delay_val))
            entry_delay.pack(side="left")

            row_data = {"frame": row_frame, "entry_key": entry_key,
                        "entry_delay": entry_delay, "label": lbl_num, "type": row_type}

            def _remove():
                attack_rows.remove(row_data)
                row_frame.destroy()
                _hunt_renumber()

            btn_del = tk.Button(inner, text="🗑", font=("Segoe UI Emoji", 10),
                                bg=row_bg, fg="#3f3f46", bd=0, cursor="hand2",
                                activebackground=row_bg, activeforeground=_RED,
                                command=_remove)
            btn_del.pack(side="right", padx=(8, 0))

            attack_rows.append(row_data)

        _combo_setup_widgets["_add_hunt_attack"] = _add_hunt_attack

        # --- Nightmare Mode ---
        nm_seq_label = tk.Frame(scroll_content, bg=_BG)
        nl = tk.Frame(nm_seq_label, bg=_BG)
        nl.pack(fill="x", padx=4)
        tk.Label(nl, text="SEQUÊNCIA CUSTOMIZADA",
                 font=("Consolas", 7, "bold"), bg=_BG, fg="#52525b").pack(side="left")

        nm_attacks_frame = tk.Frame(nightmare_container, bg=_BG)
        nm_attacks_frame.pack(fill="x", padx=4, pady=(4, 0))

        _combo_setup_widgets["nm_attacks_frame"] = nm_attacks_frame
        _combo_setup_widgets["nightmare_rows"] = nightmare_rows

        def _nm_renumber():
            for i, r in enumerate(nightmare_rows):
                emoji_map = {"pokeball": "🔴", "attack": "💀",
                             "revive": "💙", "medicine": "💊", "pokestop": "📍"}
                em = emoji_map.get(r["type"], "💀")
                r["label"].config(text=f"{em} {i + 1}")

        def _add_nightmare_row(key1_val="", key2_val="", delay_val="0.5", row_type="attack"):
            """row_type: 'attack', 'pokeball', 'revive', 'medicine', 'pokestop'"""
            if len(nightmare_rows) >= 100:
                print("Máximo de 100 itens nightmare!")
                return

            row_bg = "#18181b"
            type_colors = {
                "attack": _RED,
                "pokeball": _ORANGE,
                "revive": _BLUE,
                "medicine": "#34d399",
                "pokestop": "#ef4444",
            }
            accent = type_colors.get(row_type, _RED)

            row_frame = tk.Frame(nm_attacks_frame, bg=row_bg,
                                 highlightbackground=_BORDER, highlightthickness=1)
            row_frame.pack(fill="x", pady=3, padx=2)

            bar = tk.Frame(row_frame, bg=accent, width=3)
            bar.pack(side="left", fill="y")

            inner = tk.Frame(row_frame, bg=row_bg)
            inner.pack(side="left", fill="x", expand=True, padx=8, pady=6)

            idx = len(nightmare_rows) + 1
            emoji_map = {"pokeball": "🔴", "attack": "💀",
                         "revive": "💙", "medicine": "💊", "pokestop": "📍"}
            em = emoji_map.get(row_type, "💀")
            lbl_num = tk.Label(inner, text=f"{em} {idx}", font=("Consolas", 9, "bold"),
                               bg=row_bg, fg="#52525b", width=4)
            lbl_num.pack(side="left", padx=(0, 4))

            entry_key2 = None

            if row_type == "pokeball":
                tk.Label(inner, text="K1:", font=("Consolas", 7, "bold"),
                         bg=row_bg, fg="#52525b").pack(side="left", padx=(0, 1))
                entry_key1 = tk.Entry(inner, width=4, font=("Consolas", 10, "bold"),
                                      bg="#0a0a0c", fg="white", insertbackground="white",
                                      bd=1, relief="solid", justify="center")
                entry_key1.insert(0, key1_val)
                entry_key1.pack(side="left", padx=(0, 2))

                tk.Label(inner, text="+", font=("Consolas", 9, "bold"),
                         bg=row_bg, fg=_ORANGE).pack(side="left", padx=2)

                entry_key2 = tk.Entry(inner, width=4, font=("Consolas", 10, "bold"),
                                      bg="#0a0a0c", fg=_ORANGE, insertbackground=_ORANGE,
                                      bd=1, relief="solid", justify="center")
                entry_key2.insert(0, key2_val)
                entry_key2.pack(side="left", padx=(0, 4))
            else:
                type_labels = {"attack": "ATK:", "revive": "REV:", "medicine": "MED:", "pokestop": "PKS:"}
                tk.Label(inner, text=type_labels.get(row_type, "ATK:"),
                         font=("Consolas", 7, "bold"), bg=row_bg, fg="#52525b").pack(side="left", padx=(0, 2))
                entry_key1 = tk.Entry(inner, width=5, font=("Consolas", 10, "bold"),
                                      bg="#0a0a0c", fg="white", insertbackground="white",
                                      bd=1, relief="solid", justify="center")
                entry_key1.insert(0, key1_val)
                entry_key1.pack(side="left", padx=(0, 8))

            tk.Label(inner, text="⏱", font=("Segoe UI Emoji", 8),
                     bg=row_bg, fg="#3f3f46").pack(side="left", padx=(0, 2))
            entry_delay = tk.Entry(inner, width=4, font=("Consolas", 10, "bold"),
                                   bg="#0a0a0c", fg=_CYAN, insertbackground=_CYAN,
                                   bd=1, relief="solid", justify="center")
            entry_delay.insert(0, str(delay_val))
            entry_delay.pack(side="left")

            row_data = {"frame": row_frame, "entry_key1": entry_key1,
                        "entry_key2": entry_key2, "entry_delay": entry_delay,
                        "label": lbl_num, "type": row_type}

            def _remove_nm():
                nightmare_rows.remove(row_data)
                row_frame.destroy()
                _nm_renumber()

            btn_del = tk.Button(inner, text="🗑", font=("Segoe UI Emoji", 10),
                                bg=row_bg, fg="#3f3f46", bd=0, cursor="hand2",
                                activebackground=row_bg, activeforeground=_RED,
                                command=_remove_nm)
            btn_del.pack(side="right", padx=(8, 0))

            nightmare_rows.append(row_data)

        _combo_setup_widgets["_add_nightmare_row"] = _add_nightmare_row

        # ════════════════════════════════════════
        # PLUS MENU (inserir ação especial)
        # ════════════════════════════════════════
        plus_menu_frame = tk.Frame(scroll_content, bg=_BG)
        _combo_setup_widgets["plus_menu_frame"] = plus_menu_frame

        def _repack_plus_menu():
            """Garante que o plus_menu aparece na posição certa."""
            plus_menu_frame.pack_forget()
            if plus_menu_visible[0]:
                plus_menu_frame.pack(fill="x", padx=16, pady=(4, 0))

        def _toggle_plus_menu():
            plus_menu_visible[0] = not plus_menu_visible[0]
            if plus_menu_visible[0]:
                btn_plus.config(bg=_YELLOW, fg="black")
                plus_menu_frame.pack(fill="x", padx=16, pady=(4, 0))
                _build_plus_menu_contents()
            else:
                btn_plus.config(bg="#27272a", fg="#52525b")
                plus_menu_frame.pack_forget()

        def _build_plus_menu_contents():
            for w in plus_menu_frame.winfo_children():
                w.destroy()

            pm_inner = tk.Frame(plus_menu_frame, bg="#0d0d0f",
                                highlightbackground=_BORDER, highlightthickness=1)
            pm_inner.pack(fill="x")

            tk.Label(pm_inner, text="INSERIR AÇÃO ESPECIAL",
                     font=("Consolas", 7, "bold"), bg="#0d0d0f", fg="#52525b").pack(pady=(8, 4))

            def _add_special(action_type):
                """Adiciona ação especial com tecla pré-preenchida da config."""
                rev_k = _combo_setup_widgets["entry_revive_key"].get()
                rev_d = _combo_setup_widgets["entry_revive_delay"].get() or "0.5"
                med_k = _combo_setup_widgets["entry_medicine_key"].get()
                ps_k = _combo_setup_widgets["entry_pokestop_key"].get()
                med_d = _combo_setup_widgets["entry_medicine_delay"].get() or "0.5"
                ps_d = _combo_setup_widgets["entry_pokestop_delay"].get() or "0.5"

                if combo_mode_var[0] == "HUNT NORMAL":
                    if action_type == "revive":
                        _add_hunt_attack(rev_k, rev_d, "revive")
                    elif action_type == "medicine":
                        _add_hunt_attack(med_k, med_d, "medicine")
                    elif action_type == "pokestop":
                        _add_hunt_attack(ps_k, ps_d, "pokestop")
                else:
                    if action_type == "revive":
                        _add_nightmare_row(rev_k, "", rev_d, "revive")
                    elif action_type == "medicine":
                        _add_nightmare_row(med_k, "", med_d, "medicine")
                    elif action_type == "pokestop":
                        _add_nightmare_row(ps_k, "", ps_d, "pokestop")

                _toggle_plus_menu()

            # Revive
            rev_btn = tk.Frame(pm_inner, bg="#1e3a5f",
                               highlightbackground="#1e3a5f", highlightthickness=1,
                               cursor="hand2")
            rev_btn.pack(fill="x", padx=8, pady=2)
            rev_inner = tk.Frame(rev_btn, bg="#1e3a5f")
            rev_inner.pack(fill="x", padx=10, pady=8)
            tk.Label(rev_inner, text="💙", font=("Segoe UI Emoji", 10),
                     bg="#1e3a5f", fg=_BLUE).pack(side="left", padx=(0, 8))
            tk.Label(rev_inner, text="REVIVE", font=("Consolas", 9, "bold"),
                     bg="#1e3a5f", fg=_BLUE).pack(side="left")
            tk.Label(rev_inner, text="+", font=("Consolas", 12, "bold"),
                     bg="#1e3a5f", fg="#3f3f46").pack(side="right")
            rev_btn.bind("<Button-1>", lambda e: _add_special("revive"))
            for child in rev_btn.winfo_children():
                child.bind("<Button-1>", lambda e: _add_special("revive"))
                for gc in child.winfo_children():
                    gc.bind("<Button-1>", lambda e: _add_special("revive"))

            # Medicine
            med_btn = tk.Frame(pm_inner, bg="#064e3b",
                               highlightbackground="#064e3b", highlightthickness=1,
                               cursor="hand2")
            med_btn.pack(fill="x", padx=8, pady=2)
            med_inner_btn = tk.Frame(med_btn, bg="#064e3b")
            med_inner_btn.pack(fill="x", padx=10, pady=8)
            tk.Label(med_inner_btn, text="💊", font=("Segoe UI Emoji", 10),
                     bg="#064e3b", fg=_GREEN).pack(side="left", padx=(0, 8))
            tk.Label(med_inner_btn, text="MEDICINE", font=("Consolas", 9, "bold"),
                     bg="#064e3b", fg=_GREEN).pack(side="left")
            med_btn.bind("<Button-1>", lambda e: _add_special("medicine"))
            for child in med_btn.winfo_children():
                child.bind("<Button-1>", lambda e: _add_special("medicine"))
                for gc in child.winfo_children():
                    gc.bind("<Button-1>", lambda e: _add_special("medicine"))

            # Pokestop
            pks_btn = tk.Frame(pm_inner, bg="#1a0505",
                               highlightbackground="#1a0505", highlightthickness=1,
                               cursor="hand2")
            pks_btn.pack(fill="x", padx=8, pady=(2, 8))
            pks_inner = tk.Frame(pks_btn, bg="#1a0505")
            pks_inner.pack(fill="x", padx=10, pady=8)
            tk.Label(pks_inner, text="📍", font=("Segoe UI Emoji", 10),
                     bg="#1a0505", fg=_RED).pack(side="left", padx=(0, 8))
            tk.Label(pks_inner, text="POKESTOP", font=("Consolas", 9, "bold"),
                     bg="#1a0505", fg=_RED).pack(side="left")
            pks_btn.bind("<Button-1>", lambda e: _add_special("pokestop"))
            for child in pks_btn.winfo_children():
                child.bind("<Button-1>", lambda e: _add_special("pokestop"))
                for gc in child.winfo_children():
                    gc.bind("<Button-1>", lambda e: _add_special("pokestop"))

        # ════════════════════════════════════════
        # FOOTER: ADICIONAR ATK + ➕ + TROCA POKEMON
        # ════════════════════════════════════════
        footer_frame = tk.Frame(scroll_content, bg=_BG)
        footer_frame.pack(fill="x", padx=16, pady=(10, 0))

        footer_grid = tk.Frame(footer_frame, bg=_BG)
        footer_grid.pack(fill="x")
        footer_grid.columnconfigure(0, weight=1)
        footer_grid.columnconfigure(1, weight=0)
        footer_grid.columnconfigure(2, weight=1)

        def _add_atk():
            if combo_mode_var[0] == "HUNT NORMAL":
                _add_hunt_attack()
            else:
                _add_nightmare_row(row_type="attack")

        btn_add_atk = tk.Button(footer_grid, text="ADICIONAR ATK",
                                font=("Consolas", 8, "bold"),
                                bg="#064e3b", fg=_GREEN,
                                activebackground="#10b981", activeforeground="black",
                                bd=0, pady=10, cursor="hand2",
                                highlightbackground="#10b981", highlightthickness=1,
                                command=_add_atk)
        btn_add_atk.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        btn_plus = tk.Button(footer_grid, text="＋", font=("Consolas", 16, "bold"),
                             bg="#27272a", fg="#52525b",
                             activebackground=_YELLOW, activeforeground="black",
                             bd=0, width=3, cursor="hand2",
                             command=_toggle_plus_menu)
        btn_plus.grid(row=0, column=1, padx=4)

        def _add_swap():
            if combo_mode_var[0] == "NIGHTMARE":
                _add_nightmare_row(row_type="pokeball")
            else:
                _add_hunt_attack()

        btn_troca = tk.Button(footer_grid, text="TROCA POKEMON",
                              font=("Consolas", 8, "bold"),
                              bg="#431407", fg=_ORANGE,
                              activebackground=_ORANGE, activeforeground="black",
                              bd=0, pady=10, cursor="hand2",
                              highlightbackground=_ORANGE, highlightthickness=1,
                              command=_add_swap)
        btn_troca.grid(row=0, column=2, sticky="ew", padx=(4, 0))

        # ════════════════════════════════════════
        # BOTÃO GRAVAR CONFIGURAÇÕES
        # ════════════════════════════════════════
        def _salvar_combo():
            global pokestop_key, pokemedi_key, revive_key
            global pokestop_delay, pokemedi_delay, revive_delay
            global combo_start_key, nightmare_attacks, combo_mode_active
            global hunt_attacks

            def get_delay(entry, default=0.5):
                value = entry.get()
                try:
                    return float(value)
                except ValueError:
                    return default

            combo_start_key = entry_combo_start.get()
            pokestop_key = entry_pokestop_key.get()
            pokestop_delay = get_delay(entry_pokestop_delay)
            pokemedi_key = entry_medicine_key.get()
            pokemedi_delay = get_delay(entry_medicine_delay)
            revive_key = entry_revive_key.get()
            revive_delay = get_delay(entry_revive_delay)
            combo_mode_active = combo_mode_var[0]

            # Coleta hunt_attacks como lista dinâmica
            hunt_attacks = []
            for row in attack_rows:
                k = row["entry_key"].get()
                d = get_delay(row["entry_delay"])
                rtype = row.get("type", "atk")
                if k:
                    hunt_attacks.append({"key": k, "delay": d, "type": rtype})

            # Coleta nightmare attacks
            nightmare_attacks = []
            for nm_row in nightmare_rows:
                k1 = nm_row["entry_key1"].get()
                k2 = nm_row["entry_key2"].get() if nm_row["entry_key2"] else ""
                d = get_delay(nm_row["entry_delay"])
                rtype = nm_row["type"]
                if k1 or k2:
                    nightmare_attacks.append({"key1": k1, "key2": k2, "delay": d, "type": rtype})

            print(f"✅ Combo configurado! Modo: {combo_mode_active}")
            salvar_perfil_atual(perfil_ativo)

        btn_salvar = tk.Button(scroll_content, text="💾  GRAVAR CONFIGURAÇÕES",
                               font=("Consolas", 11, "bold"),
                               bg="#10b981", fg="white",
                               activebackground="#059669", activeforeground="white",
                               bd=0, pady=12, cursor="hand2",
                               command=_salvar_combo)
        btn_salvar.pack(fill="x", padx=16, pady=(10, 6))

        # Speaker dots
        dots = tk.Frame(scroll_content, bg=_BG)
        dots.pack(pady=(0, 10))
        for _ in range(3):
            tk.Canvas(dots, width=5, height=5, bg=_BG, highlightthickness=0)\
              .pack(side="left", padx=2)

        # Inicia no modo correto
        if combo_mode_active == "NIGHTMARE":
            _select_nightmare()
        else:
            _select_hunt()

        _combo_setup_built[0] = True

    def _refresh_combo_setup():
        """Preenche/recarrega os campos de config com os valores globais atuais."""
        w = _combo_setup_widgets

        # Limpa e preenche campos de suporte
        for name, val in [
            ("entry_combo_start", combo_start_key),
            ("entry_pokestop_key", pokestop_key),
            ("entry_pokestop_delay", str(pokestop_delay)),
            ("entry_medicine_key", pokemedi_key),
            ("entry_medicine_delay", str(pokemedi_delay)),
            ("entry_revive_key", revive_key),
            ("entry_revive_delay", str(revive_delay)),
        ]:
            entry = w.get(name)
            if entry:
                entry.delete(0, "end")
                entry.insert(0, val)

        # Limpa e reconstrói ataques hunt (lista dinâmica)
        attack_rows = w.get("attack_rows", [])
        for row in list(attack_rows):
            row["frame"].destroy()
        attack_rows.clear()

        add_hunt_fn = w.get("_add_hunt_attack")
        if add_hunt_fn:
            for atk in hunt_attacks:
                add_hunt_fn(atk.get("key", ""), atk.get("delay", 0.5), atk.get("type", "atk"))

        # Limpa e reconstrói ataques nightmare
        nm_rows = w.get("nightmare_rows", [])
        for row in list(nm_rows):
            row["frame"].destroy()
        nm_rows.clear()

        add_nm_fn = w.get("_add_nightmare_row")
        if add_nm_fn:
            for nm_atk in nightmare_attacks:
                add_nm_fn(nm_atk.get("key1", ""), nm_atk.get("key2", ""),
                          nm_atk.get("delay", 0.5), nm_atk.get("type", "attack"))

        # Atualiza toggle de modo
        btn_hunt = w.get("btn_hunt")
        btn_nightmare = w.get("btn_nightmare")
        if combo_mode_active == "NIGHTMARE" and btn_nightmare:
            btn_nightmare.invoke()
        elif btn_hunt:
            btn_hunt.invoke()

    def open_combo_setup():
        """Mostra a tela de Setup Combo dentro da mesma janela."""
        _build_combo_setup_ui()
        _refresh_combo_setup()
        main_content_frame.pack_forget()
        combo_setup_frame.pack(fill="both", expand=True)

    # ═══════════════════════════════════════════════════════
    # 📷 SETUP CAPTURA — tela inline (gavetas de scan)
    # ═══════════════════════════════════════════════════════
    _capture_setup_built = [False]
    _capture_setup_widgets = {}
    _capture_drawer_widgets = []       # lista de dicts de widgets por gaveta
    _capture_expanded_idx = [None]     # índice expandido (só um de cada vez)
    _capture_hotkey_active = [None]    # gaveta com hotkey M ativa (nome ou None)

    def _voltar_do_capture_setup():
        """Volta da tela de captura para a tela principal."""
        # Desativa hotkey M se ativa
        if _capture_hotkey_active[0] is not None:
            try:
                keyboard.remove_hotkey('m')
            except Exception:
                pass
            _capture_hotkey_active[0] = None
        capture_setup_frame.pack_forget()
        main_content_frame.pack(fill="both", expand=True)

    def _build_capture_setup_ui():
        """Constrói a UI de Setup Captura dentro de capture_setup_frame (uma vez só)."""
        if _capture_setup_built[0]:
            return

        _BG = "#121214"
        _CARD = "#1a1a1e"
        _BORDER = "#27272a"
        _DIM = "#71717a"
        _CYAN = "#22d3ee"
        _GREEN = "#10b981"
        _RED = "#ef4444"
        _PURPLE = "#a855f7"

        # ── HEADER ──
        header = tk.Frame(capture_setup_frame, bg=_BG)
        header.pack(fill="x", padx=16, pady=(14, 0))

        btn_voltar = tk.Button(
            header, text="❮  VOLTAR", font=("Consolas", 9, "bold"),
            bg=_BG, fg=_DIM, bd=0, cursor="hand2",
            activebackground=_BG, activeforeground="white",
            command=_voltar_do_capture_setup
        )
        btn_voltar.pack(side="left")

        btn_scan_toggle = tk.Button(
            header,
            text="▶  INICIAR SCAN (G)",
            font=("Consolas", 8, "bold"),
            bg=_GREEN, fg="#0a0a0c",
            activebackground="#059669", activeforeground="#0a0a0c",
            bd=0, padx=10, pady=4, cursor="hand2",
            command=toggle_captura_global
        )
        btn_scan_toggle.pack(side="right")
        _capture_setup_widgets["btn_scan_toggle"] = btn_scan_toggle

        tk.Frame(capture_setup_frame, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── Section title ──
        section_title = tk.Frame(capture_setup_frame, bg=_BG)
        section_title.pack(fill="x", padx=16, pady=(10, 4))
        tk.Label(section_title, text="📂", font=("Segoe UI Emoji", 10),
                 bg=_BG, fg=_CYAN).pack(side="left", padx=(0, 6))
        tk.Label(section_title, text="BASE DE DADOS DE SCAN",
                 font=("Consolas", 10, "bold italic"),
                 bg=_BG, fg=_CYAN).pack(side="left")

        # ── SCROLLABLE DRAWERS AREA ──
        scroll_outer = tk.Frame(capture_setup_frame, bg=_BG)
        scroll_outer.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        main_canvas = tk.Canvas(scroll_outer, bg=_BG, highlightthickness=0)
        main_scrollbar = tk.Scrollbar(scroll_outer, orient="vertical", command=main_canvas.yview)
        scroll_content = tk.Frame(main_canvas, bg=_BG)

        scroll_content.bind("<Configure>",
                            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")

        def _resize_scroll(event):
            main_canvas.itemconfig(main_canvas.find_all()[0], width=event.width)
        main_canvas.bind("<Configure>", _resize_scroll)

        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        _capture_setup_widgets["scroll_content"] = scroll_content
        _capture_setup_widgets["main_canvas"] = main_canvas

        # ── FOOTER: NOVA GAVETA ──
        footer = tk.Frame(capture_setup_frame, bg=_BG)
        footer.pack(fill="x", padx=16, pady=(6, 14))

        btn_nova_gaveta = tk.Button(
            footer,
            text="＋   NOVA GAVETA DE SCAN",
            font=("Consolas", 10, "bold"),
            bg=_CYAN, fg="#0a0a0c",
            activebackground="#06b6d4", activeforeground="#0a0a0c",
            bd=0, pady=10, cursor="hand2",
            command=_nova_gaveta_popup
        )
        btn_nova_gaveta.pack(fill="x")

        _capture_setup_built[0] = True

    def _nova_gaveta_popup():
        """Mostra um mini-popup embutido para digitar o nome da gaveta."""
        scroll_content = _capture_setup_widgets.get("scroll_content")
        if scroll_content is None:
            return

        _BG = "#121214"
        _CARD = "#1a1a1e"
        _BORDER = "#27272a"
        _CYAN = "#22d3ee"

        # Frame do popup (aparece no topo do scroll)
        popup_frame = tk.Frame(scroll_content, bg=_CARD,
                               highlightbackground=_CYAN, highlightthickness=1)
        popup_frame.pack(fill="x", padx=16, pady=(6, 4))

        tk.Label(popup_frame, text="NOME DO POKÉMON:",
                 font=("Consolas", 9, "bold"),
                 bg=_CARD, fg=_CYAN).pack(padx=12, pady=(10, 4))

        entry_nome = tk.Entry(popup_frame, font=("Consolas", 11, "bold"),
                              bg="#18181b", fg="white", insertbackground="white",
                              bd=1, relief="solid", justify="center", width=20)
        entry_nome.pack(padx=12, pady=(0, 6))
        entry_nome.focus_set()

        # ── Checkbox SHINY ──
        _YELLOW = "#eab308"
        shiny_var = tk.BooleanVar(value=False)
        shiny_frame = tk.Frame(popup_frame, bg=_CARD)
        shiny_frame.pack(padx=12, pady=(2, 6))
        chk_shiny = tk.Checkbutton(
            shiny_frame, text="✨ SHINY", variable=shiny_var,
            font=("Consolas", 9, "bold"),
            bg=_CARD, fg=_YELLOW, selectcolor="#18181b",
            activebackground=_CARD, activeforeground=_YELLOW,
            cursor="hand2"
        )
        chk_shiny.pack(side="left")
        tk.Label(shiny_frame, text="(cor + 94%)",
                 font=("Consolas", 7), bg=_CARD, fg="#71717a").pack(side="left", padx=(4, 0))

        btn_row = tk.Frame(popup_frame, bg=_CARD)
        btn_row.pack(fill="x", padx=12, pady=(0, 10))

        def confirmar():
            nome = entry_nome.get().strip()
            if not nome:
                return
            # Cria pasta
            os.makedirs(os.path.join(CAPTURA_DIR, nome), exist_ok=True)
            gaveta_data = {"nome": nome, "ativo": False, "shiny": shiny_var.get()}
            # Verifica duplicata
            if not any(g["nome"] == nome for g in captura_gavetas):
                captura_gavetas.append(gaveta_data)
            popup_frame.destroy()
            _refresh_capture_drawers()

        def cancelar():
            popup_frame.destroy()

        entry_nome.bind("<Return>", lambda e: confirmar())
        entry_nome.bind("<Escape>", lambda e: cancelar())

        tk.Button(btn_row, text="✅ CRIAR", font=("Consolas", 9, "bold"),
                  bg=_CYAN, fg="#0a0a0c", bd=0, padx=12, pady=4,
                  activebackground="#06b6d4", cursor="hand2",
                  command=confirmar).pack(side="left", expand=True, fill="x", padx=(0, 4))
        tk.Button(btn_row, text="CANCELAR", font=("Consolas", 9, "bold"),
                  bg="#27272a", fg="#71717a", bd=0, padx=12, pady=4,
                  activebackground="#3f3f46", cursor="hand2",
                  command=cancelar).pack(side="right", expand=True, fill="x", padx=(4, 0))

    def _refresh_capture_drawers():
        """Reconstrói a lista visual de gavetas."""
        scroll_content = _capture_setup_widgets.get("scroll_content")
        if scroll_content is None:
            return

        # Limpa widgets anteriores
        for w in scroll_content.winfo_children():
            w.destroy()
        _capture_drawer_widgets.clear()
        _capture_expanded_idx[0] = None

        _BG = "#121214"
        _CARD = "#1a1a1e"
        _BORDER = "#27272a"
        _DIM = "#71717a"
        _CYAN = "#22d3ee"
        _GREEN = "#10b981"
        _RED = "#ef4444"
        _PURPLE = "#a855f7"

        # Sincroniza com pastas existentes no disco
        if os.path.isdir(CAPTURA_DIR):
            for pasta_nome in sorted(os.listdir(CAPTURA_DIR)):
                pasta_full = os.path.join(CAPTURA_DIR, pasta_nome)
                if os.path.isdir(pasta_full):
                    if not any(g["nome"] == pasta_nome for g in captura_gavetas):
                        captura_gavetas.append({"nome": pasta_nome, "ativo": False})

        for idx, gaveta in enumerate(list(captura_gavetas)):
            nome = gaveta["nome"]
            pasta = os.path.join(CAPTURA_DIR, nome)
            n_imgs = len([f for f in os.listdir(pasta) if f.endswith(".png")]) if os.path.isdir(pasta) else 0

            # ── Card da gaveta ──
            card = tk.Frame(scroll_content, bg=_CARD,
                            highlightbackground=_BORDER, highlightthickness=1)
            card.pack(fill="x", padx=16, pady=(6, 0))

            # ── Cabeçalho (clicável) ──
            card_header = tk.Frame(card, bg=_CARD)
            card_header.pack(fill="x", padx=10, pady=8)

            # LED de status (clicável — toggle ativo/inativo)
            is_ativo = gaveta.get("ativo", False)
            is_shiny = gaveta.get("shiny", False)
            led_color = "#00ff88" if is_ativo else "#ef4444"
            led = tk.Label(card_header, text="●", font=("Consolas", 10),
                           bg=_CARD, fg=led_color, cursor="hand2")
            led.pack(side="left", padx=(0, 8))

            def _toggle_ativo(event=None, _led=led, _gaveta=gaveta, _nome=nome):
                current = _gaveta.get("ativo", False)
                _gaveta["ativo"] = not current
                if not current:
                    _led.config(fg="#00ff88")
                    print(f"✅ Gaveta '{_nome}' ATIVADA")
                else:
                    _led.config(fg="#ef4444")
                    print(f"❌ Gaveta '{_nome}' DESATIVADA")

            led.bind("<Button-1>", _toggle_ativo)

            # Nome + contagem (stacked vertically like React design)
            info_frame = tk.Frame(card_header, bg=_CARD)
            info_frame.pack(side="left", fill="x", expand=True)
            # Nome + badge shiny
            nome_row = tk.Frame(info_frame, bg=_CARD)
            nome_row.pack(anchor="w")
            lbl_nome = tk.Label(nome_row, text=nome.upper(),
                                font=("Consolas", 10, "bold"),
                                bg=_CARD, fg="#a1a1aa")
            lbl_nome.pack(side="left")
            if is_shiny:
                tk.Label(nome_row, text=" ✨ SHINY",
                         font=("Consolas", 7, "bold"),
                         bg=_CARD, fg="#eab308").pack(side="left", padx=(4, 0))

            lbl_count = tk.Label(info_frame, text=f"{n_imgs} IMAGENS DETECTADAS",
                                 font=("Consolas", 7),
                                 bg=_CARD, fg="#52525b")
            lbl_count.pack(anchor="w")

            # ── Toggle Shiny checkbox no card ──
            def _toggle_shiny(event=None, _gaveta=gaveta):
                _gaveta["shiny"] = not _gaveta.get("shiny", False)
                state = "SHINY" if _gaveta["shiny"] else "NORMAL"
                print(f"✨ Gaveta '{_gaveta['nome']}' → {state}")
                _refresh_capture_drawers()

            # Chevron
            chevron = tk.Label(card_header, text="❯", font=("Consolas", 10),
                               bg=_CARD, fg="#52525b")
            chevron.pack(side="right", padx=(4, 0))

            # ── Conteúdo expandido (oculto inicialmente) ──
            detail = tk.Frame(card, bg=_CARD)

            # Botões de ação
            action_row = tk.Frame(detail, bg=_CARD)
            action_row.pack(fill="x", padx=8, pady=(0, 6))

            btn_capturar = tk.Button(
                action_row, text="📸 CAPTURAR (M)",
                font=("Consolas", 8, "bold"),
                bg="#1e1528", fg=_PURPLE,
                activebackground="#6d28d9", activeforeground="white",
                bd=1, relief="solid", padx=8, pady=6, cursor="hand2"
            )
            btn_capturar.pack(side="left", expand=True, fill="x", padx=(0, 4))

            # Botão toggle shiny
            shiny_state = gaveta.get("shiny", False)
            shiny_text = "✨ SHINY: ON" if shiny_state else "✨ SHINY: OFF"
            shiny_fg = "#eab308" if shiny_state else _DIM
            shiny_bg = "#1c1a0e" if shiny_state else "#1c1c1e"
            btn_shiny = tk.Button(
                action_row, text=shiny_text,
                font=("Consolas", 8, "bold"),
                bg=shiny_bg, fg=shiny_fg,
                activebackground="#a16207", activeforeground="white",
                bd=1, relief="solid", padx=8, pady=6, cursor="hand2",
                command=_toggle_shiny
            )
            btn_shiny.pack(side="left", expand=True, fill="x", padx=(0, 4))

            btn_excluir = tk.Button(
                action_row, text="🗑 EXCLUIR",
                font=("Consolas", 8, "bold"),
                bg="#1c1c1e", fg=_RED,
                activebackground="#991b1b", activeforeground="white",
                bd=1, relief="solid", padx=8, pady=6, cursor="hand2"
            )
            btn_excluir.pack(side="right", expand=True, fill="x", padx=(4, 0))

            # Grade de imagens
            imgs_grid = tk.Frame(detail, bg="#0a0a0c",
                                 highlightbackground=_BORDER, highlightthickness=1)
            imgs_grid.pack(fill="x", padx=8, pady=(0, 8))

            def _populate_imgs(grid=imgs_grid, nome_g=nome, pasta_g=pasta, lbl_c=lbl_count, led_ref=led):
                for w in grid.winfo_children():
                    w.destroy()
                if not os.path.isdir(pasta_g):
                    os.makedirs(pasta_g, exist_ok=True)
                arquivos = sorted([f for f in os.listdir(pasta_g) if f.endswith(".png")])
                n = len(arquivos)
                lbl_c.config(text=f"{n} IMAGENS DETECTADAS")
                led_ref.config(fg="#00ff88" if n > 0 else "#3f3f46")
                if n == 0:
                    empty_frame = tk.Frame(grid, bg="#0a0a0c")
                    empty_frame.pack(fill="x", pady=20)
                    tk.Label(empty_frame, text="🔍", font=("Segoe UI Emoji", 16),
                             bg="#0a0a0c", fg="#3f3f46").pack()
                    tk.Label(empty_frame, text="GAVETA VAZIA",
                             font=("Consolas", 7, "bold italic"),
                             bg="#0a0a0c", fg="#3f3f46").pack()
                    return
                # Grid 4 colunas
                row_frame = None
                for i, arq_name in enumerate(arquivos[:12]):
                    if i % 4 == 0:
                        row_frame = tk.Frame(grid, bg="#0a0a0c")
                        row_frame.pack(fill="x", padx=4, pady=2)
                    try:
                        img_path = os.path.join(pasta_g, arq_name)
                        pil_img = Image.open(img_path).resize((36, 36), Image.NEAREST)
                        tk_img = ImageTk.PhotoImage(pil_img)
                        cell = tk.Frame(row_frame, bg="#121214", bd=1, relief="solid")
                        cell.pack(side="left", padx=2, pady=2)
                        img_lbl = tk.Label(cell, image=tk_img, bg="#121214")
                        img_lbl.image = tk_img
                        img_lbl.pack(padx=2, pady=2)
                        # Delete button on hover
                        def _del_img(p=img_path, refresh=_populate_imgs):
                            try:
                                os.remove(p)
                                refresh()
                            except Exception as ex:
                                print(f"Erro ao remover: {ex}")
                        del_btn = tk.Button(cell, text="✕", font=("Consolas", 6),
                                            bg="#ff4444", fg="white", bd=0, padx=2, pady=0,
                                            activebackground="#cc0000", cursor="hand2",
                                            command=_del_img)
                        del_btn.pack()
                    except Exception:
                        pass

            # ── Lógica de expand/collapse ──
            widget_info = {
                "card": card, "detail": detail, "chevron": chevron,
                "lbl_nome": lbl_nome, "led": led, "lbl_count": lbl_count,
                "imgs_grid": imgs_grid, "populate": _populate_imgs,
                "btn_capturar": btn_capturar, "btn_excluir": btn_excluir,
                "nome": nome, "idx": idx
            }
            _capture_drawer_widgets.append(widget_info)

            def _toggle_expand(i=idx, w=widget_info):
                if _capture_expanded_idx[0] == i:
                    # Fechar
                    w["detail"].pack_forget()
                    w["chevron"].config(text="❯")
                    w["lbl_nome"].config(fg="#a1a1aa")
                    w["card"].config(highlightbackground="#27272a")
                    _capture_expanded_idx[0] = None
                else:
                    # Fechar anterior
                    if _capture_expanded_idx[0] is not None and _capture_expanded_idx[0] < len(_capture_drawer_widgets):
                        prev = _capture_drawer_widgets[_capture_expanded_idx[0]]
                        prev["detail"].pack_forget()
                        prev["chevron"].config(text="❯")
                        prev["lbl_nome"].config(fg="#a1a1aa")
                        prev["card"].config(highlightbackground="#27272a")
                    # Abrir este
                    w["detail"].pack(fill="x", after=w["card"].winfo_children()[0])
                    w["chevron"].config(text="❮")
                    w["lbl_nome"].config(fg="#22d3ee")
                    w["card"].config(highlightbackground="#1a3a40")
                    _capture_expanded_idx[0] = i
                    w["populate"]()

            # Bind click em header inteiro (exceto LED que tem toggle próprio)
            for widget in [card_header, info_frame, nome_row, lbl_nome, lbl_count, chevron]:
                widget.bind("<Button-1>", lambda e, fn=_toggle_expand: fn())
                widget.config(cursor="hand2")

            # Capturar (M) toggle
            def _toggle_captura_hotkey(i=idx, w=widget_info):
                nome_g = w["nome"]
                pasta_g = os.path.join(CAPTURA_DIR, nome_g)
                if _capture_hotkey_active[0] == nome_g:
                    # Desativar
                    try:
                        keyboard.remove_hotkey('m')
                    except Exception:
                        pass
                    _capture_hotkey_active[0] = None
                    w["btn_capturar"].config(text="📸 CAPTURAR (M)", fg="#a855f7", bg="#1c1c1e")
                    print(f"Modo captura desativado para '{nome_g}'")
                else:
                    # Desativar anterior se existir
                    if _capture_hotkey_active[0] is not None:
                        try:
                            keyboard.remove_hotkey('m')
                        except Exception:
                            pass
                        # Reset visual do anterior
                        for dw in _capture_drawer_widgets:
                            if dw["nome"] == _capture_hotkey_active[0]:
                                dw["btn_capturar"].config(text="📸 CAPTURAR (M)", fg="#a855f7", bg="#1c1c1e")
                    # Ativar
                    def on_m(n=nome_g, p=pasta_g, w_ref=w):
                        capturar_imagem_cursor(n)
                        w_ref["populate"]()
                    keyboard.add_hotkey('m', on_m)
                    _capture_hotkey_active[0] = nome_g
                    w["btn_capturar"].config(text="⏹ PARAR (M)", fg="white", bg="#9333ea")
                    print(f"Modo captura ativado para '{nome_g}' — pressione M para capturar")

            btn_capturar.config(command=_toggle_captura_hotkey)

            # Excluir gaveta
            def _excluir_gaveta(i=idx, w=widget_info):
                nome_g = w["nome"]
                # Desativa hotkey se ativa para essa gaveta
                if _capture_hotkey_active[0] == nome_g:
                    try:
                        keyboard.remove_hotkey('m')
                    except Exception:
                        pass
                    _capture_hotkey_active[0] = None
                # Remove pasta
                pasta_g = os.path.join(CAPTURA_DIR, nome_g)
                if os.path.isdir(pasta_g):
                    shutil.rmtree(pasta_g)
                # Remove da lista
                captura_gavetas[:] = [g for g in captura_gavetas if g["nome"] != nome_g]
                print(f"🗑 Gaveta '{nome_g}' excluída.")
                _refresh_capture_drawers()

            btn_excluir.config(command=_excluir_gaveta)

    def _update_scan_toggle_btn():
        """Atualiza o botão de scan na tela de captura."""
        btn = _capture_setup_widgets.get("btn_scan_toggle")
        if btn is None:
            return
        if captura_modo_ativo:
            btn.config(text="■  PARAR SCAN (G)", bg="#ef4444",
                       activebackground="#dc2626")
        else:
            btn.config(text="▶  INICIAR SCAN (G)", bg="#10b981",
                       activebackground="#059669")

    def open_capture_setup():
        """Mostra a tela de Setup Captura dentro da mesma janela."""
        _build_capture_setup_ui()
        _refresh_capture_drawers()
        _update_scan_toggle_btn()
        main_content_frame.pack_forget()
        capture_setup_frame.pack(fill="both", expand=True)

    def _set_capturando(val):
        global capturando, captura_thread
        capturando = val
        if val:
            captura_thread = threading.Thread(target=_loop_captura, daemon=True)
            captura_thread.start()

    # Registra hotkey global do bot
    keyboard.add_hotkey(bot_hotkey, toggle_bot, suppress=False)

    # ========== SISTEMA DE CAPTURA (GAVETAS) ==========
    janela_captura = None

    def capturar_imagem_cursor(nome_gaveta, preview_label=None):
        """Captura 27x27 ao redor do cursor e salva na pasta captura/<nome>."""
        pasta = os.path.join(CAPTURA_DIR, nome_gaveta)
        os.makedirs(pasta, exist_ok=True)
        x, y = py.position()
        bbox = (x - 13, y - 13, x + 14, y + 14)
        img = ImageGrab.grab(bbox=bbox)
        # Conta arquivos existentes para nome incremental
        existentes = [f for f in os.listdir(pasta) if f.endswith(".png")]
        idx = len(existentes) + 1
        caminho = os.path.join(pasta, f"{nome_gaveta}_{idx}.png")
        img.save(caminho)
        print(f"📸 Imagem capturada: {caminho}")
        # Atualiza preview se possível
        if preview_label is not None:
            try:
                tk_img = ImageTk.PhotoImage(img.resize((40, 40), Image.NEAREST))
                preview_label.config(image=tk_img)
                preview_label.image = tk_img
            except Exception:
                pass
        return caminho

    def _win_click(cx, cy):
        """Move + click via Win32 API — zero overhead Python."""
        ctypes.windll.user32.SetCursorPos(cx, cy)
        ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP

    def scan_captura_loop():
        """
        MAX SPEED scan:
        - MSS (DXGI) — captura GPU nativa, ~3x mais rápido que ImageGrab
        - BGRA→Gray direto (1 conversão, pula RGB)
        - ctypes Win32 mouse (bypassa pyautogui)
        - Idle: 0.05s | Pós-ball: 0.6s
        - SHINY: usa matching por COR (BGR) com precisão 94%+
        """
        global captura_modo_ativo
        print("🟢 Scan MAX SPEED (MSS+DXGI+ctypes)")

        # Pré-carrega refs — GRAY para normal, COLOR (BGR) para shiny
        ref_list_normal = []   # (nome, arq, img_gray)
        ref_list_shiny = []    # (nome, arq, img_bgr)
        for gaveta in list(captura_gavetas):
            if not gaveta.get("ativo", False):
                continue
            nome = gaveta["nome"]
            is_shiny = gaveta.get("shiny", False)
            pasta = os.path.join(CAPTURA_DIR, nome)
            if not os.path.isdir(pasta):
                continue
            for f in sorted(os.listdir(pasta)):
                if f.endswith(".png"):
                    caminho = os.path.join(pasta, f)
                    if is_shiny:
                        img = cv2.imread(caminho, cv2.IMREAD_COLOR)
                        if img is not None:
                            ref_list_shiny.append((nome, f, img))
                    else:
                        img = cv2.imread(caminho, cv2.IMREAD_GRAYSCALE)
                        if img is not None:
                            ref_list_normal.append((nome, f, img))
        total = len(ref_list_normal) + len(ref_list_shiny)
        print(f"📦 {total} refs ({len(ref_list_normal)} normal gray, {len(ref_list_shiny)} shiny color)")

        if total == 0:
            print("⚠ Nenhuma ref encontrada!")
            captura_modo_ativo = False
            return

        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                while captura_modo_ativo:
                    # MSS DXGI: captura BGRA direto da GPU
                    try:
                        raw = sct.grab(monitor)
                        frame = np.frombuffer(raw.bgra, dtype=np.uint8).reshape(raw.height, raw.width, 4)
                    except Exception:
                        continue

                    # Converte conforme necessário (lazy: só converte se tem refs)
                    screen_gray = None
                    screen_bgr = None
                    if ref_list_normal:
                        screen_gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
                    if ref_list_shiny:
                        screen_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    encontrou = False

                    # --- Scan NORMAL (grayscale, threshold 0.84) ---
                    for nome, arq, ref_gray in ref_list_normal:
                        if not captura_modo_ativo:
                            break
                        res = cv2.matchTemplate(screen_gray, ref_gray, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, max_loc = cv2.minMaxLoc(res)
                        if max_val >= 0.84:
                            h, w = ref_gray.shape
                            cx = max_loc[0] + w // 2
                            cy = max_loc[1] + h // 2
                            ctypes.windll.user32.SetCursorPos(cx, cy)
                            keyboard.press_and_release('t')
                            print(f"🎯 {nome} ({arq}) — ({cx},{cy}) [{max_val:.0%}]")
                            encontrou = True
                            time.sleep(0.6)
                            break

                    # --- Scan SHINY (color BGR, threshold 0.94) ---
                    if not encontrou:
                        for nome, arq, ref_bgr in ref_list_shiny:
                            if not captura_modo_ativo:
                                break
                            res = cv2.matchTemplate(screen_bgr, ref_bgr, cv2.TM_CCOEFF_NORMED)
                            _, max_val, _, max_loc = cv2.minMaxLoc(res)
                            if max_val >= 0.94:
                                h, w = ref_bgr.shape[:2]
                                cx = max_loc[0] + w // 2
                                cy = max_loc[1] + h // 2
                                ctypes.windll.user32.SetCursorPos(cx, cy)
                                keyboard.press_and_release('t')
                                print(f"✨ SHINY {nome} ({arq}) — ({cx},{cy}) [{max_val:.0%}]")
                                encontrou = True
                                time.sleep(0.6)
                                break

                    if not encontrou:
                        time.sleep(0.01)
        except Exception as e:
            print(f"⚠ Erro scan: {e}")

        print("🔴 Scan encerrado.")

    def toggle_captura_global():
        """Liga/desliga o scan global de captura."""
        global captura_modo_ativo, captura_thread_scan, captura_scan_habilitado
        if not bot_active:
            print("⚠ Bot desligado! Ligue primeiro com a hotkey global.")
            return
        if not captura_scan_habilitado:
            print("⚠ Scan desabilitado. Ligue primeiro na interface principal.")
            return
        if captura_modo_ativo:
            captura_modo_ativo = False
            try:
                if update_overlay_scan: update_overlay_scan()
            except Exception:
                pass
            print("Scan de captura desligado.")
        else:
            # Verifica se tem gaveta ativa
            ativas = [g["nome"] for g in captura_gavetas if g.get("ativo", False)]
            if not ativas:
                print("⚠ Nenhuma gaveta ativa! Ative pelo menos uma.")
                return
            captura_modo_ativo = True
            try:
                if update_overlay_scan: update_overlay_scan()
            except Exception:
                pass
            captura_thread_scan = threading.Thread(target=scan_captura_loop, daemon=True)
            captura_thread_scan.start()
            print(f"Scan de captura ligado! Gavetas ativas: {ativas}")

    # Hotkey G — suppress=False para poder digitar "g" normalmente no jogo
    keyboard.add_hotkey('g', toggle_captura_global, suppress=False)

    def abrir_captura():
        nonlocal janela_captura
        if janela_captura is not None and janela_captura.winfo_exists():
            janela_captura.lift()
            return

        janela_captura = tk.Toplevel(root)
        janela_captura.title("📷 Captura de Pokémon")
        janela_captura.geometry("450x500")
        janela_captura.resizable(False, True)
        janela_captura.configure(bg="#1e1e2e")

        # Header
        header = tk.Frame(janela_captura, bg="#1e1e2e")
        header.pack(fill="x", padx=15, pady=(15, 5))
        tk.Label(header, text="📷 Gavetas de Captura", font=("Arial", 14, "bold"),
                 fg="#00d4ff", bg="#1e1e2e").pack(side="left")

        # Botão global de scan
        btn_captura_toggle_win = tk.Button(header, text="▶ Iniciar Scan (G)" if not captura_modo_ativo else "■ Parar Scan (G)",
                                       font=("Arial", 9, "bold"),
                                       bg="#4caf50" if not captura_modo_ativo else "#f44336",
                                       fg="white", bd=0, padx=10, pady=3,
                                       command=toggle_captura_global)
        btn_captura_toggle_win.pack(side="right")

        # scrollable area para gavetas
        canvas_frame = tk.Frame(janela_captura, bg="#1e1e2e")
        canvas_frame.pack(fill="both", expand=True, padx=15, pady=5)

        canvas_cv = tk.Canvas(canvas_frame, bg="#1e1e2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas_cv.yview)
        gavetas_frame = tk.Frame(canvas_cv, bg="#1e1e2e")

        gavetas_frame.bind("<Configure>", lambda e: canvas_cv.configure(scrollregion=canvas_cv.bbox("all")))
        canvas_cv.create_window((0, 0), window=gavetas_frame, anchor="nw")
        canvas_cv.configure(yscrollcommand=scrollbar.set)

        canvas_cv.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        gaveta_widgets = []

        def criar_gaveta_widget(gaveta_data):
            """Cria o widget visual de uma gaveta."""
            idx = len(gaveta_widgets)
            nome = gaveta_data["nome"]

            # Card da gaveta
            card = tk.Frame(gavetas_frame, bg="#2a2a3d", bd=1, relief="groove")
            card.pack(fill="x", pady=4, padx=5)

            # Linha principal (clicável para expandir)
            row_main = tk.Frame(card, bg="#2a2a3d")
            row_main.pack(fill="x", padx=8, pady=6)

            # Toggle ativo/desativo
            ativo_var = tk.BooleanVar(value=gaveta_data.get("ativo", False))

            def toggle_gaveta(idx=idx, var=ativo_var):
                captura_gavetas[idx]["ativo"] = var.get()
                status = "ON" if var.get() else "OFF"
                print(f"Gaveta '{captura_gavetas[idx]['nome']}' → {status}")

            chk = tk.Checkbutton(row_main, variable=ativo_var, command=toggle_gaveta,
                                 bg="#2a2a3d", activebackground="#2a2a3d",
                                 selectcolor="#00ff88")
            chk.pack(side="left")

            tk.Label(row_main, text=f"🗂 {nome}", font=("Arial", 11, "bold"),
                     fg="#e0e0e0", bg="#2a2a3d").pack(side="left", padx=5)

            # Contar imagens existentes
            pasta = os.path.join(CAPTURA_DIR, nome)
            n_imgs = len([f for f in os.listdir(pasta) if f.endswith(".png")]) if os.path.isdir(pasta) else 0
            lbl_count = tk.Label(row_main, text=f"({n_imgs} imgs)", font=("Consolas", 9),
                                 fg="#888888", bg="#2a2a3d")
            lbl_count.pack(side="left", padx=5)

            # Conteúdo expandível (inicialmente oculto)
            detail = tk.Frame(card, bg="#2a2a3d")
            is_expanded = [False]

            def toggle_expand():
                if is_expanded[0]:
                    detail.pack_forget()
                    btn_expand.config(text="▼")
                    is_expanded[0] = False
                else:
                    detail.pack(fill="x", padx=10, pady=(0, 8))
                    btn_expand.config(text="▲")
                    is_expanded[0] = True
                    # Atualiza preview das imagens
                    atualizar_preview()

            btn_expand = tk.Button(row_main, text="▼", font=("Consolas", 10),
                                   bg="#3a3a5d", fg="white", bd=0, padx=6,
                                   command=toggle_expand)
            btn_expand.pack(side="right")

            # Botão captura rápida
            preview_lbl = tk.Label(detail, bg="#2a2a3d")
            captura_hotkey_ativa = [False]  # estado do modo captura por gaveta

            def captura_rapida(nome=nome, preview=preview_lbl, lbl_c=lbl_count, p=pasta):
                capturar_imagem_cursor(nome, preview)
                n = len([f for f in os.listdir(p) if f.endswith(".png")]) if os.path.isdir(p) else 0
                lbl_c.config(text=f"({n} imgs)")
                atualizar_preview()

            def toggle_captura_hotkey(nome=nome, preview=preview_lbl, lbl_c=lbl_count, p=pasta):
                if captura_hotkey_ativa[0]:
                    # Desativar
                    try:
                        keyboard.remove_hotkey('m')
                    except Exception:
                        pass
                    captura_hotkey_ativa[0] = False
                    btn_captura.config(text="📸 Capturar (M)", bg="#7c3aed")
                    print(f"Modo captura desativado para '{nome}'")
                else:
                    # Ativar — hotkey M captura imagem
                    def on_m():
                        capturar_imagem_cursor(nome, preview)
                        n = len([f for f in os.listdir(p) if f.endswith(".png")]) if os.path.isdir(p) else 0
                        lbl_c.config(text=f"({n} imgs)")
                        try:
                            atualizar_preview()
                        except Exception:
                            pass
                    keyboard.add_hotkey('m', on_m)
                    captura_hotkey_ativa[0] = True
                    btn_captura.config(text="⏹ Parar (M)", bg="#f44336")
                    print(f"Modo captura ativado para '{nome}' — pressione M para capturar")

            btn_row = tk.Frame(detail, bg="#2a2a3d")
            btn_row.pack(fill="x", pady=4)

            btn_captura = tk.Button(btn_row, text="📸 Capturar (M)", font=("Arial", 9, "bold"),
                      bg="#7c3aed", fg="white", bd=0, padx=10, pady=4,
                      command=toggle_captura_hotkey)
            btn_captura.pack(side="left", padx=4)

            def excluir_gaveta(idx=idx, card_ref=card):
                nome_g = captura_gavetas[idx]["nome"]
                # Remove a pasta do disco
                pasta_g = os.path.join(CAPTURA_DIR, nome_g)
                if os.path.isdir(pasta_g):
                    shutil.rmtree(pasta_g)
                captura_gavetas.pop(idx)
                card_ref.destroy()
                # Re-index remaining widgets
                gaveta_widgets.pop(idx)
                print(f"🗑 Gaveta '{nome_g}' excluída (pasta removida).")

            tk.Button(btn_row, text="🗑 Excluir", font=("Arial", 9),
                      bg="#f44336", fg="white", bd=0, padx=10, pady=4,
                      command=excluir_gaveta).pack(side="right", padx=4)

            # Preview das imagens salvas
            imgs_frame = tk.Frame(detail, bg="#2a2a3d")
            imgs_frame.pack(fill="x", pady=4)

            def atualizar_preview():
                for w in imgs_frame.winfo_children():
                    w.destroy()
                pasta_g = os.path.join(CAPTURA_DIR, nome)
                if not os.path.isdir(pasta_g):
                    return
                arquivos = sorted([f for f in os.listdir(pasta_g) if f.endswith(".png")])
                for arq_name in arquivos[:10]:  # max 10 previews
                    try:
                        img_path = os.path.join(pasta_g, arq_name)
                        pil_img = Image.open(img_path).resize((36, 36), Image.NEAREST)
                        tk_img = ImageTk.PhotoImage(pil_img)
                        img_container = tk.Frame(imgs_frame, bg="#2a2a3d")
                        img_container.pack(side="left", padx=2)
                        img_lbl = tk.Label(img_container, image=tk_img, bg="#2a2a3d")
                        img_lbl.image = tk_img
                        img_lbl.pack()
                        # Botão mini para excluir imagem individual
                        def del_img(p=img_path, c=img_container):
                            try:
                                os.remove(p)
                                c.destroy()
                                n = len([f for f in os.listdir(pasta_g) if f.endswith(".png")])
                                lbl_count.config(text=f"({n} imgs)")
                                print(f"Imagem removida: {p}")
                            except Exception as ex:
                                print(f"Erro ao remover: {ex}")
                        tk.Button(img_container, text="✕", font=("Arial", 6),
                                  bg="#ff3b3b", fg="white", bd=0, padx=2, pady=0,
                                  command=del_img).pack()
                    except Exception:
                        pass

            preview_lbl.pack(pady=2)
            gaveta_widgets.append({"card": card, "gaveta": gaveta_data})

        def adicionar_gaveta():
            """Abre popup para informar nome e cria a gaveta."""
            popup = tk.Toplevel(janela_captura)
            popup.title("Nova Gaveta")
            popup.geometry("300x130")
            popup.resizable(False, False)
            popup.configure(bg="#1e1e2e")

            tk.Label(popup, text="Nome do Pokémon:", font=("Arial", 11),
                     fg="#e0e0e0", bg="#1e1e2e").pack(pady=(15, 5))
            entry_nome = tk.Entry(popup, font=("Arial", 12), width=20,
                                  bg="#12121a", fg="white", insertbackground="white")
            entry_nome.pack()
            entry_nome.focus_set()

            def confirmar():
                nome = entry_nome.get().strip()
                if not nome:
                    return
                # Cria pasta
                os.makedirs(os.path.join(CAPTURA_DIR, nome), exist_ok=True)
                gaveta_data = {"nome": nome, "ativo": False, "shiny": False}
                captura_gavetas.append(gaveta_data)
                criar_gaveta_widget(gaveta_data)
                print(f"📂 Gaveta '{nome}' criada.")
                popup.destroy()

            entry_nome.bind("<Return>", lambda e: confirmar())
            tk.Button(popup, text="✅ Criar", font=("Arial", 11, "bold"),
                      bg="#7c3aed", fg="white", bd=0, padx=15, pady=5,
                      command=confirmar).pack(pady=10)

        # Botão +
        add_frame = tk.Frame(janela_captura, bg="#1e1e2e")
        add_frame.pack(fill="x", padx=15, pady=(5, 15))
        tk.Button(add_frame, text="➕ Nova Gaveta", font=("Arial", 11, "bold"),
                  bg="#00d4ff", fg="#1e1e2e", bd=0, padx=15, pady=6,
                  command=adicionar_gaveta).pack()

        # Carrega gavetas existentes da pasta captura/
        if os.path.isdir(CAPTURA_DIR):
            for pasta_nome in sorted(os.listdir(CAPTURA_DIR)):
                pasta_full = os.path.join(CAPTURA_DIR, pasta_nome)
                if os.path.isdir(pasta_full):
                    # Verifica se já existe na lista
                    if not any(g["nome"] == pasta_nome for g in captura_gavetas):
                        gaveta_data = {"nome": pasta_nome, "ativo": False}
                        captura_gavetas.append(gaveta_data)
                    else:
                        gaveta_data = next(g for g in captura_gavetas if g["nome"] == pasta_nome)
                    criar_gaveta_widget(gaveta_data)

        def on_close_captura():
            nonlocal janela_captura
            janela_captura.destroy()
            janela_captura = None

        janela_captura.protocol("WM_DELETE_WINDOW", on_close_captura)

    # Botão Captura na tela principal (será posicionado depois junto com o resto)
    # (movido para a seção de botões principais abaixo)
    
    def atualizar_perfil_label():
        perfil_label.config(text=f" {perfil_ativo.upper()}")

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

        # Lista dinâmica de ataques
        attack_rows = []

        def save_key():
            global pokestop_key, pokemedi_key, revive_key
            global pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4, pokeattack_key5
            global pokeattack_key6, pokeattack_key7, pokeattack_key8, pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12
            global pokestop_delay, pokemedi_delay
            global pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5
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
            revive_key = entry_revive.get()
            combo_start_key = entry_iniciar_combo.get()

            # Coleta ataques dinâmicos
            keys = []
            delays = []
            for row in attack_rows:
                keys.append(row["entry_key"].get())
                delays.append(get_delay(row["entry_delay"]))
            # Preenche até 12
            while len(keys) < 12:
                keys.append("")
                delays.append(0.5)

            pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4 = keys[0], keys[1], keys[2], keys[3]
            pokeattack_key5, pokeattack_key6, pokeattack_key7, pokeattack_key8 = keys[4], keys[5], keys[6], keys[7]
            pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12 = keys[8], keys[9], keys[10], keys[11]
            pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4 = delays[0], delays[1], delays[2], delays[3]
            pokeattack_delay5, pokeattack_delay6, pokeattack_delay7, pokeattack_delay8 = delays[4], delays[5], delays[6], delays[7]
            pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12 = delays[8], delays[9], delays[10], delays[11]

            # Coleta nightmare attacks
            global nightmare_attacks, combo_mode_active
            nightmare_attacks = []
            for nm_row in nightmare_rows:
                k1 = nm_row["entry_key1"].get()
                k2 = nm_row["entry_key2"].get() if nm_row["entry_key2"] else ""
                d = get_delay(nm_row["entry_delay"])
                rtype = nm_row["type"]
                if k1 or k2:
                    nightmare_attacks.append({"key1": k1, "key2": k2, "delay": d, "type": rtype})

            # Salva o modo ativo
            combo_mode_active = combo_mode.get()

            print(f"Configurado! Modo: {combo_mode_active}")
            salvar_perfil_atual(perfil_ativo)

        janela_combo = tk.Toplevel(root)
        janela_combo.title("Configuração do Combo")
        janela_combo.geometry("420x500")
        janela_combo.resizable(False, True)
        janela_combo.iconphoto(True, icon_photo)

        # ── Bloco centralizado com grid para alinhar tudo ──
        grid_container = tk.Frame(janela_combo)
        grid_container.pack(pady=8)

        # Linha 0 — Combo Start
        tk.Label(grid_container, text="🎮 Combo Start", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(5, 10), pady=4)
        tk.Label(grid_container, text="Key:", font=("Arial", 9)).grid(row=0, column=1, sticky="e", padx=2, pady=4)
        entry_iniciar_combo = tk.Entry(grid_container, width=6)
        entry_iniciar_combo.insert(0, combo_start_key)
        entry_iniciar_combo.grid(row=0, column=2, padx=2, pady=4)

        # Separador
        tk.Frame(grid_container, height=1, bg="#cccccc").grid(row=1, column=0, columnspan=5, sticky="ew", pady=4)

        # Linha 2 — Pokestop
        tk.Label(grid_container, text="🛑 Pokestop", font=("Arial", 10, "bold"), fg="#d32f2f").grid(row=2, column=0, sticky="w", padx=(5, 10), pady=4)
        tk.Label(grid_container, text="Key:", font=("Arial", 9)).grid(row=2, column=1, sticky="e", padx=2, pady=4)
        entry_pokestop = tk.Entry(grid_container, width=6)
        entry_pokestop.insert(0, pokestop_key)
        entry_pokestop.grid(row=2, column=2, padx=2, pady=4)
        tk.Label(grid_container, text="Delay:", font=("Arial", 9)).grid(row=2, column=3, sticky="e", padx=2, pady=4)
        entry_pokestop_delay = tk.Entry(grid_container, width=5)
        entry_pokestop_delay.insert(0, str(pokestop_delay))
        entry_pokestop_delay.grid(row=2, column=4, padx=2, pady=4)

        # Linha 3 — Medicine
        tk.Label(grid_container, text="💊 Medicine", font=("Arial", 10, "bold"), fg="#388e3c").grid(row=3, column=0, sticky="w", padx=(5, 10), pady=4)
        tk.Label(grid_container, text="Key:", font=("Arial", 9)).grid(row=3, column=1, sticky="e", padx=2, pady=4)
        entry_medicine = tk.Entry(grid_container, width=6)
        entry_medicine.insert(0, pokemedi_key)
        entry_medicine.grid(row=3, column=2, padx=2, pady=4)
        tk.Label(grid_container, text="Delay:", font=("Arial", 9)).grid(row=3, column=3, sticky="e", padx=2, pady=4)
        entry_medicine_delay = tk.Entry(grid_container, width=5)
        entry_medicine_delay.insert(0, str(pokemedi_delay))
        entry_medicine_delay.grid(row=3, column=4, padx=2, pady=4)

        # Linha 4 — Revive
        tk.Label(grid_container, text="🔄 Revive", font=("Arial", 10, "bold"), fg="#1565c0").grid(row=4, column=0, sticky="w", padx=(5, 10), pady=4)
        tk.Label(grid_container, text="Key:", font=("Arial", 9)).grid(row=4, column=1, sticky="e", padx=2, pady=4)
        entry_revive = tk.Entry(grid_container, width=6)
        entry_revive.insert(0, revive_key)
        entry_revive.grid(row=4, column=2, padx=2, pady=4)

        # Separador
        tk.Frame(grid_container, height=1, bg="#cccccc").grid(row=5, column=0, columnspan=5, sticky="ew", pady=4)

        # ── ⚔ Attacks ──
        # Toggle HUNT NORMAL / NIGHTMARE
        mode_frame = tk.Frame(janela_combo)
        mode_frame.pack(pady=5)

        combo_mode = tk.StringVar(value="HUNT NORMAL")

        # Wrapper que contém ambos os modos — sempre empacotado
        content_wrapper = tk.Frame(janela_combo)
        content_wrapper.pack(fill="both", expand=True, padx=10)

        def select_hunt():
            combo_mode.set("HUNT NORMAL")
            btn_hunt.config(bg="#4caf50", fg="white", relief="sunken")
            btn_nightmare.config(bg="#555555", fg="#aaaaaa", relief="raised")
            nightmare_container.pack_forget()
            nm_btn_add_frame.pack_forget()
            hunt_container.pack(in_=content_wrapper, fill="both", expand=True)
            btn_add_frame.pack(in_=content_wrapper, pady=5)

        def select_nightmare():
            combo_mode.set("NIGHTMARE")
            btn_nightmare.config(bg="#b71c1c", fg="white", relief="sunken")
            btn_hunt.config(bg="#555555", fg="#aaaaaa", relief="raised")
            hunt_container.pack_forget()
            btn_add_frame.pack_forget()
            nightmare_container.pack(in_=content_wrapper, fill="both", expand=True)
            nm_btn_add_frame.pack(in_=content_wrapper, pady=5)

        btn_hunt = tk.Button(mode_frame, text="⚔ HUNT NORMAL", font=("Arial", 10, "bold"),
                             bg="#4caf50", fg="white", relief="sunken", width=16, command=select_hunt)
        btn_hunt.pack(side="left", padx=4)

        btn_nightmare = tk.Button(mode_frame, text="💀 NIGHTMARE", font=("Arial", 10, "bold"),
                                  bg="#555555", fg="#aaaaaa", relief="raised", width=16, command=select_nightmare)
        btn_nightmare.pack(side="left", padx=4)

        # ── HUNT NORMAL container ──
        hunt_container = tk.Frame(content_wrapper)
        hunt_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(hunt_container, highlightthickness=0, height=150)
        scrollbar = tk.Scrollbar(hunt_container, orient="vertical", command=canvas.yview)
        attacks_frame = tk.Frame(canvas)
        attacks_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=attacks_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def renumerar():
            for i, r in enumerate(attack_rows):
                r["label"].config(text=f"⚔ {i + 1}")

        def add_attack_row(key_val="", delay_val="0.5"):
            if len(attack_rows) >= 12:
                print("Máximo de 12 ataques!")
                return

            row_frame = tk.Frame(attacks_frame)
            row_frame.pack(pady=2, fill="x")

            idx = len(attack_rows) + 1
            lbl_num = tk.Label(row_frame, text=f"⚔ {idx}", font=("Arial", 9, "bold"), width=4)
            lbl_num.pack(side="left", padx=2)

            tk.Label(row_frame, text="Key:").pack(side="left", padx=1)
            entry_key = tk.Entry(row_frame, width=6)
            entry_key.insert(0, key_val)
            entry_key.pack(side="left", padx=2)

            tk.Label(row_frame, text="Delay:").pack(side="left", padx=1)
            entry_delay = tk.Entry(row_frame, width=5)
            entry_delay.insert(0, str(delay_val))
            entry_delay.pack(side="left", padx=2)

            row_data = {"frame": row_frame, "entry_key": entry_key, "entry_delay": entry_delay, "label": lbl_num}

            def remove_row():
                attack_rows.remove(row_data)
                row_frame.destroy()
                renumerar()

            btn_remove = tk.Button(row_frame, text="🗑", fg="red", command=remove_row, relief="flat", font=("Arial", 9))
            btn_remove.pack(side="left", padx=3)

            attack_rows.append(row_data)

        # Botão ➕ para adicionar ataques
        btn_add_frame = tk.Frame(content_wrapper)
        btn_add_frame.pack(pady=5)
        tk.Button(btn_add_frame, text="➕ Adicionar Attack", font=("Arial", 10, "bold"),
                  command=add_attack_row, bg="#4caf50", fg="white", relief="groove").pack()

        # Carrega ataques já configurados
        existing_attacks = [
            (pokeattack_key1, pokeattack_delay1), (pokeattack_key2, pokeattack_delay2),
            (pokeattack_key3, pokeattack_delay3), (pokeattack_key4, pokeattack_delay4),
            (pokeattack_key5, pokeattack_delay5), (pokeattack_key6, pokeattack_delay6),
            (pokeattack_key7, pokeattack_delay7), (pokeattack_key8, pokeattack_delay8),
            (pokeattack_key9, pokeattack_delay9), (pokeattack_key10, pokeattack_delay10),
            (pokeattack_key11, pokeattack_delay11), (pokeattack_key12, pokeattack_delay12),
        ]
        for key_val, delay_val in existing_attacks:
            if key_val:
                add_attack_row(key_val, delay_val)

        # ── NIGHTMARE container ──
        nightmare_container = tk.Frame(content_wrapper)
        nightmare_rows = []

        nm_canvas = tk.Canvas(nightmare_container, highlightthickness=0, height=150)
        nm_scrollbar = tk.Scrollbar(nightmare_container, orient="vertical", command=nm_canvas.yview)
        nm_attacks_frame = tk.Frame(nm_canvas)
        nm_attacks_frame.bind("<Configure>", lambda e: nm_canvas.configure(scrollregion=nm_canvas.bbox("all")))
        nm_canvas.create_window((0, 0), window=nm_attacks_frame, anchor="nw")
        nm_canvas.configure(yscrollcommand=nm_scrollbar.set)
        nm_canvas.pack(side="left", fill="both", expand=True)
        nm_scrollbar.pack(side="right", fill="y")

        def nm_renumerar():
            for i, r in enumerate(nightmare_rows):
                emoji = "🔴" if r["type"] == "pokeball" else "💀"
                r["label"].config(text=f"{emoji} {i + 1}")

        def add_nightmare_row(key1_val="", key2_val="", delay_val="0.5", row_type="attack"):
            """row_type: 'attack' (1 campo) ou 'pokeball' (2 campos combo key)"""
            if len(nightmare_rows) >= 20:
                print("Máximo de 20 itens nightmare!")
                return

            row_frame = tk.Frame(nm_attacks_frame)
            row_frame.pack(pady=2, fill="x")

            idx = len(nightmare_rows) + 1
            emoji = "🔴" if row_type == "pokeball" else "💀"
            lbl_num = tk.Label(row_frame, text=f"{emoji} {idx}", font=("Arial", 9, "bold"), width=4)
            lbl_num.pack(side="left", padx=2)

            entry_key2 = None  # só existe no tipo pokeball

            if row_type == "pokeball":
                # Troca de pokemon: 2 campos (ex: alt + 1)
                tk.Label(row_frame, text="Key1:", font=("Arial", 8)).pack(side="left", padx=1)
                entry_key1 = tk.Entry(row_frame, width=5)
                entry_key1.insert(0, key1_val)
                entry_key1.pack(side="left", padx=1)

                tk.Label(row_frame, text="+", font=("Arial", 9, "bold")).pack(side="left")

                tk.Label(row_frame, text="Key2:", font=("Arial", 8)).pack(side="left", padx=1)
                entry_key2 = tk.Entry(row_frame, width=5)
                entry_key2.insert(0, key2_val)
                entry_key2.pack(side="left", padx=1)
            else:
                # Attack: 1 campo só
                tk.Label(row_frame, text="Key:", font=("Arial", 8)).pack(side="left", padx=1)
                entry_key1 = tk.Entry(row_frame, width=6)
                entry_key1.insert(0, key1_val)
                entry_key1.pack(side="left", padx=2)

            tk.Label(row_frame, text="Delay:", font=("Arial", 8)).pack(side="left", padx=1)
            entry_delay = tk.Entry(row_frame, width=4)
            entry_delay.insert(0, str(delay_val))
            entry_delay.pack(side="left", padx=1)

            row_data = {"frame": row_frame, "entry_key1": entry_key1, "entry_key2": entry_key2,
                        "entry_delay": entry_delay, "label": lbl_num, "type": row_type}

            def remove_nm_row():
                nightmare_rows.remove(row_data)
                row_frame.destroy()
                nm_renumerar()

            tk.Button(row_frame, text="🗑", fg="red", command=remove_nm_row, relief="flat", font=("Arial", 9)).pack(side="left", padx=3)

            nightmare_rows.append(row_data)

        nm_btn_add_frame = tk.Frame(content_wrapper)
        nm_btn_frame_inner = tk.Frame(nm_btn_add_frame)
        nm_btn_frame_inner.pack()
        tk.Button(nm_btn_frame_inner, text="💀 Adicionar Atk", font=("Arial", 9, "bold"),
                  command=lambda: add_nightmare_row(row_type="attack"), bg="#b71c1c", fg="white", relief="groove").pack(side="left", padx=4)
        tk.Button(nm_btn_frame_inner, text="🔴 Troca de Pokemon", font=("Arial", 9, "bold"),
                  command=lambda: add_nightmare_row(row_type="pokeball"), bg="#e65100", fg="white", relief="groove").pack(side="left", padx=4)

        # Carrega nightmare attacks do perfil
        for nm_atk in nightmare_attacks:
            add_nightmare_row(nm_atk.get("key1", ""), nm_atk.get("key2", ""), nm_atk.get("delay", 0.5), nm_atk.get("type", "attack"))

        # Abre no modo salvo
        if combo_mode_active == "NIGHTMARE":
            select_nightmare()

        # Botão Salvar
        save_btn = tk.Button(janela_combo, text="💾 Salvar", font=("Arial", 11, "bold"),
                  command=save_key, bg="#1976d2", fg="white", relief="groove")
        save_btn.pack(pady=10)

        def on_close():
            nonlocal janela_combo
            canvas.unbind_all("<MouseWheel>")
            janela_combo.destroy()
            janela_combo = None
        janela_combo.protocol("WM_DELETE_WINDOW", on_close)

    def selecionar_perfil():
        """Mostra a tela de seleção de perfil dentro da mesma janela."""
        _build_select_profile_ui()
        _refresh_select_profile_list()
        main_content_frame.pack_forget()
        select_profile_frame.pack(fill="both", expand=True)

    _select_profile_built = [False]
    _select_profile_widgets = {}
    _selected_profile_var = [None]  # perfil selecionado na lista

    def _voltar_do_selecionar_perfil():
        """Volta da tela de selecionar perfil para a tela principal."""
        select_profile_frame.pack_forget()
        main_content_frame.pack(fill="both", expand=True)

    def _refresh_select_profile_list():
        """Reconstrói a lista de cards de perfil."""
        cards_container = _select_profile_widgets.get("cards_container")
        if not cards_container:
            return
        # Limpa cards antigos
        for w in cards_container.winfo_children():
            w.destroy()

        _selected_profile_var[0] = perfil_ativo
        _select_profile_widgets["card_buttons"] = []

        # Cores para avatares (rotação)
        avatar_colors = [
            ("#1e3a5f", "#3b82f6"),  # azul
            ("#1a3a1a", "#22c55e"),  # verde
            ("#3a1a1a", "#ef4444"),  # vermelho
            ("#3a2a1a", "#eab308"),  # amarelo
            ("#2a1a3a", "#a855f7"),  # roxo
            ("#1a3a3a", "#22d3ee"),  # cyan
        ]

        def _on_select(nome):
            _selected_profile_var[0] = nome
            _update_card_visuals()

        def _update_card_visuals():
            for btn_data in _select_profile_widgets.get("card_buttons", []):
                nome = btn_data["nome"]
                card = btn_data["card"]
                inner = btn_data["inner"]
                name_lbl = btn_data["name_lbl"]
                check_lbl = btn_data["check_lbl"]
                if nome == _selected_profile_var[0]:
                    card.config(highlightbackground="#3b82f6", bg="#1a1a1e")
                    inner.config(bg="#1a1a1e")
                    name_lbl.config(fg="white", bg="#1a1a1e")
                    check_lbl.config(text="●", fg="#3b82f6", bg="#1a1a1e")
                else:
                    card.config(highlightbackground="#27272a", bg="#151518")
                    inner.config(bg="#151518")
                    name_lbl.config(fg="#52525b", bg="#151518")
                    check_lbl.config(text="", bg="#151518")

        for i, nome in enumerate(perfis.keys()):
            bg_color, fg_color = avatar_colors[i % len(avatar_colors)]
            is_active = (nome == perfil_ativo)

            card_bg = "#1a1a1e" if is_active else "#151518"
            border_color = "#3b82f6" if is_active else "#27272a"

            card = tk.Frame(cards_container, bg=card_bg,
                            highlightbackground=border_color, highlightthickness=2,
                            cursor="hand2")
            card.pack(fill="x", pady=4, padx=4)

            inner = tk.Frame(card, bg=card_bg)
            inner.pack(fill="x", padx=10, pady=10)

            # Avatar
            avatar = tk.Frame(inner, bg=bg_color, width=40, height=40)
            avatar.pack(side="left", padx=(0, 12))
            avatar.pack_propagate(False)
            tk.Label(avatar, text="👤", font=("Segoe UI Emoji", 14),
                     bg=bg_color, fg=fg_color).pack(expand=True)

            # Nome
            name_lbl = tk.Label(inner, text=nome.upper(),
                                font=("Consolas", 10, "bold"),
                                bg=card_bg,
                                fg="white" if is_active else "#52525b")
            name_lbl.pack(side="left")

            # Check
            check_lbl = tk.Label(inner, text="●" if is_active else "",
                                 font=("Consolas", 14, "bold"),
                                 bg=card_bg, fg="#3b82f6")
            check_lbl.pack(side="right", padx=(0, 4))

            btn_data = {"nome": nome, "card": card, "inner": inner, "name_lbl": name_lbl, "check_lbl": check_lbl}
            _select_profile_widgets["card_buttons"].append(btn_data)

            # Bind click em todos os widgets do card
            def _bind_click(widget, n=nome):
                widget.bind("<Button-1>", lambda e: _on_select(n))
                for child in widget.winfo_children():
                    _bind_click(child, n)
            _bind_click(card)

        _update_card_visuals()

        # Se não tem perfis
        if not perfis:
            tk.Label(cards_container, text="Nenhum perfil encontrado...",
                     font=("Consolas", 8, "bold italic"),
                     bg="#121214", fg="#52525b").pack(pady=30)

    def _build_select_profile_ui():
        """Constrói a UI de seleção de perfil dentro de select_profile_frame (uma vez só)."""
        if _select_profile_built[0]:
            return

        _BG = "#121214"
        _DIM = "#71717a"
        _BLUE = "#3b82f6"
        _BORDER = "#27272a"

        # ── HEADER ──
        header = tk.Frame(select_profile_frame, bg=_BG)
        header.pack(fill="x", padx=16, pady=(14, 0))

        btn_voltar = tk.Button(
            header, text="❮  VOLTAR", font=("Consolas", 9, "bold"),
            bg=_BG, fg=_DIM, bd=0, cursor="hand2",
            activebackground=_BG, activeforeground="white",
            command=_voltar_do_selecionar_perfil
        )
        btn_voltar.pack(side="left")

        title_frame = tk.Frame(header, bg=_BG)
        title_frame.pack(side="right")
        tk.Label(title_frame, text="👥", font=("Segoe UI Emoji", 12),
                 bg=_BG, fg=_BLUE).pack(side="left", padx=(0, 4))
        tk.Label(title_frame, text="ESCOLHER", font=("Consolas", 13, "bold italic"),
                 bg=_BG, fg=_BLUE).pack(side="left")

        tk.Frame(select_profile_frame, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── SCROLLABLE LIST ──
        list_frame = tk.Frame(select_profile_frame, bg=_BG)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(8, 0))

        list_canvas = tk.Canvas(list_frame, bg=_BG, highlightthickness=0)
        list_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=list_canvas.yview)
        cards_container = tk.Frame(list_canvas, bg=_BG)

        cards_container.bind("<Configure>",
                             lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0, 0), window=cards_container, anchor="nw")
        list_canvas.configure(yscrollcommand=list_scrollbar.set)

        list_canvas.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")

        # Faz os cards preencherem a largura do canvas
        def _resize_cards(event):
            list_canvas.itemconfig(list_canvas.find_all()[0], width=event.width)
        list_canvas.bind("<Configure>", _resize_cards)

        # Mouse wheel scroll
        def _on_mousewheel(event):
            list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        list_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        _select_profile_widgets["cards_container"] = cards_container

        # ── BOTÃO APLICAR ──
        def _aplicar_selecao():
            nome = _selected_profile_var[0]
            if nome and nome in perfis:
                aplicar_perfil(nome)
                atualizar_perfil_label()
                print(f"Perfil selecionado: {nome}")
                _voltar_do_selecionar_perfil()

        btn_aplicar = tk.Button(
            select_profile_frame, text="🖱  APLICAR SELEÇÃO",
            font=("Consolas", 12, "bold"), bg=_BLUE, fg="white",
            activebackground="#2563eb", activeforeground="white",
            bd=0, pady=10, cursor="hand2",
            command=_aplicar_selecao
        )
        btn_aplicar.pack(fill="x", padx=16, pady=(10, 6))

        # Speaker dots
        dots = tk.Frame(select_profile_frame, bg=_BG)
        dots.pack(pady=(0, 6))
        for _ in range(3):
            tk.Canvas(dots, width=5, height=5, bg=_BG, highlightthickness=0)\
              .pack(side="left", padx=2)

        _select_profile_built[0] = True

    _create_profile_built = [False]
    _create_profile_widgets = {}

    def _voltar_do_criar_perfil():
        """Volta da tela de criar perfil para a tela principal."""
        create_profile_frame.pack_forget()
        main_content_frame.pack(fill="both", expand=True)

    def _build_create_profile_ui():
        """Constrói a UI do Trainer Card dentro de create_profile_frame (uma vez só)."""
        if _create_profile_built[0]:
            return

        _BG = "#121214"
        _CARD_GREEN = "#9da33a"
        _CARD_DARK = "#2d2f11"
        _CARD_LIGHT = "#bdc54a"
        _CARD_INPUT_BG = "#f8f9e6"
        _DIM = "#71717a"
        _CYAN = "#22d3ee"
        _YELLOW = "#eab308"
        _BORDER = "#27272a"

        # ── HEADER ──
        header = tk.Frame(create_profile_frame, bg=_BG)
        header.pack(fill="x", padx=16, pady=(14, 0))

        btn_voltar = tk.Button(
            header, text="❮  VOLTAR", font=("Consolas", 9, "bold"),
            bg=_BG, fg=_DIM, bd=0, cursor="hand2",
            activebackground=_BG, activeforeground="white",
            command=_voltar_do_criar_perfil
        )
        btn_voltar.pack(side="left")

        title_frame = tk.Frame(header, bg=_BG)
        title_frame.pack(side="right")
        tk.Label(title_frame, text="👤", font=("Segoe UI Emoji", 12),
                 bg=_BG, fg=_YELLOW).pack(side="left", padx=(0, 4))
        tk.Label(title_frame, text="NOVO PERFIL", font=("Consolas", 13, "bold italic"),
                 bg=_BG, fg=_YELLOW).pack(side="left")

        tk.Frame(create_profile_frame, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── CONTENT AREA ──
        content = tk.Frame(create_profile_frame, bg=_BG)
        content.pack(fill="both", expand=True, padx=16, pady=(10, 0))

        # ═══ TRAINER CARD ═══
        card = tk.Frame(content, bg=_CARD_GREEN, bd=2, relief="ridge",
                        highlightbackground=_CARD_DARK, highlightthickness=2)
        card.pack(fill="both", expand=True, pady=(6, 0))

        # Card inner padding
        card_inner = tk.Frame(card, bg=_CARD_GREEN)
        card_inner.pack(fill="both", expand=True, padx=10, pady=8)

        # Card header
        card_header = tk.Frame(card_inner, bg=_CARD_GREEN)
        card_header.pack(fill="x", pady=(0, 6))
        tk.Label(card_header, text="POKÉMON TRAINER CARD",
                 font=("Consolas", 8, "bold"), bg=_CARD_GREEN,
                 fg=_CARD_DARK).pack(side="left")
        tk.Label(card_header, text="🎮", font=("Segoe UI Emoji", 9),
                 bg=_CARD_GREEN, fg=_CARD_DARK).pack(side="right")

        # Main row: avatar + name input
        main_row = tk.Frame(card_inner, bg=_CARD_GREEN)
        main_row.pack(fill="x", pady=(0, 6))

        # Avatar slot
        avatar_frame = tk.Frame(main_row, bg=_CARD_LIGHT, bd=2,
                                relief="sunken", width=80, height=90)
        avatar_frame.pack(side="left", padx=(0, 10))
        avatar_frame.pack_propagate(False)
        tk.Label(avatar_frame, text="👤", font=("Segoe UI Emoji", 28),
                 bg=_CARD_LIGHT, fg=_CARD_DARK).pack(expand=True)

        # Name input area
        name_area = tk.Frame(main_row, bg=_CARD_GREEN)
        name_area.pack(side="left", fill="both", expand=True)

        tk.Label(name_area, text="NOME DO NOVO PERFIL:",
                 font=("Consolas", 7, "bold"), bg=_CARD_GREEN,
                 fg=_CARD_DARK).pack(anchor="w", pady=(0, 4))

        entry_novo = tk.Entry(name_area, font=("Consolas", 11, "bold"),
                              bg=_CARD_INPUT_BG, fg=_CARD_DARK,
                              insertbackground=_CARD_DARK, bd=2,
                              relief="solid", width=18)
        entry_novo.insert(0, "")
        entry_novo.pack(anchor="w", ipady=4)
        _create_profile_widgets["entry_nome"] = entry_novo

        # Trainer ID
        trainer_id = random.randint(10000, 99999)
        id_frame = tk.Frame(name_area, bg=_CARD_GREEN)
        id_frame.pack(anchor="w", pady=(8, 0))
        _trainer_id_lbl = tk.Label(id_frame, text=f"TRAINER ID: {trainer_id}",
                 font=("Consolas", 7), bg=_CARD_GREEN,
                 fg=_CARD_DARK)
        _trainer_id_lbl.pack(anchor="w")
        _create_profile_widgets["trainer_id_lbl"] = _trainer_id_lbl

        # Bottom section: badges + team
        bottom_row = tk.Frame(card_inner, bg=_CARD_GREEN)
        bottom_row.pack(fill="x", pady=(4, 0))

        # Badges section
        badges_frame = tk.Frame(bottom_row, bg=_CARD_LIGHT, bd=1, relief="groove")
        badges_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))

        badges_inner = tk.Frame(badges_frame, bg=_CARD_LIGHT)
        badges_inner.pack(fill="both", expand=True, padx=6, pady=4)

        tk.Label(badges_inner, text="🏆 INSÍGNIAS",
                 font=("Consolas", 6, "bold"), bg=_CARD_LIGHT,
                 fg=_CARD_DARK).pack(anchor="w", pady=(0, 3))

        badges_grid = tk.Frame(badges_inner, bg=_CARD_LIGHT)
        badges_grid.pack()
        for row in range(2):
            for col in range(4):
                badge = tk.Canvas(badges_grid, width=16, height=16,
                                  bg=_CARD_LIGHT, highlightthickness=0)
                badge.grid(row=row, column=col, padx=2, pady=2)
                badge.create_oval(2, 2, 14, 14, fill=_CARD_GREEN,
                                  outline=_CARD_DARK, width=1)

        # Team section
        team_frame = tk.Frame(bottom_row, bg=_CARD_LIGHT, bd=1, relief="groove")
        team_frame.pack(side="right", fill="both", expand=True, padx=(4, 0))

        team_inner = tk.Frame(team_frame, bg=_CARD_LIGHT)
        team_inner.pack(fill="both", expand=True, padx=6, pady=4)

        tk.Label(team_inner, text="EQUIPA POKÉMON",
                 font=("Consolas", 6, "bold"), bg=_CARD_LIGHT,
                 fg=_CARD_DARK).pack(anchor="w", pady=(0, 3))

        team_grid = tk.Frame(team_inner, bg=_CARD_LIGHT)
        team_grid.pack()
        for row in range(2):
            for col in range(3):
                slot = tk.Frame(team_grid, bg=_CARD_INPUT_BG, bd=1,
                                relief="solid", width=18, height=18)
                slot.grid(row=row, column=col, padx=2, pady=2)
                slot.pack_propagate(False)

        # ── BOTÃO CRIAR PERFIL ──
        def _criar_e_voltar():
            nome = entry_novo.get().strip()
            if not nome:
                return
            if nome in perfis:
                print(f"⚠ Perfil '{nome}' já existe!")
                return
            salvar_perfil_atual(nome)
            aplicar_perfil(nome)
            atualizar_perfil_label()
            print(f"Perfil criado: {nome}")
            entry_novo.delete(0, tk.END)
            _voltar_do_criar_perfil()

        btn_criar = tk.Button(
            create_profile_frame, text="🃏  CRIAR PERFIL",
            font=("Consolas", 12, "bold"), bg=_YELLOW, fg="black",
            activebackground="#fbbf24", activeforeground="black",
            bd=0, pady=10, cursor="hand2",
            command=_criar_e_voltar
        )
        btn_criar.pack(fill="x", padx=16, pady=(10, 6))

        # Enter tambem cria
        entry_novo.bind("<Return>", lambda e: _criar_e_voltar())

        # Speaker dots
        dots = tk.Frame(create_profile_frame, bg=_BG)
        dots.pack(pady=(0, 6))
        for _ in range(3):
            tk.Canvas(dots, width=5, height=5, bg=_BG, highlightthickness=0)\
              .pack(side="left", padx=2)

        _create_profile_built[0] = True

    def criar_perfil():
        """Mostra a tela de criar perfil dentro da mesma janela."""
        _build_create_profile_ui()
        # Limpa o campo e gera novo trainer ID
        entry = _create_profile_widgets.get("entry_nome")
        if entry:
            entry.delete(0, tk.END)
            entry.focus_set()
        id_lbl = _create_profile_widgets.get("trainer_id_lbl")
        if id_lbl:
            id_lbl.config(text=f"TRAINER ID: {random.randint(10000, 99999)}")
        main_content_frame.pack_forget()
        create_profile_frame.pack(fill="both", expand=True)

    _delete_profile_built = [False]
    _delete_profile_widgets = {}
    _delete_selected_var = [None]

    def _voltar_do_excluir_perfil():
        """Volta da tela de excluir perfil para a tela principal."""
        delete_profile_frame.pack_forget()
        main_content_frame.pack(fill="both", expand=True)

    def _refresh_delete_profile_list():
        """Reconstrói a lista de cards para exclusão."""
        cards_container = _delete_profile_widgets.get("cards_container")
        if not cards_container:
            return
        for w in cards_container.winfo_children():
            w.destroy()

        _delete_selected_var[0] = None
        _delete_profile_widgets["card_buttons"] = []

        def _on_select(nome):
            if nome == "default":
                return
            _delete_selected_var[0] = nome
            _update_delete_visuals()

        def _update_delete_visuals():
            for btn_data in _delete_profile_widgets.get("card_buttons", []):
                nome = btn_data["nome"]
                card = btn_data["card"]
                inner = btn_data["inner"]
                icon_frame = btn_data["icon_frame"]
                icon_lbl = btn_data["icon_lbl"]
                name_lbl = btn_data["name_lbl"]
                flame_lbl = btn_data["flame_lbl"]
                is_default = (nome == "default")

                if is_default:
                    card.config(highlightbackground="#27272a", bg="#151518")
                    inner.config(bg="#151518")
                    icon_frame.config(bg="#18181b")
                    icon_lbl.config(bg="#18181b", fg="#3f3f46")
                    name_lbl.config(fg="#3f3f46", bg="#151518")
                    flame_lbl.config(text="", bg="#151518")
                elif nome == _delete_selected_var[0]:
                    card.config(highlightbackground="#ef4444", bg="#1a0505")
                    inner.config(bg="#1a0505")
                    icon_frame.config(bg="#dc2626")
                    icon_lbl.config(bg="#dc2626", fg="white")
                    name_lbl.config(fg="#ef4444", bg="#1a0505")
                    flame_lbl.config(text="🔥", bg="#1a0505")
                else:
                    card.config(highlightbackground="#27272a", bg="#151518")
                    inner.config(bg="#151518")
                    icon_frame.config(bg="#18181b")
                    icon_lbl.config(bg="#18181b", fg="#52525b")
                    name_lbl.config(fg="#52525b", bg="#151518")
                    flame_lbl.config(text="", bg="#151518")

            # Atualiza botão confirmar
            btn = _delete_profile_widgets.get("btn_confirmar")
            if btn:
                if _delete_selected_var[0] and _delete_selected_var[0] != "default":
                    btn.config(bg="#dc2626", fg="white", state="normal", cursor="hand2")
                else:
                    btn.config(bg="#27272a", fg="#52525b", state="disabled", cursor="arrow")

        for nome in perfis.keys():
            is_default = (nome == "default")

            card_bg = "#151518"
            border_color = "#27272a"

            card = tk.Frame(cards_container, bg=card_bg,
                            highlightbackground=border_color, highlightthickness=2,
                            cursor="arrow" if is_default else "hand2")
            card.pack(fill="x", pady=4, padx=4)

            inner = tk.Frame(card, bg=card_bg)
            inner.pack(fill="x", padx=10, pady=10)

            # Ícone lixeira
            icon_frame = tk.Frame(inner, bg="#18181b", width=36, height=36)
            icon_frame.pack(side="left", padx=(0, 12))
            icon_frame.pack_propagate(False)
            icon_lbl = tk.Label(icon_frame, text="🗑", font=("Segoe UI Emoji", 12),
                                bg="#18181b", fg="#3f3f46" if is_default else "#52525b")
            icon_lbl.pack(expand=True)

            # Nome
            name_lbl = tk.Label(inner, text=nome.upper(),
                                font=("Consolas", 10, "bold"),
                                bg=card_bg,
                                fg="#3f3f46" if is_default else "#52525b")
            name_lbl.pack(side="left")

            # Flame indicator
            flame_lbl = tk.Label(inner, text="",
                                 font=("Segoe UI Emoji", 14),
                                 bg=card_bg, fg="#ef4444")
            flame_lbl.pack(side="right", padx=(0, 4))

            btn_data = {"nome": nome, "card": card, "inner": inner,
                        "icon_frame": icon_frame, "icon_lbl": icon_lbl,
                        "name_lbl": name_lbl, "flame_lbl": flame_lbl}
            _delete_profile_widgets["card_buttons"].append(btn_data)

            if not is_default:
                def _bind_click(widget, n=nome):
                    widget.bind("<Button-1>", lambda e: _on_select(n))
                    for child in widget.winfo_children():
                        _bind_click(child, n)
                _bind_click(card)

        _update_delete_visuals()

        if not perfis:
            tk.Label(cards_container, text="Nenhum perfil encontrado...",
                     font=("Consolas", 8, "bold italic"),
                     bg="#121214", fg="#52525b").pack(pady=30)

    def _build_delete_profile_ui():
        """Constrói a UI de exclusão de perfil dentro de delete_profile_frame (uma vez só)."""
        if _delete_profile_built[0]:
            return

        _BG = "#121214"
        _DIM = "#71717a"
        _RED = "#ef4444"
        _DARK_RED = "#dc2626"
        _BORDER = "#27272a"

        # ── HEADER ──
        header = tk.Frame(delete_profile_frame, bg=_BG)
        header.pack(fill="x", padx=16, pady=(14, 0))

        btn_voltar = tk.Button(
            header, text="❮  VOLTAR", font=("Consolas", 9, "bold"),
            bg=_BG, fg=_DIM, bd=0, cursor="hand2",
            activebackground=_BG, activeforeground="white",
            command=_voltar_do_excluir_perfil
        )
        btn_voltar.pack(side="left")

        title_frame = tk.Frame(header, bg=_BG)
        title_frame.pack(side="right")
        tk.Label(title_frame, text="⚠", font=("Segoe UI Emoji", 12),
                 bg=_BG, fg=_RED).pack(side="left", padx=(0, 4))
        tk.Label(title_frame, text="APAGAR", font=("Consolas", 13, "bold italic"),
                 bg=_BG, fg=_RED).pack(side="left")

        tk.Frame(delete_profile_frame, bg="#450a0a", height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── AVISO CRÍTICO ──
        warn_frame = tk.Frame(delete_profile_frame, bg="#1a0505",
                              highlightbackground="#450a0a", highlightthickness=1)
        warn_frame.pack(fill="x", padx=16, pady=(10, 0))

        warn_inner = tk.Frame(warn_frame, bg="#1a0505")
        warn_inner.pack(fill="x", padx=8, pady=8)
        tk.Label(warn_inner, text="⛔", font=("Segoe UI Emoji", 10),
                 bg="#1a0505", fg=_RED).pack(side="left", padx=(0, 8))
        tk.Label(warn_inner,
                 text="ATENÇÃO: A REMOÇÃO DE UM PERFIL É DEFINITIVA\nE APAGARÁ TODOS OS DADOS ASSOCIADOS.",
                 font=("Consolas", 7, "bold"), bg="#1a0505", fg="#fca5a5",
                 justify="left").pack(side="left")

        # ── SCROLLABLE LIST ──
        list_frame = tk.Frame(delete_profile_frame, bg=_BG)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(8, 0))

        list_canvas = tk.Canvas(list_frame, bg=_BG, highlightthickness=0)
        list_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=list_canvas.yview)
        cards_container = tk.Frame(list_canvas, bg=_BG)

        cards_container.bind("<Configure>",
                             lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0, 0), window=cards_container, anchor="nw")
        list_canvas.configure(yscrollcommand=list_scrollbar.set)

        list_canvas.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")

        def _resize_cards(event):
            list_canvas.itemconfig(list_canvas.find_all()[0], width=event.width)
        list_canvas.bind("<Configure>", _resize_cards)

        def _on_mousewheel(event):
            list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        list_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        _delete_profile_widgets["cards_container"] = cards_container

        # ── BOTÃO CONFIRMAR EXCLUSÃO ──
        def _confirmar_exclusao():
            nome = _delete_selected_var[0]
            if nome and nome in perfis and nome != "default":
                excluir_perfil(nome)
                print(f"Perfil excluído: {nome}")
                if perfil_ativo == nome:
                    aplicar_perfil("default")
                    atualizar_perfil_label()
                _voltar_do_excluir_perfil()

        btn_confirmar = tk.Button(
            delete_profile_frame, text="🗑  CONFIRMAR EXCLUSÃO",
            font=("Consolas", 12, "bold"), bg="#27272a", fg="#52525b",
            activebackground="#b91c1c", activeforeground="white",
            bd=0, pady=10, cursor="arrow", state="disabled",
            command=_confirmar_exclusao
        )
        btn_confirmar.pack(fill="x", padx=16, pady=(10, 6))
        _delete_profile_widgets["btn_confirmar"] = btn_confirmar

        # Speaker dots
        dots = tk.Frame(delete_profile_frame, bg=_BG)
        dots.pack(pady=(0, 6))
        for _ in range(3):
            tk.Canvas(dots, width=5, height=5, bg=_BG, highlightthickness=0)\
              .pack(side="left", padx=2)

        _delete_profile_built[0] = True

    def excluir_perfil_ui():
        """Mostra a tela de exclusão de perfil dentro da mesma janela."""
        _build_delete_profile_ui()
        _refresh_delete_profile_list()
        main_content_frame.pack_forget()
        delete_profile_frame.pack(fill="both", expand=True)

    # ═══════════════════════════════════════════════════════
    # ⚡ COMBO & CAPTURA BOXES (inside screen) ⚡
    # ═══════════════════════════════════════════════════════

    # Container para os cards empilhados
    action_panel = tk.Frame(main_content_frame, bg="#27272a")
    action_panel.pack(fill="x", padx=10, pady=(4, 6))

    # ── COMBO BOX (full width) ──
    combo_card = tk.Frame(action_panel, bg="#1a1a1e", padx=10, pady=8,
                          highlightbackground="#eab308", highlightthickness=1)
    combo_card.pack(fill="x", pady=(0, 6))

    combo_header = tk.Frame(combo_card, bg="#1a1a1e")
    combo_header.pack(fill="x")
    combo_title_frame = tk.Frame(combo_header, bg="#1a1a1e")
    combo_title_frame.pack(side="left")
    tk.Label(combo_title_frame, text="⚔", font=("Segoe UI Emoji", 13),
             bg="#1a1a1e", fg="#eab308").pack(side="left", padx=(0, 6))
    combo_title_lbl = tk.Label(combo_title_frame, text="MODO COMBO",
             font=("Consolas", 11, "bold italic"),
             bg="#1a1a1e", fg="#eab308")
    combo_title_lbl.pack(side="left")
    btn_combo_cfg = tk.Button(combo_header, text="⚙", font=("Segoe UI Emoji", 12),
                              bg="#1a1a1e", fg="#52525b", activebackground="#27272a",
                              activeforeground="white", bd=0, cursor="hand2",
                              command=open_combo_setup)
    btn_combo_cfg.pack(side="right")

    # Toggle Combo ON/OFF — botão estilo 3D
    button_activation = tk.Button(
        combo_card, text="●  DESLIGADO", font=("Consolas", 10, "bold"),
        bg="#27272a", fg="#52525b", activebackground="#18181b",
        bd=0, pady=8, cursor="hand2",
        command=toggle_activation, relief="flat"
    )
    button_activation.pack(fill="x", padx=4, pady=(8, 2))

    # ── CAPTURA BOX (full width) ──
    captura_card = tk.Frame(action_panel, bg="#1a1a1e", padx=10, pady=8,
                            highlightbackground="#22d3ee", highlightthickness=1)
    captura_card.pack(fill="x", pady=(0, 4))

    captura_header = tk.Frame(captura_card, bg="#1a1a1e")
    captura_header.pack(fill="x")
    captura_title_frame = tk.Frame(captura_header, bg="#1a1a1e")
    captura_title_frame.pack(side="left")
    tk.Label(captura_title_frame, text="📷", font=("Segoe UI Emoji", 13),
             bg="#1a1a1e", fg="#22d3ee").pack(side="left", padx=(0, 6))
    captura_title_lbl = tk.Label(captura_title_frame, text="MODO CAPTURA",
             font=("Consolas", 11, "bold italic"),
             bg="#1a1a1e", fg="#22d3ee")
    captura_title_lbl.pack(side="left")
    btn_captura_cfg = tk.Button(captura_header, text="⚙", font=("Segoe UI Emoji", 12),
                                bg="#1a1a1e", fg="#52525b", activebackground="#27272a",
                                activeforeground="white", bd=0, cursor="hand2",
                                command=open_capture_setup)
    btn_captura_cfg.pack(side="right")

    # Toggle Captura ON/OFF (single button with embedded dot)

    def toggle_captura_btn():
        """Toggle captura scan habilitado com visual feedback + overlay."""
        global captura_scan_habilitado, captura_modo_ativo
        if not bot_active:
            print("⚠ Bot desligado! Ligue primeiro com a hotkey global.")
            return
        if captura_scan_habilitado:
            captura_scan_habilitado = False
            captura_modo_ativo = False
            btn_captura_main_toggle.config(text="●  DESLIGADO", bg="#27272a", fg="#52525b")
            try:
                if update_overlay_scan: update_overlay_scan()
            except Exception:
                pass
            print("📷 Captura desligada")
        else:
            captura_scan_habilitado = True
            btn_captura_main_toggle.config(text="●  ATIVADO", bg="#16a34a", fg="white")
            try:
                if update_overlay_scan: update_overlay_scan()
            except Exception:
                pass
            print("📷 Captura ligada — pressione G para scan!")

    btn_captura_main_toggle = tk.Button(
        captura_card,
        text="●  DESLIGADO" if not captura_scan_habilitado else "●  ATIVADO",
        font=("Consolas", 10, "bold"),
        bg="#27272a" if not captura_scan_habilitado else "#16a34a",
        fg="#52525b" if not captura_scan_habilitado else "white",
        activebackground="#18181b",
        bd=0, pady=8, cursor="hand2",
        command=toggle_captura_btn, relief="flat"
    )
    btn_captura_main_toggle.pack(fill="x", padx=4, pady=(8, 2))

    # Combo toggle visual update
    _orig_toggle = toggle_activation
    def _enhanced_toggle():
        if not bot_active:
            print("⚠ Bot desligado! Ligue primeiro com a hotkey global.")
            return
        _orig_toggle()
        if combo_active:
            button_activation.config(text="●  ATIVADO", bg="#16a34a", fg="white")
        else:
            button_activation.config(text="●  DESLIGADO", bg="#27272a", fg="#52525b")
    button_activation.config(command=_enhanced_toggle)

    # Bot master switch indicator
    global update_bot_indicator
    def update_bot_indicator():
        if bot_active:
            scan_status_lbl.config(text="BOT ON", fg="#34d399")
            # LED grande fica cyan quando ON
            led_big.itemconfig(led_big_inner, fill="#22d3ee")
            # LED vermelho apaga, verde acende
            small_leds[0][0].itemconfig(small_leds[0][1], fill="#450a0a")
            small_leds[2][0].itemconfig(small_leds[2][1], fill="#22c55e")
            # Restaura cores dos cards
            combo_card.config(highlightbackground="#eab308")
            captura_card.config(highlightbackground="#22d3ee")
            combo_title_lbl.config(fg="#eab308")
            captura_title_lbl.config(fg="#22d3ee")
        else:
            scan_status_lbl.config(text="BOT OFF", fg="#f87171")
            # LED grande fica vermelho quando OFF
            led_big.itemconfig(led_big_inner, fill="#ef4444")
            # LED vermelho acende, verde apaga
            small_leds[0][0].itemconfig(small_leds[0][1], fill="#ef4444")
            small_leds[2][0].itemconfig(small_leds[2][1], fill="#14532d")
        # Also update toggle buttons + cards UI
        try:
            if not bot_active:
                button_activation.config(text="●  DESLIGADO", bg="#27272a", fg="#52525b")
                btn_captura_main_toggle.config(text="●  DESLIGADO", bg="#27272a", fg="#52525b")
                # Dim card borders
                combo_card.config(highlightbackground="#3f3f46")
                captura_card.config(highlightbackground="#3f3f46")
                combo_title_lbl.config(fg="#52525b")
                captura_title_lbl.config(fg="#52525b")
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════
    # 📋 LOG SCREEN (inside screen, bottom)
    # ═══════════════════════════════════════════════════════

    log_panel = tk.Frame(main_content_frame, bg="#000000", bd=1, relief="solid",
                         highlightbackground="#3f3f46", highlightthickness=1)
    log_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # Header do log
    log_header = tk.Frame(log_panel, bg="#000000")
    log_header.pack(fill="x", padx=8, pady=(6, 2))
    tk.Label(log_header, text="\u276f_", font=("Consolas", 8),
             bg="#000000", fg="#52525b").pack(side="left", padx=(0, 4))
    tk.Label(log_header, text="LUUKZ_CONSOLE", font=("Consolas", 8, "bold"),
             bg="#000000", fg="#52525b").pack(side="left")
    # Cursor piscante (muda cor baseado no estado do bot)
    blink_lbl = tk.Label(log_header, text="\u2588", font=("Consolas", 9, "bold"),
                         bg="#000000", fg="#22d3ee")
    blink_lbl.pack(side="right")
    def _blink():
        cur = blink_lbl.cget("fg")
        bot_color = "#22d3ee" if bot_active else "#ef4444"
        blink_lbl.config(fg="#000000" if cur != "#000000" else bot_color)
        root.after(500, _blink)
    _blink()

    # Separador fino
    tk.Frame(log_panel, bg="#27272a", height=1).pack(fill="x", padx=8)

    # Texto do log (visível, scrollável)
    log_panel_text = tk.Text(log_panel, wrap="word", state="disabled",
                             bg="#000000", fg="#a1a1aa", font=("Consolas", 8),
                             bd=0, padx=8, pady=4, height=6,
                             insertbackground="#000000", selectbackground="#3f3f46",
                             cursor="arrow")
    log_panel_text.pack(fill="both", expand=True, padx=2, pady=(2, 4))
    log_panel_text.tag_config("ok", foreground="#34d399")
    log_panel_text.tag_config("err", foreground="#f87171")

    # Mensagens iniciais
    log_panel_text.config(state="normal")
    log_panel_text.insert(tk.END, "Sistema pronto.\n", "ok")
    log_panel_text.insert(tk.END, f"Perfil '{perfil_ativo}' carregado.\n")
    log_panel_text.insert(tk.END, "Aguardando entrada...\n")
    log_panel_text.config(state="disabled")

    # ═══════════════════════════════════════════════════════
    # 🔴 BOTTOM CONTROLS (D-PAD + BUTTONS + GEAR)
    # ═══════════════════════════════════════════════════════

    # ── Decorações inferiores (pontos) ──
    bottom_section = tk.Frame(root, bg="#dc2626")
    bottom_section.pack(fill="x", padx=16, pady=(6, 4))

    dots_frame = tk.Frame(bottom_section, bg="#dc2626")
    dots_frame.pack(anchor="center", pady=(4, 2))
    for _ in range(3):
        _dc = tk.Canvas(dots_frame, width=6, height=6, bg="#dc2626", highlightthickness=0)
        _dc.pack(side="left", padx=3)
        _dc.create_oval(1, 1, 5, 5, fill="#000000", outline="")

    # Barra decorativa
    _deco_bar = tk.Frame(bottom_section, bg="#b91c1c", height=4, width=120)
    _deco_bar.pack(anchor="center", pady=(4, 4))

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
    mini.geometry("200x90+1200+680")
    mini.attributes("-alpha", 0.93)

    # Canvas principal — estilo moderno escuro
    bg = tk.Canvas(mini, width=200, height=90, highlightthickness=0)
    bg.place(x=0, y=0, relwidth=1, relheight=1)

    # Fundo gradiente fake (3 faixas)
    bg.create_rectangle(0, 0, 200, 30, fill="#0f0f0f", outline="")
    bg.create_rectangle(0, 30, 200, 60, fill="#1a1a2e", outline="")
    bg.create_rectangle(0, 60, 200, 90, fill="#16213e", outline="")

    # Linha accent neon no topo
    bg.create_rectangle(0, 0, 200, 2, fill="#00d4ff", outline="")

    # Linha accent neon embaixo
    bg.create_rectangle(0, 88, 200, 90, fill="#7c3aed", outline="")

    # Nome do perfil
    lbl = bg.create_text(12, 13, text=f"⚡ {perfil_ativo}",
                         fill="#00d4ff", font=("Consolas", 9, "bold"), anchor="w")

    # Status dot (combo ativo/desativado)
    status_dot_id = bg.create_oval(178, 5, 192, 19, fill="#ff3b3b", outline="#333333", width=1)

    # Pokeball scan indicator (captura ligado/desligado)
    # Bolinha exterior (vermelho/verde)
    scan_ball_outer = bg.create_oval(160, 5, 174, 19, fill="#ff3b3b", outline="#333333", width=1)
    # Linha do meio da pokeball
    bg.create_line(160, 12, 174, 12, fill="#333333", width=1)
    # Centro da pokeball
    scan_ball_center = bg.create_oval(164, 9, 170, 15, fill="white", outline="#333333", width=1)

    # ---- Indicador BOT (mini toggle com texto OFF/ON + pokeball) ----
    # Track (trilha): x=116-156, y=5-19 — contorno vermelho/verde
    bot_track = bg.create_rectangle(116, 5, 156, 19, fill="#0f0f0f", outline="#ff3b3b", width=1)
    # Texto OFF/ON no centro da trilha
    bot_text = bg.create_text(136, 12, text="  OFF", fill="#ff3b3b",
                               font=("Consolas", 7, "bold"), anchor="center")
    # Pokeball (slider) — OFF = esquerda
    bot_ball = bg.create_oval(117, 6, 131, 18, fill="#ff3b3b", outline="#444444", width=1)
    bot_ball_line = bg.create_line(117, 12, 131, 12, fill="#444444", width=1)
    bot_ball_center = bg.create_oval(121, 9, 127, 15, fill="white", outline="#444444", width=1)

    # ---- Indicador Captu (pokeball + texto em formato pílula) ----
    # Pílula: retângulo central + semicírculos nas pontas
    captu_pill_left = bg.create_oval(58, 25, 82, 55, fill="", outline="#ff3b3b", width=2)
    captu_pill_rect = bg.create_rectangle(70, 25, 130, 55, fill="#0f0f0f", outline="", width=0)
    captu_pill_right = bg.create_oval(118, 25, 142, 55, fill="", outline="#ff3b3b", width=2)
    captu_pill_top = bg.create_line(70, 25, 130, 25, fill="#ff3b3b", width=2)
    captu_pill_bot = bg.create_line(70, 55, 130, 55, fill="#ff3b3b", width=2)
    # Texto "Captu" dentro da pílula (lado esquerdo)
    captu_text = bg.create_text(86, 40, text="Captu", fill="#ff3b3b", font=("Consolas", 8, "bold"), anchor="center")
    # Pokeball dentro da pílula (lado direito, centralizada no semicírculo)
    captu_ball = bg.create_oval(123, 33, 137, 47, fill="#ff3b3b", outline="#444444", width=1)
    captu_ball_line = bg.create_line(123, 40, 137, 40, fill="#444444", width=1)
    captu_center = bg.create_oval(127, 37, 133, 43, fill="white", outline="#444444", width=1)

    # Botão de restaurar (seta elegante)
    bg.create_rectangle(60, 62, 140, 78, fill="#7c3aed", outline="#9d5cff", width=1)
    bg.create_text(100, 70, text="▲ ABRIR", fill="white", font=("Consolas", 8, "bold"))

    # Registra as funções no escopo global
    global update_overlay_status, update_overlay_label, update_overlay_scan, update_overlay_bot

    def update_overlay_status():
        """Atualiza a bolinha de status do overlay."""
        try:
            color = "#00ff88" if combo_active else "#ff3b3b"
            bg.itemconfig(status_dot_id, fill=color)
        except Exception:
            pass

    def update_overlay_scan():
        """Atualiza a pokeball do scan no overlay e o indicador Captu."""
        try:
            # Pokeball pequena: segue captura_scan_habilitado (master switch)
            hab_color = "#00ff88" if captura_scan_habilitado else "#ff3b3b"
            bg.itemconfig(scan_ball_outer, fill=hab_color)
            # Pílula Captu: segue captura_modo_ativo (G ligado/desligado)
            captu_color = "#00ff88" if captura_modo_ativo else "#ff3b3b"
            bg.itemconfig(captu_pill_left, outline=captu_color)
            bg.itemconfig(captu_pill_right, outline=captu_color)
            bg.itemconfig(captu_pill_top, fill=captu_color)
            bg.itemconfig(captu_pill_bot, fill=captu_color)
            bg.itemconfig(captu_ball, fill=captu_color)
            bg.itemconfig(captu_text, fill=captu_color)
        except Exception:
            pass

    def update_overlay_bot():
        """Atualiza o mini toggle BOT no overlay."""
        try:
            if bot_active:
                color = "#00ff88"
                bg.itemconfig(bot_track, outline=color)
                bg.itemconfig(bot_text, text="ON", fill=color)
                bg.itemconfig(bot_ball, fill=color)
                # Pokeball desliza para a direita
                bg.coords(bot_ball, 143, 6, 155, 18)
                bg.coords(bot_ball_line, 143, 12, 155, 12)
                bg.coords(bot_ball_center, 146, 9, 152, 15)
            else:
                color = "#ff3b3b"
                bg.itemconfig(bot_track, outline=color)
                bg.itemconfig(bot_text, text="  OFF", fill=color)
                bg.itemconfig(bot_ball, fill=color)
                # Pokeball na esquerda
                bg.coords(bot_ball, 117, 6, 131, 18)
                bg.coords(bot_ball_line, 117, 12, 131, 12)
                bg.coords(bot_ball_center, 121, 9, 127, 15)
        except Exception:
            pass

    def update_overlay_label():
        """Atualiza o nome do perfil no overlay."""
        try:
            bg.itemconfig(lbl, text=f"⚡ {perfil_ativo}")
        except Exception:
            pass

    def on_restore(event=None):
        cx, cy = event.x, event.y
        if 60 <= cx <= 140 and 62 <= cy <= 78:
            restaurar()

    bg.bind("<Button-1>", on_restore)

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
        update_overlay_label()
        
        
    # Intercepta minimizar da janela principal
    def _on_unmap(e):
        root.after(10, minimizar_personalizado)
    root.bind("<Unmap>", _on_unmap)
    
    # ==================================

    root.mainloop()

if __name__ == "__main__":
    main()