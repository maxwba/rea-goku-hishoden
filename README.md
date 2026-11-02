# REA Goku Hishōden Native

Base Rust/SDL3 para uma reimplementação nativa com localização pt-BR. O estado atual
é uma demonstração compilável com tela inicial, menu, diálogo progressivo e opções.
O jogo original completo, seus eventos e o combate ainda não foram reimplementados.

A aplicação funciona **sem ROM ou emulador**. Usa textos próprios, fonte pública e
renderização em 160 × 144, com escala inteira de 2x a 6x e três paletas próprias.
Ferramentas opcionais de referência ficam separadas do executável nativo.

## Compilar e executar no macOS

Requisitos: Rust estável com Cargo, compilador C/C++ das Command Line Tools e CMake.
Python 3 é necessário para os verificadores e ferramentas de análise. Node.js é usado
somente na verificação de sintaxe do visualizador. O alvo validado é macOS ARM64.

Instale Rust pelo [rustup oficial](https://rust-lang.org/tools/install/). Se CMake
estiver ausente, ele pode ser instalado com `brew install cmake`. Em seguida:

```sh
rustup component add rustfmt clippy
cargo build --locked
./Jogar.command
```

Também é possível abrir **Jogar.command** com duplo clique no Finder. O iniciador
mantém erros visíveis e salva diagnósticos locais em `logs/`, ignorada pelo Git.
Para executar pelo terminal sem o iniciador: `cargo run --locked`.

A SDL3 é compilada do código-fonte e vinculada estaticamente pelo Cargo; não é preciso
instalá-la globalmente. `Cargo.lock` fixa as dependências. `tools/dev.sh` usa ferramentas
locais de `.tools/` quando disponíveis e, caso contrário, as ferramentas do PATH.
Instalações locais, caches e executáveis compilados não são distribuídos no repositório.

## Controles da demonstração

- Tela inicial: Enter abre o menu.
- Menu: Cima/Baixo selecionam, parando nos extremos; Z ou Enter confirma.
- Diálogo exemplo: Z/Enter revela o texto restante e depois avança; Esquerda revisita
  a página anterior. Ao concluir, retorna ao menu.
- Opções: Cima/Baixo escolhem escala ou paleta; Esquerda/Direita ajustam.
- Esc retorna ou encerra na tela inicial/menu.

As preferências ficam em `saves/demo-preferences.json`, ignorada pelo Git. Arquivos
inválidos são preservados. A narrativa e a velocidade de apresentação são próprias
da demonstração, sem diálogos originais copiados.

## Verificações sem ROM

```sh
cargo fmt --check
cargo clippy --all-targets --locked -- -D warnings
cargo test --no-default-features --locked
cargo test --locked
cargo build --locked
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_localization.py
python3 tools/check_native.py
```

O último comando testa o loop SDL com vídeo virtual, preferências isoladas e eventos
sintéticos. A CI executa essas verificações sem ROM, patches ou recursos do jogo.
Resultados e limitações: [ambiente](docs/environment.md).

## Referência local opcional

ROM, patch, gráficos, músicas, diálogos extraídos, capturas, rastros, saves e ferramentas
instaladas não estão incluídos. Referências autorizadas permanecem exclusivamente locais.
O inspetor é somente leitura: `python3 tools/rom_inspector.py "arquivo-local.gb"`.
Guarde seus relatórios em `private-analysis/`, ignorada pelo Git.

No macOS ARM64, `./tools/build-reference-tools.sh` prepara SameBoy/RGBDS localmente em
`.tools/`. Com uma referência local válida, **Analisar.command** abre o visualizador
privado para marcar telas. As imagens ficam em memória; entradas, classificações e
roteiros permanecem na pasta privada. A demo Rust não utiliza essas ferramentas.

[Arquitetura](docs/architecture.md) · [Engenharia reversa](docs/reverse-engineering.md) ·
[REA/MCP](docs/rea-integration.md) · [Coleta de referência](docs/reference-workflow.md) ·
[Observação local](docs/local-observation.md) · [C-001](docs/selection-contract.md) ·
[C-002](docs/flow-contract.md).

## Próximas etapas

Identificar os menus intermediários a partir de evidências reproduzíveis, reconstruir
o fluxo de jogo e validar regras antes de implementar combate. Extração e localização
do conteúdo original dependem de esclarecer a autorização para uso desses materiais.
Até lá, os recursos e textos demonstrativos continuam próprios.
