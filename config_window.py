"""
config_window.py — Janela de Ajustes (Pokédex style)
Hotkey global para ligar/desligar o bot + modo captura revive/pos_center.
"""

import tkinter as tk
import threading
import keyboard


# ══════════════════════════════════════════════
#  Cores (design system)
# ══════════════════════════════════════════════
_BG       = "#121214"
_CARD     = "#1a1a1e"
_BORDER   = "#27272a"
_TEXT     = "#d4d4d8"
_DIM      = "#71717a"
_CYAN     = "#22d3ee"
_YELLOW   = "#eab308"
_GREEN    = "#16a34a"
_RED      = "#dc2626"
_BLACK    = "#000000"


def abrir_configuracao(root, ctx):
    """
    Abre a janela de ajustes.

    ctx é um dict com referências do main:
        ctx["janela_cfg"]          — referência mutável [None]
        ctx["get_capturando"]      — lambda: bool
        ctx["set_capturando"]      — lambda(bool): sets + starts thread if True
        ctx["_loop_captura"]       — função (not used directly, set_capturando handles thread)
        ctx["bot_hotkey"]          — [str]   ex: "F1"
        ctx["on_hotkey_changed"]   — callback(old_key, new_key)
        ctx["salvar_perfil_atual"] — função(nome)
        ctx["perfil_ativo"]        — str
        ctx["perfis"]              — dict
        ctx["salvar_perfis"]       — função()
    """

    ref = ctx["janela_cfg"]
    if ref[0] is not None:
        try:
            if ref[0].winfo_exists():
                ref[0].lift()
                ref[0].focus_force()
                return
        except Exception:
            pass

    cfg = tk.Toplevel(root)
    ref[0] = cfg
    cfg.title("⚙ Ajustes")
    cfg.geometry("380x520")
    cfg.resizable(False, False)
    cfg.configure(bg=_BG)

    # ── HEADER ──
    header = tk.Frame(cfg, bg=_BG)
    header.pack(fill="x", padx=16, pady=(14, 0))

    # Botão VOLTAR
    btn_voltar = tk.Button(
        header, text="❮  VOLTAR", font=("Consolas", 9, "bold"),
        bg=_BG, fg=_DIM, bd=0, cursor="hand2",
        activebackground=_BG, activeforeground="white",
        command=lambda: _fechar(cfg, ref, ctx)
    )
    btn_voltar.pack(side="left")

    # Título AJUSTES
    title_frame = tk.Frame(header, bg=_BG)
    title_frame.pack(side="right")
    tk.Label(title_frame, text="⚙", font=("Segoe UI Emoji", 12),
             bg=_BG, fg=_CYAN).pack(side="left", padx=(0, 4))
    tk.Label(title_frame, text="AJUSTES", font=("Consolas", 13, "bold italic"),
             bg=_BG, fg=_CYAN).pack(side="left")

    # Separador header
    tk.Frame(cfg, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(10, 0))

    # ── SCROLL AREA ──
    content = tk.Frame(cfg, bg=_BG)
    content.pack(fill="both", expand=True, padx=16, pady=(10, 0))

    # ═══════════════════════════════════════════
    # SEÇÃO 1: HOTKEY GLOBAL
    # ═══════════════════════════════════════════
    _section_label(content, "⌨  HOTKEY GLOBAL", _YELLOW)

    hotkey_card = tk.Frame(content, bg=_CARD, highlightbackground=_BORDER,
                           highlightthickness=1)
    hotkey_card.pack(fill="x", pady=(6, 0))

    hotkey_inner = tk.Frame(hotkey_card, bg=_CARD)
    hotkey_inner.pack(fill="x", padx=12, pady=10)

    # Texto esquerda
    lbl_frame = tk.Frame(hotkey_inner, bg=_CARD)
    lbl_frame.pack(side="left")
    tk.Label(lbl_frame, text="LIGAR / DESLIGAR BOT",
             font=("Consolas", 9, "bold"), bg=_CARD, fg="white").pack(anchor="w")
    tk.Label(lbl_frame, text="ALTERNA ESTADO DO PROGRAMA",
             font=("Consolas", 7), bg=_CARD, fg=_DIM).pack(anchor="w")

    # Botão da hotkey (clicável para capturar nova tecla)
    hotkey_var = tk.StringVar(value=ctx["bot_hotkey"][0])
    _capturing_hotkey = [False]

    btn_hotkey = tk.Button(
        hotkey_inner, textvariable=hotkey_var,
        font=("Consolas", 11, "bold"), bg="#18181b", fg=_YELLOW,
        bd=1, relief="solid", padx=12, pady=4, cursor="hand2",
        activebackground="#27272a", activeforeground=_YELLOW,
        command=lambda: _start_hotkey_capture(btn_hotkey, hotkey_var, _capturing_hotkey, cfg)
    )
    btn_hotkey.pack(side="right")

    # ═══════════════════════════════════════════
    # SEÇÃO 2: CAPTURA REVIVE & POS
    # ═══════════════════════════════════════════
    _section_label(content, "◎  CAPTURA REVIVE & POS", _CYAN)

    cap_card = tk.Frame(content, bg=_CARD, highlightbackground=_BORDER,
                        highlightthickness=1)
    cap_card.pack(fill="x", pady=(6, 0))

    # Info box
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

    # Status variável
    status_var = tk.StringVar(value="DESATIVADO")

    # Botão ATIVAR
    btn_ativar = tk.Button(
        cap_card, text="◎  ATIVAR CAPTURA (H=POKE, J=CENTER)",
        font=("Consolas", 9, "bold"), bg="#27272a", fg="white",
        activebackground=_CYAN, activeforeground="black",
        bd=0, pady=8, cursor="hand2",
        command=lambda: _start_captura(ctx, status_var)
    )
    btn_ativar.pack(fill="x", padx=10, pady=(8, 4))

    # Botão DESATIVAR
    _des_frame = tk.Frame(cap_card, bg=_RED, bd=0, highlightthickness=0)
    _des_frame.pack(fill="x", padx=10, pady=(0, 8))
    btn_desativar = tk.Button(
        _des_frame, text="⚡  DESATIVAR CAPTURA",
        font=("Consolas", 9, "bold"), bg="#0a0a0c", fg=_RED,
        activebackground="#1a0505",
        bd=0, relief="flat", pady=6, cursor="hand2",
        highlightthickness=0,
        command=lambda: _stop_captura(ctx, status_var)
    )
    btn_desativar.pack(fill="both", expand=True, padx=2, pady=2)

    # Status label
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

    # Atualiza cor do status
    def _update_status_color(*_):
        val = status_var.get()
        if val == "DESATIVADO":
            status_lbl.config(fg=_RED)
        else:
            status_lbl.config(fg=_GREEN)
    status_var.trace_add("write", _update_status_color)

    # ── FOOTER: SALVAR + RESET ──
    tk.Frame(cfg, bg=_BORDER, height=1).pack(fill="x", padx=16, pady=(8, 0))

    footer = tk.Frame(cfg, bg=_BG)
    footer.pack(fill="x", padx=16, pady=(8, 12))

    btn_salvar = tk.Button(
        footer, text="💾  SALVAR CONFIGS",
        font=("Consolas", 10, "bold"), bg=_GREEN, fg="white",
        activebackground="#15803d", bd=0, pady=8, cursor="hand2",
        command=lambda: _salvar(cfg, ctx, hotkey_var)
    )
    btn_salvar.pack(side="left", fill="x", expand=True, padx=(0, 6))

    btn_reset = tk.Button(
        footer, text="↻", font=("Consolas", 14, "bold"),
        bg="#27272a", fg=_DIM, activebackground="#3f3f46",
        bd=1, relief="solid", padx=8, pady=4, cursor="hand2",
        command=lambda: _reset(hotkey_var, status_var, ctx)
    )
    btn_reset.pack(side="right")

    # Speaker dots (detalhe)
    dots = tk.Frame(cfg, bg=_BG)
    dots.pack(pady=(0, 6))
    for _ in range(3):
        tk.Canvas(dots, width=5, height=5, bg=_BG, highlightthickness=0)\
          .pack(side="left", padx=2)

    cfg.protocol("WM_DELETE_WINDOW", lambda: _fechar(cfg, ref, ctx))


