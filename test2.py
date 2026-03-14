import tkinter as tk
import time

class OverlayRota:
    def __init__(self):
        self.root = tk.Tk()
        
        # Faz a janela ocupar a tela toda, remove as bordas e fica sempre no topo
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # Define a cor preta como 100% transparente (você verá o jogo através dela)
        self.root.wm_attributes('-transparentcolor', 'black')
        
        # Cria a área de desenho preta (que ficará invisível)
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Lista para guardar o histórico de coordenadas
        self.pontos = []

    def registrar_coordenada(self, x, y):
        # Desenha o quadrado 32x32 na posição atual
        self.canvas.create_rectangle(x-16, y-16, x+16, y+16, outline="green", width=2)
        
        # Se já existir um ponto anterior, desenha uma linha conectando os dois
        if len(self.pontos) > 0:
            ultimo_x, ultimo_y = self.pontos[-1]
            
            # Desenha uma linha verde pontilhada (dash) conectando os pontos
            self.canvas.create_line(ultimo_x, ultimo_y, x, y, fill="green", width=2, dash=(5, 5))
        
        # Salva o novo ponto na lista
        self.pontos.append((x, y))
        self.root.update()

# --- Testando a Rota ---
overlay = OverlayRota()

# Simulando o usuário clicando e gravando pontos pelo mapa
overlay.registrar_coordenada(200, 200) # Ponto 1
time.sleep(1)
overlay.registrar_coordenada(400, 300) # Ponto 2 (Vai criar uma linha do Ponto 1 até aqui)
time.sleep(1)
overlay.registrar_coordenada(600, 250) # Ponto 3 (Vai criar uma linha do Ponto 2 até aqui)
time.sleep(1)
overlay.registrar_coordenada(800, 500) # Ponto 4

# Mantém o overlay aberto para você visualizar
overlay.root.mainloop()