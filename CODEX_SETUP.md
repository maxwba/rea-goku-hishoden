# Codex: REA Goku Hishōden Native

## Missão

Você é o agente principal de engenharia do projeto **rea-goku-hishoden**, uma reimplementação nativa, em **Rust**, de **Dragon Ball Z: Goku Hishōden** (Game Boy), com localização completa em **português brasileiro**. O executável final **não pode depender de ROM ou emulador em tempo de execução**.

**Repositório oficial:** https://github.com/maxwba/rea-goku-hishoden

**Ambiente alvo de desenvolvimento:** macOS Apple Silicon (ARM64).

**Agente:** OpenAI Codex.

**Diretório de trabalho:** raiz do repositório clonado, onde este arquivo e uma cópia local do jogo foram colocados.

## Regras de segurança e preservação

1. **Há um arquivo do jogo na raiz do projeto.** Antes de criar ou alterar arquivos, identifique arquivos candidatos pelas extensões `.gb`, `.gbc`, `.rom`, `.bin` ou `.iso`, sem presumir nome ou formato. Um cartucho de Game Boy normalmente é um dump `.gb`, não uma imagem ISO. Inspecione tamanho, assinatura/header e metadados para identificar o formato real. Se houver vários candidatos ou formato inesperado, peça confirmação antes de prosseguir com a análise específica.
2. Trate o arquivo do jogo como **material local de referência**, exclusivamente para engenharia reversa e testes comparativos autorizados. Não o incorpore ao executável, aos testes distribuídos, a fixtures, screenshots ou a qualquer artefato publicado.
3. **Antes de executar `git add`**, configure `.gitignore` para ignorar `*.gb`, `*.gbc`, `*.rom`, `*.iso` e dumps/derivados privados. Não ignore indiscriminadamente `*.bin` se isso afetar arquivos legítimos; ignore o arquivo identificado nominalmente e use uma pasta privada ignorada, por exemplo `private-roms/`. Verifique `git status --ignored` e `git ls-files` para garantir que o arquivo não esteja rastreado. Se já estiver rastreado, interrompa o fluxo de publicação e solicite instruções para removê-lo do índice/histórico conforme necessário.
4. Não exiba nem envie conteúdo binário da ROM para serviços externos, agentes remotos ou logs. Não faça upload do arquivo a GitHub, issues, PRs, Actions, artefatos de CI ou serviços de terceiros. Registre no máximo metadados não sensíveis, como hash SHA-256, tamanho e tipo de cartucho, em documentação local apropriada. Não grave caminhos pessoais absolutos no repositório.
5. Não inclua gráficos, música, textos originais ou código protegido nos commits sem autorização. Para a aplicação demonstrativa, utilize recursos próprios e textos marcados como exemplos.
6. Preserve arquivos existentes, histórico Git e configurações do usuário. Não use `git push --force`, comandos destrutivos ou instalação privilegiada sem aprovação. Não presuma que permissões de rede, sistema ou GitHub estejam disponíveis.
7. Não invente rotinas, offsets, mecânicas ou resultados de testes. Separe claramente **observação**, **hipótese** e **implementação validada**.

## Fase 1: Auditoria do repositório e ambiente

- Confirme a raiz do repositório, `git remote -v`, branch padrão, arquivos existentes, estado do Git e autenticação `gh auth status`.
- Se o diretório ainda não for um clone do repositório oficial, explique o estado encontrado e prepare um clone seguro sem sobrescrever a ROM local ou outros arquivos.
- Identifique a ROM local conforme as regras acima e **proteja-a contra versionamento imediatamente**.
- Detecte arquitetura, macOS, shell e disponibilidade de Homebrew, Git, GitHub CLI, `rustup`, `rustc`, `cargo`, `rustfmt`, `clippy`, Python 3, Java, CMake, SDL3, Ghidra, SameBoy e RGBDS.
- Documente as versões e eventuais bloqueios em `docs/environment.md`, sem revelar dados privados.

## Fase 2: Instalação das dependências

- Instale apenas ferramentas ausentes, preferindo Homebrew e fontes oficiais. Para Rust, use `rustup` e a toolchain estável, com `rustfmt` e `clippy`.
- Prepare SDL3 e bibliotecas necessárias para compilação nativa no macOS ARM64.
- Prepare Ghidra, SameBoy e RGBDS para análise e comparação, verificando disponibilidade e compatibilidade reais.
- Revise scripts externos antes de executá-los; peça aprovação quando houver alterações globais, privilegiadas ou potencialmente destrutivas.
- Confirme o funcionamento de cada dependência com um comando de versão ou teste real.

## Fase 3: REA + Codex

- Inspecione a documentação atual de https://github.com/morluto/rea e identifique requisitos, instalação, integração MCP e compatibilidade com OpenAI Codex.
- Verifique se o backend de análise suporta o processador **Sharp SM83 / LR35902** do Game Boy. Não assuma que suporte a Ghidra significa suporte automático a ROMs Game Boy.
- Configure MCP no Codex **somente se houver um caminho comprovado e seguro**; teste a conexão e as ferramentas expostas.
- Se o REA não atender ao caso, documente a limitação e adote um fluxo alternativo com debugger SameBoy, disassembly SM83 e scripts próprios.
- Registre procedimentos e evidências em `docs/rea-integration.md`.

