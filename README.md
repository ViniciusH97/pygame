# Survive If You Can

Um jogo de sobrevivência 2D desenvolvido em Python com Pygame.

## Como rodar o jogo

### Pré-requisitos
- Python 3.7 ou superior
- Pygame

### Instalação
1. Instale o Pygame:
```bash
pip install pygame
```

2. Execute o jogo:
```bash
python main.py
```

Ou dê permissão de execução e rode diretamente:
```bash
chmod +x main.py
./main.py
```

## Controles

- **WASD** ou **Setas**: Mover
- **SHIFT**: Correr
- **Botão Esquerdo do Mouse**: Atirar
- **Botão Direito do Mouse**: Ataque corpo a corpo
- **ESPAÇO**: Pular
- **R**: Recarregar munição
- **ESC**: Voltar ao menu / Sair

## Estrutura do Projeto

```
a06/
├── main.py              # Ponto de entrada principal
├── game.py              # Lógica principal do jogo
├── menu.py              # Sistema de menu
├── player.py            # Classe do jogador
├── zombie.py            # Classe dos zumbis
├── zombie_spawner.py    # Sistema de spawn dos zumbis
├── animated_sprite.py   # Sistema de animação
├── background.py        # Sistema de background com paralaxe
└── README.md           # Este arquivo
```

## Recursos

- **Player customizável**: Sistema de personagens com diferentes sprites
- **Sistema de combate**: Ataques corpo a corpo e à distância
- **IA dos inimigos**: Zumbis com comportamento inteligente
- **Sistema de munição**: Munição limitada com recarga
- **Sistema de vida**: Barra de vida e invulnerabilidade temporária
- **Background paralaxe**: Múltiplas camadas de fundo com velocidades diferentes
- **Animações fluidas**: Sistema de sprites animados
- **Debug visual**: Hitboxes visíveis para desenvolvimento

## Desenvolvimento

Para adicionar novos recursos:

### Novos inimigos
Edite `zombie.py` e `zombie_spawner.py`

### Novos personagens
Edite `player.py` e adicione os sprites na pasta `imagens/`

### Novos níveis
Edite `game.py` e `background.py`

### Novos menus
Edite `menu.py`

## Assets

O jogo espera que os assets estejam organizados na seguinte estrutura:
```
imagens/
├── Raider_1/
│   ├── Idle.png
│   ├── Walk.png
│   ├── Run.png
│   ├── Attack_1.png
│   ├── Attack_2.png
│   ├── Shot.png
│   ├── Jump.png
│   ├── Recharge.png
│   ├── Dead.png
│   └── Hurt.png
├── Zombie_1/
├── Zombie_2/
├── Postapocalypce2/
└── Postapocalypce4/
```

## Licença

[A definir]
