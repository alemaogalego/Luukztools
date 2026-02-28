import json
import os
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

# Nightmare attacks: lista de dicts [{"key1": "alt", "key2": "1", "delay": 0.5}, ...]
nightmare_attacks = []

# Modo de combo ativo: "HUNT NORMAL" ou "NIGHTMARE"
combo_mode_active = "HUNT NORMAL"

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
    global revive_key
    global pokestop_delay, pokemedi_delay, pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5
    global pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12, combo_start_key, lbl
    global nightmare_attacks, combo_mode_active
    global bot_hotkey

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
        "combo_start_key": combo_start_key,
        "nightmare_attacks": nightmare_attacks,
        "combo_mode_active": combo_mode_active,
        "pos_poke": list(combo.pos_poke),
        "pos_center": list(combo.pos_center),
        "bot_hotkey": bot_hotkey
    }
    salvar_perfis()

def excluir_perfil(nome):
    if nome in perfis and nome != "default":
        del perfis[nome]
        salvar_perfis()

combo_start_key = ""  # Defina a tecla padrão ou carregue do perfil

def start_combo():
    if not bot_active:
        print("⚠ Bot desligado! Combo não executa.")
        return
    if combo_active:
        if combo_mode_active == "NIGHTMARE":
            # Nightmare: pokestop + medicine + nightmare attacks com combo keys
            combo.combo_nightmare(
                pokestop_key, pokemedi_key,
                pokestop_delay, pokemedi_delay,
                nightmare_attacks
            )
            print("Combo Nightmare executado!")
            combo.revive(revive_key)
            print("Revive executado!")
        else:
            # Hunt Normal
            combo.combopoke(
                pokestop_key, pokemedi_key,
                pokeattack_key1, pokeattack_key2, pokeattack_key3, pokeattack_key4, pokeattack_key5,
                pokeattack_key6, pokeattack_key7, pokeattack_key8, pokeattack_key9, pokeattack_key10, pokeattack_key11, pokeattack_key12,
                pokestop_delay, pokemedi_delay,
                pokeattack_delay1, pokeattack_delay2, pokeattack_delay3, pokeattack_delay4, pokeattack_delay5,
                pokeattack_delay6, pokeattack_delay7, pokeattack_delay8, pokeattack_delay9, pokeattack_delay10, pokeattack_delay11, pokeattack_delay12
            )
            print("Combo Hunt Normal executado!")
            combo.revive(revive_key)
            print("Revive executado!")
    else:
        print("Combo está desligado, não executa!")