## Fase 4: Inspeção inicial do jogo local

- Crie `tools/rom_inspector.py` com leitura **somente local** e somente leitura do arquivo fornecido.
- Valide o header do Game Boy (quando aplicável), incluindo título, flag CGB, tipo de cartucho/mapper, tamanhos declarados de ROM/RAM, checksums e SHA-256. Sinalize discrepâncias, truncamentos e arquivos não reconhecidos; não faça suposições com base apenas na extensão.
- Execute o inspetor contra o arquivo encontrado. Se não for um dump Game Boy válido, interrompa a análise e explique o que foi detectado.
- Registre mapa inicial de bancos, hipóteses e evidências em `docs/reverse-engineering.md`, sem copiar dados protegidos para arquivos públicos.
- Não publique a ROM nem seus dados extraídos protegidos.

## Fase 5: Aplicação nativa em Rust

Crie a estrutura modular a seguir, adaptando-a se houver justificativa técnica:

```text
rea-goku-hishoden/
├── .github/workflows/ci.yml
├── docs/
│   ├── environment.md
│   ├── architecture.md
│   ├── reverse-engineering.md
│   └── rea-integration.md
├── tools/rom_inspector.py
├── assets/README.md
├── localization/pt-BR.json
├── src/
│   ├── main.rs
│   ├── engine/
│   ├── scenes/
│   ├── battle/
│   ├── world/
│   ├── assets/
│   ├── localization/
│   └── save/
├── tests/
├── AGENTS.md
├── CODEX_SETUP.md
├── Cargo.toml
├── Cargo.lock
├── .gitignore
└── README.md
```

- Use **Rust estável**, **SDL3** para janela, vídeo e input, e **Serde** quando fizer sentido para dados.
- Implemente janela com resolução lógica **160 × 144**, escala inteira e pixels nítidos.
- Implemente um menu **demonstrativo**, com teclado e caracteres acentuados em pt-BR, sem reutilizar recursos protegidos do jogo.
- Mantenha separação entre loop principal, cenas, regras, renderização, localização e persistência.
- Prepare testes de unidade e integração. Não implemente combate ou eventos originais antes de ter evidências suficientes.
- Crie `AGENTS.md` para orientar sessões futuras do Codex: fidelidade, rastreabilidade de evidências, segurança da ROM, localização e testes.

## Fase 6: Localização completa pt-BR

- Prepare sistema de chaves estáveis para textos, com arquivos de idioma versionáveis **sem copiar diálogos originais protegidos**.
- Suporte UTF-8, acentos, quebra de linha e renderização de fontes.
- Crie verificação automatizada de chaves ausentes e inventário de strings pendentes.
- Planeje extração e tradução dos diálogos, menus, telas, mensagens embutidas em gráficos e créditos, com revisão contextual.
- Use placeholders até que a extração e a autorização para uso dos materiais estejam esclarecidas.

## Fase 7: Build, testes e CI

Execute, corrigindo falhas quando possível:

```bash
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
cargo build
```

- Quando houver acesso a ambiente gráfico, execute a aplicação e valide janela, controles, escala e acentos.
- Configure GitHub Actions para as verificações compatíveis com os runners escolhidos, sem depender da ROM local nem disponibilizar binários protegidos.
- Registre resultados reais, comandos e limitações.

## Fase 8: Publicação no GitHub

- Destino **exclusivo**: https://github.com/maxwba/rea-goku-hishoden.
- Antes do commit, revise `git diff`, `git status`, arquivos ignorados e conteúdo staged. Garanta que ROM, dumps, segredos e recursos protegidos não serão publicados.
- Crie branch `feat/initial-rust-setup` (ou outra branch adequada caso já exista), commits descritivos e faça push.
- Abra um Pull Request para a branch padrão usando `gh` quando autenticado e autorizado. **Não faça merge automático.**
- Se push ou PR não forem possíveis, entregue comandos exatos e explique o bloqueio sem declarar publicação concluída.

## Entregáveis e relatório final

1. Projeto Rust compilável e demonstração nativa sem ROM em runtime.
2. Inspetor local do header do cartucho e relatório de identificação do arquivo encontrado.
3. Documentação de arquitetura, ambiente, engenharia reversa e REA/MCP.
4. `AGENTS.md`, `.gitignore`, README e CI.
5. Testes executados com resultados verificáveis.
6. Branch, commits e URL do PR, se criados.
7. Próximos passos específicos para recuperar a tela inicial, menus, fluxo de jogo e mecânicas originais a partir de evidências.

**Comece pela auditoria da raiz do projeto e proteção imediata da ROM contra versionamento. Depois prossiga incrementalmente, validando cada fase.**
