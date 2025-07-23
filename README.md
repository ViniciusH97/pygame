# SURVIVE IF YOU CAN 

Um jogo de sobrevivência 2D desenvolvido em Python com Pygame onde você deve sobreviver contra hordas de zumbis em um mundo pós-apocalíptico.

## Sobre o Jogo

**Survive If You Can** é um jogo de sobrevivência em 2D onde o jogador controla um sobrevivente em um mundo devastado por zumbis. O objetivo é sobreviver o máximo de tempo possível, eliminando zumbis e coletando munição enquanto explora um ambiente infinito.

### aracterísticas Principais
- Sistema de combate híbrido (corpo a corpo e à distância)
- IA dos zumbis com detecção e perseguição
- Sistema de munição com coleta e recarga
- Física realista com gravidade e pulo
- Background paralaxe dinâmico
- Sistema de pontuação e recordes
- Dificuldade progressiva baseada na pontuação

## Como Executar

### Pré-requisitos
- Python 3.7 ou superior
- Pygame 2.0+

### Instalação
1. Clone ou baixe o repositório
2. Navegue até a pasta do projeto:
```bash
cd pygame/jogo6/a06
```

3. Instale as dependências:
```bash
pip install pygame
```

4. Execute o jogo:
```bash
python main.py
```

**Alternativa para Linux:**
```bash
chmod +x main.py
./main.py
```

## Controles

### Movimentação
- **WASD** ou **Setas direcionais**: Mover o personagem
- **SHIFT** (segurar): Correr (movimento mais rápido)
- **ESPAÇO**: Pular

### Combate
- **Botão Esquerdo do Mouse**: Atirar (ataque à distância)
- **Botão Direito do Mouse**: Ataque corpo a corpo
- **R**: Recarregar munição

### Sistema
- **ESC**: Pausar jogo / Voltar ao menu
- **P**: Pausar/Despausar durante o jogo

## Como Jogar

1. **Sobrevivência**: Evite ser atacado pelos zumbis mantendo distância
2. **Combate**: Use ataques à distância para eliminar zumbis de longe, ou ataques corpo a corpo quando necessário
3. **Munição**: Colete caixas de munição que aparecem quando zumbis morrem
4. **Pontuação**: Elimine zumbis para aumentar sua pontuação e desbloquear mais desafios
5. **Progressão**: A dificuldade aumenta conforme sua pontuação - mais zumbis e spawn mais rápido

### Dicas de Sobrevivência
- Mantenha distância dos zumbis sempre que possível
- Gerencie sua munição - colete caixas de munição regularmente
- Use o pulo para escapar de situações difíceis
- Ataques corpo a corpo causam knockback - use para empurrar zumbis

## Sistemas Implementados

### Sistema do Jogador
- **Movimentação fluida**: Caminhada, corrida e pulo com física realista
- **Sistema de vida**: Barra de vida com invulnerabilidade temporária após dano
- **Combate duplo**: Ataques corpo a corpo (2 tipos) e à distância
- **Munição**: Sistema de munição atual (5) e reserva (15) com recarga

### Sistema de Zumbis
- **4 tipos diferentes**: Cada um com sprites e comportamentos únicos
- **IA**: Detecção, perseguição e ataque ao jogador
- **Movimento durante ataque**: Zumbis continuam se movendo ao atacar
- **Sistema de dano**: Diferentes valores de dano para cada tipo de ataque

### Sistema de Combate
- **Ataque 1**: Ataque corpo a corpo básico com knockback
- **Ataque 2** (Coronhada): Maior alcance e knockback mais forte
- **Tiro**: Ataque à distância com maior alcance
- **Hitboxes precisas**: Sistema de colisão otimizado para cada tipo de ataque

### Sistema de Progressão
- **Dificuldade adaptativa**: Mais zumbis conforme pontuação aumenta
- **Spawn inteligente**: Zumbis aparecem atrás e à frente do jogador
- **Recordes**: Sistema de salvamento de maior pontuação
- **Métricas**: Tempo sobrevivido, zumbis eliminados, pontuação total

### Sistemas Visuais
- **Background paralaxe**: Múltiplas camadas com velocidades diferentes
- **Animações fluidas**: Sistema de sprites animados para todas as ações
- **Efeitos visuais**: Knockback, flutuação de itens, transições suaves
- **Interface responsiva**: HUD com informações em tempo real

## Assets e Recursos

O jogo utiliza sprites profissionais organizados na seguinte estrutura:

```
imagens/
├── fonts/
│   └── Zombie_Holocaust.ttf    # Fonte temática do jogo
├── municao.png                 # Sprite da munição coletável
├── Raider_1/ (Personagem Principal)
│   ├── Idle.png               # Parado
│   ├── Walk.png               # Caminhando
│   ├── Run.png                # Correndo
│   ├── Attack_1.png           # Ataque corpo a corpo 1
│   ├── Attack_2.png           # Ataque corpo a corpo 2 (coronhada)
│   ├── Shot.png               # Atirando
│   ├── Jump.png               # Pulando
│   ├── Recharge.png           # Recarregando
│   ├── Dead.png               # Morte
│   └── Hurt.png               # Tomando dano
├── Zombie_1/ até Zombie_4/     # 4 tipos diferentes de zumbis
│   ├── Idle.png               # Parado
│   ├── Walk.png               # Caminhando
│   ├── Attack.png             # Atacando
│   ├── Dead.png               # Morte
│   └── Hurt.png               # Tomando dano
├── Postapocalypce2/Bright/     # Background principal
│   ├── sky.png                # Céu
│   ├── houses&trees_bg.png    # Fundo distante
│   ├── houses.png             # Casas do meio
│   ├── car_trees_etc.png      # Objetos do meio
│   ├── road.png               # Estrada
│   └── bird*.png              # Pássaros animados
└── Postapocalypce4/Bright/     # Background alternativo
    └── [estrutura similar]
```

## Tecnologias Utilizadas

- **Python 3.7+**: Linguagem de programação principal
- **Pygame 2.0+**: Framework para desenvolvimento de jogos 2D
- **JSON**: Armazenamento de recordes e configurações

### Especificações Mínimas
- **SO**: Windows 7+, macOS 10.9+, Ubuntu 16.04+
- **RAM**: 512MB
- **Processador**: CPU dual-core 1.5GHz
- **Espaço**: 50MB livres

## Contribuição

Este projeto foi desenvolvido como parte de um estudo de desenvolvimento de jogos com Pygame. Sugestões e melhorias são bem-vindas!

## Licença

Este projeto é de código aberto para fins educacionais.