def toggle_bot():
    """Liga/desliga o bot inteiro (master switch)."""
    global bot_active, combo_active, captura_modo_ativo
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
        if captura_modo_ativo:
            captura_modo_ativo = False
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
    led_big.create_oval(7, 7, 41, 41, fill="#22d3ee", outline="white", width=3)
    # Brilho/reflexo
    led_big.create_oval(14, 10, 28, 22, fill="#80eeff", outline="")

    # Pequenos LEDs (vermelho, amarelo, verde)
    for color, border in [("#ef4444", "#991b1b"), ("#facc15", "#a16207"), ("#22c55e", "#166534")]:
        led_sm = tk.Canvas(top_bar, width=12, height=12, bg="#dc2626", highlightthickness=0)
        led_sm.pack(side="left", padx=2, pady=16)
        led_sm.create_oval(1, 1, 11, 11, fill=color, outline=border, width=1)

    # Título "LUUKZ TOOLS" no canto direito
    tk.Label(top_bar, text="LUUKZ TOOLS", font=("Arial Black", 15, "italic"),
             bg="#dc2626", fg="white").pack(side="right", padx=10)

    # Borda inferior vermelha escura (separador sutil)
    tk.Frame(root, bg="#b91c1c", height=2).pack(fill="x", padx=8)

    # ═══════════════════════════════════════════
    # 📺 INNER SCREEN CONTAINER
    # ═══════════════════════════════════════════

    screen_border = tk.Frame(root, bg="#3f3f46", bd=0)
    screen_border.pack(fill="both", expand=True, padx=16, pady=(8, 6))

    screen = tk.Frame(screen_border, bg="#27272a")
    screen.pack(fill="both", expand=True, padx=4, pady=4)

    # ── Profile Header ──
    perfil_bar = tk.Frame(screen, bg="#18181b", bd=1, relief="solid",
                          highlightbackground="#3f3f46", highlightthickness=1)
    perfil_bar.pack(fill="x", padx=10, pady=(10, 6))

    # Lado esquerdo: > PROFILE
    perfil_left = tk.Frame(perfil_bar, bg="#18181b")
    perfil_left.pack(side="left", padx=6, pady=4)
    tk.Label(perfil_left, text="❯", font=("Consolas", 11, "bold"),
             bg="#18181b", fg="#22d3ee").pack(side="left")
    perfil_label = tk.Label(perfil_left, text=f" {perfil_ativo.upper()}",
                            font=("Consolas", 11, "bold"),
                            fg="#22d3ee", bg="#18181b")
    perfil_label.pack(side="left")

    # Lado direito: badge scan status
    scan_badge = tk.Frame(perfil_bar, bg="#27272a", bd=1, relief="solid",
                          highlightbackground="#3f3f46", highlightthickness=1)
    scan_badge.pack(side="right", padx=6, pady=4)
    scan_icon_lbl = tk.Label(scan_badge, text="⚠", font=("Segoe UI Emoji", 9),
             bg="#27272a", fg="#f87171")
    scan_icon_lbl.pack(side="left", padx=(4, 2))
    scan_status_lbl = tk.Label(scan_badge, text="BOT OFF",
                               font=("Consolas", 8, "bold"),
                               bg="#27272a", fg="#f87171")
    scan_status_lbl.pack(side="left", padx=(0, 2))
    tk.Label(scan_badge, text="📋", font=("Segoe UI Emoji", 9),
             bg="#27272a", fg="#22d3ee").pack(side="left", padx=(2, 4))

    # Log mini (hidden - will use full log)
    log_history = []

    # Invisible mini log widget (needed for TextRedirector compatibility)
    _log_mini_frame = tk.Frame(screen, bg="#27272a", height=1)
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

    # Log button attached to scan_badge (clicking 📋 opens full log)
    scan_badge.bind("<Button-1>", lambda e: abrir_log_completo())
    for child in scan_badge.winfo_children():
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

    def _on_hotkey_changed(old_key, new_key):
        """Re-registra a hotkey global do bot."""
        global bot_hotkey
        try:
            keyboard.remove_hotkey(old_key)
        except Exception:
            pass
        bot_hotkey = new_key
        keyboard.add_hotkey(new_key, toggle_bot, suppress=False)

    def abrir_configuracao():
        config_window.abrir_configuracao(root, {
            "janela_cfg": _janela_cfg_ref,
            "get_capturando": lambda: capturando,
            "set_capturando": _set_capturando,
            "_loop_captura": _loop_captura,
            "bot_hotkey": [bot_hotkey],
            "on_hotkey_changed": _on_hotkey_changed,
            "salvar_perfil_atual": salvar_perfil_atual,
            "perfil_ativo": perfil_ativo,
            "perfis": perfis,
            "salvar_perfis": salvar_perfis,
        })

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
        """
        global captura_modo_ativo
        print("🟢 Scan MAX SPEED (MSS+DXGI+ctypes)")

        # Pré-carrega refs em GRAYSCALE, lista plana
        ref_list = []
        for gaveta in list(captura_gavetas):
            if not gaveta.get("ativo", False):
                continue
            nome = gaveta["nome"]
            pasta = os.path.join(CAPTURA_DIR, nome)
            if not os.path.isdir(pasta):
                continue
            for f in sorted(os.listdir(pasta)):
                if f.endswith(".png"):
                    caminho = os.path.join(pasta, f)
                    img = cv2.imread(caminho, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        ref_list.append((nome, f, img))
        print(f"📦 {len(ref_list)} refs (gray flat-cache)")

        if not ref_list:
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
                        screen_gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
                    except Exception:
                        continue

                    encontrou = False
                    for nome, arq, ref_gray in ref_list:
                        if not captura_modo_ativo:
                            break
                        res = cv2.matchTemplate(screen_gray, ref_gray, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, max_loc = cv2.minMaxLoc(res)
                        if max_val >= 0.84:
                            h, w = ref_gray.shape
                            cx = max_loc[0] + w // 2
                            cy = max_loc[1] + h // 2
                            # Move mouse SEM clicar → T → 1 click só
                            ctypes.windll.user32.SetCursorPos(cx, cy)
                            keyboard.press_and_release('t')
                            time.sleep(0.015)
                            _win_click(cx, cy)
                            print(f"🎯 {nome} ({arq}) — ({cx},{cy}) [{max_val:.0%}]")
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
                gaveta_data = {"nome": nome, "ativo": False}
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

    # ═══════════════════════════════════════════════════════
    # ⚡ COMBO & CAPTURA BOXES (inside screen) ⚡
    # ═══════════════════════════════════════════════════════

    # Container para os 2 cards + slider central
    action_panel = tk.Frame(screen, bg="#27272a")
    action_panel.pack(fill="x", padx=10, pady=(4, 6))

    # ── COMBO BOX (esquerda) ──
    combo_card = tk.Frame(action_panel, bg="#18181b", padx=10, pady=8,
                          highlightbackground="#eab308", highlightthickness=2)
    combo_card.grid(row=0, column=0, padx=(0, 4), pady=0, sticky="nsew")

    tk.Label(combo_card, text="⚔", font=("Segoe UI Emoji", 26),
             bg="#18181b", fg="#eab308").pack(pady=(4, 0))
    tk.Label(combo_card, text="COMBO", font=("Consolas", 11, "bold"),
             bg="#18181b", fg="#eab308").pack(pady=(2, 6))

    btn_combo_open = tk.Button(
        combo_card, text="⚙ Config", font=("Consolas", 9, "bold"),
        bg="#4f46e5", fg="white", activebackground="#3730a3",
        bd=0, padx=20, pady=5, cursor="hand2",
        command=open_janelacombo
    )
    btn_combo_open.pack(fill="x", padx=8, pady=(0, 6))

    # Toggle Combo ON/OFF (single button with embedded dot)
    button_activation = tk.Button(
        combo_card, text="● Desligado", font=("Consolas", 9, "bold"),
        bg="#dc2626", fg="white", activebackground="#991b1b",
        bd=0, pady=5, cursor="hand2",
        command=toggle_activation
    )
    button_activation.pack(fill="x", padx=8)

    # ── VERTICAL SLIDER / SEPARATOR ──
    sep_frame = tk.Frame(action_panel, bg="#27272a", width=20)
    sep_frame.grid(row=0, column=1, padx=2, pady=10, sticky="ns")
    slider_canvas = tk.Canvas(sep_frame, width=16, height=100,
                              bg="#27272a", highlightthickness=0)
    slider_canvas.pack(expand=True)
    # Trilho vertical
    slider_canvas.create_rectangle(6, 5, 10, 95, fill="#3f3f46", outline="")
    # Bolinha do slider
    slider_canvas.create_oval(1, 42, 15, 58, fill="white", outline="#18181b", width=2)
    slider_canvas.create_rectangle(5, 48, 11, 52, fill="#a1a1aa", outline="")

    # ── CAPTURA BOX (direita) ──
    captura_card = tk.Frame(action_panel, bg="#18181b", padx=10, pady=8,
                            highlightbackground="#22d3ee", highlightthickness=2)
    captura_card.grid(row=0, column=2, padx=(4, 0), pady=0, sticky="nsew")

    tk.Label(captura_card, text="📷", font=("Segoe UI Emoji", 26),
             bg="#18181b", fg="#22d3ee").pack(pady=(4, 0))
    tk.Label(captura_card, text="CAPTURA", font=("Consolas", 11, "bold"),
             bg="#18181b", fg="#22d3ee").pack(pady=(2, 6))

    btn_captura_open = tk.Button(
        captura_card, text="⚙ Config", font=("Consolas", 9, "bold"),
        bg="#7c3aed", fg="white", activebackground="#5b21b6",
        bd=0, padx=20, pady=5, cursor="hand2",
        command=abrir_captura
    )
    btn_captura_open.pack(fill="x", padx=8, pady=(0, 6))

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
            btn_captura_main_toggle.config(text="● Desligado", bg="#dc2626")
            try:
                if update_overlay_scan: update_overlay_scan()
            except Exception:
                pass
            print("📷 Captura desligada")
        else:
            captura_scan_habilitado = True
            btn_captura_main_toggle.config(text="● Ligado", bg="#16a34a")
            try:
                if update_overlay_scan: update_overlay_scan()
            except Exception:
                pass
            print("📷 Captura ligada — pressione G para scan!")

    btn_captura_main_toggle = tk.Button(
        captura_card,
        text="● Desligado" if not captura_scan_habilitado else "● Ligado",
        font=("Consolas", 9, "bold"),
        bg="#dc2626" if not captura_scan_habilitado else "#16a34a",
        fg="white", activebackground="#991b1b",
        bd=0, pady=5, cursor="hand2",
        command=toggle_captura_btn
    )
    btn_captura_main_toggle.pack(fill="x", padx=8)

    # Grid weights
    action_panel.columnconfigure(0, weight=1)
    action_panel.columnconfigure(2, weight=1)

    # Combo toggle visual update
    _orig_toggle = toggle_activation
    def _enhanced_toggle():
        if not bot_active:
            print("⚠ Bot desligado! Ligue primeiro com a hotkey global.")
            return
        _orig_toggle()
        if combo_active:
            button_activation.config(text="● Ativado", bg="#16a34a")
        else:
            button_activation.config(text="● Desligado", bg="#dc2626")
    button_activation.config(command=_enhanced_toggle)

    # Bot master switch indicator
    global update_bot_indicator
    def update_bot_indicator():
        if bot_active:
            scan_status_lbl.config(text="BOT ON", fg="#34d399")
            scan_icon_lbl.config(text="✔", fg="#34d399")
        else:
            scan_status_lbl.config(text="BOT OFF", fg="#f87171")
            scan_icon_lbl.config(text="⚠", fg="#f87171")
        # Also update toggle buttons UI
        try:
            if not bot_active:
                button_activation.config(text="● Desligado", bg="#dc2626")
                btn_captura_main_toggle.config(text="● Desligado", bg="#dc2626")
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════
    # 📋 LOG SCREEN (inside screen, bottom)
    # ═══════════════════════════════════════════════════════

    log_panel = tk.Frame(screen, bg="#000000", bd=2, relief="solid",
                         highlightbackground="#3f3f46", highlightthickness=1)
    log_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # Header do log
    log_header = tk.Frame(log_panel, bg="#000000")
    log_header.pack(fill="x", padx=8, pady=(6, 2))
    tk.Label(log_header, text="SYSTEM_LOGS", font=("Consolas", 8),
             bg="#000000", fg="#52525b").pack(side="left")
    # Cursor piscante
    blink_lbl = tk.Label(log_header, text="_", font=("Consolas", 9, "bold"),
                         bg="#000000", fg="#52525b")
    blink_lbl.pack(side="right")
    def _blink():
        cur = blink_lbl.cget("fg")
        blink_lbl.config(fg="#000000" if cur != "#000000" else "#52525b")
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
    log_panel_text.insert(tk.END, "Sistema iniciado...\n", "ok")
    log_panel_text.insert(tk.END, "Aguardando comando do usuário.\n")
    log_panel_text.insert(tk.END, "Scan desabilitado por padrão.\n")
    log_panel_text.config(state="disabled")

    # ═══════════════════════════════════════════════════════
    # 🔴 BOTTOM CONTROLS (D-PAD + BUTTONS + GEAR)
    # ═══════════════════════════════════════════════════════

    bottom_section = tk.Frame(root, bg="#dc2626")
    bottom_section.pack(fill="x", padx=16, pady=(4, 2))

    # D-pad decorativo (esquerda)
    dpad = tk.Canvas(bottom_section, width=52, height=52, bg="#dc2626", highlightthickness=0)
    dpad.grid(row=0, column=0, padx=(4, 8), pady=4)
    # Cruz horizontal
    dpad.create_rectangle(0, 18, 52, 34, fill="#27272a", outline="#3f3f46", width=1)
    # Cruz vertical
    dpad.create_rectangle(18, 0, 34, 52, fill="#27272a", outline="#3f3f46", width=1)
    # Centro
    dpad.create_oval(20, 20, 32, 32, fill="#18181b", outline="#3f3f46", width=1)

    # 3 Botões de ação (centro)
    btn_frame = tk.Frame(bottom_section, bg="#dc2626")
    btn_frame.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
    bottom_section.columnconfigure(1, weight=1)

    # Botão CRIAR (amarelo com shadow)
    btn_criar_f = tk.Frame(btn_frame, bg="#a16207")
    btn_criar_f.pack(side="left", expand=True, fill="x", padx=3)
    btn_criar = tk.Button(btn_criar_f, text="＋\nCRIAR", font=("Consolas", 8, "bold"),
                          bg="#eab308", fg="black", activebackground="#facc15",
                          bd=0, padx=6, pady=4, cursor="hand2",
                          command=criar_perfil)
    btn_criar.pack(fill="x", padx=0, pady=(0, 3))

    # Botão SELECIONAR (azul com shadow)
    btn_sel_f = tk.Frame(btn_frame, bg="#1e3a8a")
    btn_sel_f.pack(side="left", expand=True, fill="x", padx=3)
    btn_selecionar = tk.Button(btn_sel_f, text="▷\nSELECIONAR", font=("Consolas", 8, "bold"),
                               bg="#2563eb", fg="white", activebackground="#3b82f6",
                               bd=0, padx=6, pady=4, cursor="hand2",
                               command=selecionar_perfil)
    btn_selecionar.pack(fill="x", padx=0, pady=(0, 3))

    # Botão EXCLUIR (vermelho escuro com shadow)
    btn_exc_f = tk.Frame(btn_frame, bg="#7f1d1d")
    btn_exc_f.pack(side="left", expand=True, fill="x", padx=3)
    btn_excluir = tk.Button(btn_exc_f, text="🗑\nEXCLUIR", font=("Consolas", 8, "bold"),
                            bg="#b91c1c", fg="white", activebackground="#dc2626",
                            bd=0, padx=6, pady=4, cursor="hand2",
                            command=excluir_perfil_ui)
    btn_excluir.pack(fill="x", padx=0, pady=(0, 3))

    # Botão Config/Gear (direita)
    btn_gear = tk.Button(bottom_section, text="⚙", font=("Segoe UI Emoji", 18),
                         bg="#991b1b", fg="#eab308", activebackground="#7f1d1d",
                         bd=2, relief="ridge", width=3, height=1, cursor="hand2",
                         command=lambda: abrir_configuracao())
    btn_gear.grid(row=0, column=2, padx=(8, 4), pady=4)

    # ── Speaker grilles (detalhe inferior) ──
    speaker_frame = tk.Frame(root, bg="#dc2626")
    speaker_frame.pack(pady=(0, 6))
    for _ in range(4):
        tk.Frame(speaker_frame, bg="#b91c1c", width=32, height=3).pack(side="left", padx=3, pady=2)

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
    global update_overlay_status, update_overlay_label, update_overlay_scan

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