LukzTools - Ferramenta de Automação de Combos
Uma ferramenta de automação com interface gráfica (GUI) construída em Python usando Tkinter. O LukzTools permite que usuários configurem e executem sequências de teclas (combos) em jogos ou outras aplicações, com suporte a perfis, delays customizáveis e um overlay para fácil acesso.

📷 Screenshots
## 📷 Screenshots

| Janela Principal | Configuração do Combo | Mini Overlay |
| :---: |:---:|:---:|
| ![Janela Principal do LukzTools](assets/janela_principal.png) | ![Janela de Configuração do Combo](assets/config_combo.png) | ![Mini Overlay da Aplicação](assets/mini_overlay.png) |

Exportar para as Planilhas
✨ Principais Funcionalidades
Interface Gráfica Intuitiva: Fácil de configurar através de uma interface visual, sem necessidade de editar código.

Combos 100% Configuráveis: Defina até 12 teclas de ataque, teclas de suporte (stop/medicine) e uma tecla de "revive", cada uma com seu próprio delay em segundos.

Gerenciamento de Perfis: Crie, salve, selecione e exclua perfis diferentes. Ideal para configurar o bot para diferentes personagens ou situações de jogo.

Captura de Coordenadas: Um modo de configuração especial permite capturar coordenadas precisas do mouse para ações específicas, como o "revive".

Atalho de Ativação: Defina uma tecla de atalho global para iniciar o combo, que só funcionará quando a ferramenta estiver "Ativada".

Mini Overlay: Minimize a aplicação para um pequeno overlay que fica sempre visível, permitindo reabrir a janela principal com um clique, sem poluir a tela.

⚙️ Como Funciona
A aplicação utiliza as bibliotecas keyboard para simular o pressionamento de teclas e pyautogui para controlar o mouse. A interface, construída com tkinter, permite que o usuário defina todas as teclas e delays, que são salvos em um arquivo perfis.json. Ao ativar a ferramenta, ela escuta pela "tecla de início de combo" e, quando pressionada, executa a sequência de ações pré-configurada.

🚀 Instalação e Execução
Para rodar este projeto, você precisará ter o Python 3 instalado.

Clone o repositório:

Bash

git clone https://github.com/seu-usuario/LuukzTools.git
cd LuukzTools
Crie um arquivo requirements.txt com o seguinte conteúdo:

Plaintext

keyboard
pyautogui
Pillow
Instale as dependências:

Bash

pip install -r requirements.txt
Execute a aplicação:

Bash

python main.py
📋 Como Usar
Primeira Execução (Configuração de Posição):

Abra o programa.

Clique no botão "⚙ Configuração".

Clique em "▶ Ativar captura".

Volte para o seu jogo. Coloque o cursor do mouse sobre a imagem do seu pokémon (para o revive) e pressione a tecla h.

Coloque o cursor no centro da tela (ou perto do seu personagem) e pressione a tecla j.

Clique em "■ Desativar captura" na janela de configuração.

Configurando seu Combo:

Na janela principal, clique no botão "Combo".

Preencha os campos com as teclas que você usa no jogo (f1, f2, page down, etc.) e os delays desejados entre cada ação (ex: 0.5 para meio segundo).

Defina a tecla que irá iniciar todo o combo no campo "Iniciar Combo".

Clique em "Salvar".

Salvando seu Perfil:

Na janela principal, clique em "👤 Criar Perfil".

Dê um nome ao seu perfil (ex: "Meu Paladino") e clique em "Criar". Suas configurações de combo atuais serão salvas nele.

Ativando a Ferramenta:

Clique no botão "Desligado" para que ele fique verde e mude para "Ativado".

Executando no Jogo:

Com a ferramenta "Ativada", vá para o jogo e pressione a tecla que você definiu como "Iniciar Combo". A sequência de ataques e ações será executada.

📂 Estrutura dos Arquivos
/LuukzTools
|
├── main.py             # Lógica da interface gráfica, perfis e controle geral
├── combo.py            # Funções principais de automação (simulação de teclas e mouse)
├── perfis.json         # Arquivo gerado para salvar os perfis dos usuários
├── requirements.txt    # Lista de dependências Python do projeto
|
└── /assets/            # Pasta sugerida para as imagens
    ├── logo.jpg
    ├── imgfundo.jpg
    └── ...
⚠️ Aviso Importante
O uso de ferramentas de automação pode ser contra os Termos de Serviço de muitos jogos online e pode resultar em punições para sua conta. Use esta ferramenta por sua conta e risco. O desenvolvedor não se responsabiliza por qualquer consequência negativa do seu uso.
