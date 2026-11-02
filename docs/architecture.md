# Arquitetura da demonstração

O binário usa textos próprios e fonte pública. Não lê ROM, não contém emulador nem
aplica patch. SameBoy e o observador local são ferramentas separadas de análise.

- engine: janela SDL3 e renderização em grade lógica 160 × 144; evento de teclado
  vira Action antes de chegar ao controlador, e o tempo transcorrido avança o texto.
- scenes: tela inicial, menu, diálogo demonstrativo e opções. App não depende de SDL.
- scenes/dialogue: paginação UTF-8 e apresentação progressiva; confirmações não pulam
  texto ainda oculto. A velocidade de 30 ms por caractere é própria da demo.
- settings: escala inteira 2x–6x e paletas próprias Verde, Azul e Cinza.
- assets: glifos Basic Latin e Latin-1 de font8x8.
- localization: 22 chaves estáveis; placeholders das opções verificados.
- save: seleção e vídeo em JSON; leitura limitada a 4 KiB, temporário exclusivo e
  rename após sync. Preferências antigas recebem configurações padrão.
- battle/world: reservados; regras originais ainda sem implementação validada.

O desenho usa retângulos inteiros por pixel, sem filtragem. A escala padrão é 4x;
a janela varia de 320 × 288 a 960 × 864. Preferências inválidas são preservadas,
com gravação desabilitada naquela execução. Não há save de progresso do jogo.

O fluxo começa na tela inicial, aberta com Enter. No menu, Cima/Baixo selecionam e
param nos extremos; Z ou Enter confirma. Em Diálogo exemplo, Z/Enter revela o texto,
avança ou conclui; Esquerda revisita a página anterior e Esc retorna. O corpo ocupa
18 colunas e seis linhas por página. Opções conserva escala e paleta ajustáveis.

C-001 descreve a navegação limitada. C-002 confirma a entrada por Start e distingue
os checkpoints humanos do fluxo autoral da demo. Os rótulos, a narrativa e os tempos
de apresentação não representam uma localização ou recuperação do jogo original.

A feature native é padrão; --no-default-features testa o núcleo sem SDL3. Os 15 testes
Rust passaram em ambas as configurações. Testes Python cobrem inspeção, localização,
planos de inputs, rotas locais, proteção das saídas e verificação de checkpoints.

SDL3 é compilada e vinculada estaticamente pelo Cargo. tools/dev.sh usa ferramentas
locais quando disponíveis. Jogar.command abre a demo e mantém falhas visíveis.
--smoke-test percorre cenas e renderização com inputs sintéticos, sem preferências;
tools/check_native.py executa esse teste com vídeo virtual e isolamento de arquivos.
O build da demo e esse teste não dependem da referência local.

O observador usa loopback; pixels só existem em memória e inputs/classificações ficam
na pasta privada. A interface de referência e a demo anterior foram testadas pelo usuário.
A nova tela inicial e o novo diálogo ainda aguardam inspeção visual no desktop.