# ──────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────

def _section_label(parent, text, color):
    """Label de seção com barra lateral colorida."""
    f = tk.Frame(parent, bg=parent.cget("bg"))
    f.pack(fill="x", pady=(12, 0))
    bar = tk.Frame(f, bg=color, width=3, height=16)
    bar.pack(side="left", padx=(0, 8))
    bar.pack_propagate(False)
    tk.Label(f, text=text, font=("Consolas", 9, "bold"),
             bg=parent.cget("bg"), fg="#a1a1aa").pack(side="left")


def _start_hotkey_capture(btn, var, capturing, window):
    """Entra em modo de captura de tecla."""
    if capturing[0]:
        return
    capturing[0] = True
    var.set("...")
    btn.config(fg="#ef4444")

    def on_key(event):
        if event.event_type == keyboard.KEY_DOWN:
            var.set(event.name.upper())
            btn.config(fg="#eab308")
            capturing[0] = False
            keyboard.unhook(hook_ref[0])

    hook_ref = [keyboard.hook(on_key)]


def _start_captura(ctx, status_var):
    """Inicia modo captura de posições."""
    if ctx["get_capturando"]():
        return
    ctx["set_capturando"](True)
    status_var.set("AGUARDANDO TECLAS...")
    print("Modo captura iniciado — aperte 'h' para revive, 'j' para center.")


def _stop_captura(ctx, status_var):
    """Para modo captura."""
    if not ctx["get_capturando"]():
        return
    ctx["set_capturando"](False)
    status_var.set("DESATIVADO")
    print("Modo captura finalizado.")


def _salvar(cfg_win, ctx, hotkey_var):
    """Salva hotkey no perfil e aplica."""
    new_key = hotkey_var.get().strip()
    if not new_key or new_key == "...":
        return

    old_key = ctx["bot_hotkey"][0]
    ctx["bot_hotkey"][0] = new_key

    # Salva no perfil
    perfil = ctx["perfis"].get(ctx["perfil_ativo"], {})
    perfil["bot_hotkey"] = new_key
    ctx["perfis"][ctx["perfil_ativo"]] = perfil
    ctx["salvar_perfis"]()

    # Re-registra hotkey global
    ctx["on_hotkey_changed"](old_key, new_key)

    print(f"✅ Configs salvas! Hotkey bot: {new_key}")


def _reset(hotkey_var, status_var, ctx):
    """Reseta para valores padrão."""
    hotkey_var.set("F1")
    _stop_captura(ctx, status_var)


def _fechar(cfg_win, ref, ctx):
    """Fecha a janela e limpa referência."""
    _stop_captura_silent(ctx)
    cfg_win.destroy()
    ref[0] = None


def _stop_captura_silent(ctx):
    """Para captura silenciosamente."""
    if ctx["get_capturando"]():
        ctx["set_capturando"](False)
