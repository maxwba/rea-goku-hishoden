# Orientações do projeto

- Responder em português do Brasil; preservar as preferências globais do usuário.
- Ler CODEX_SETUP.md antes de trabalhar e seguir suas fases e regras.
- ROM e patch são referências privadas locais. Nunca enviar bytes, capturas, dumps,
  diálogos, gráficos ou músicas a serviços externos, agentes ou commits.
- Não executar git add antes de validar ignore, arquivos rastreados e staged.
- Não alterar ROM nem aplicar patch sem autorização explícita.
- Separar observação, hipótese e implementação validada; citar evidências reproduzíveis.
- Não implementar mecânicas originais com base em suposições.
- Executável nativo independente de ROM e emulador. Recursos demonstrativos próprios.
- Textos com chaves estáveis em localization/pt-BR.json; validar acentos e glifos.
- Executar testes Python, verificador de localização, cargo fmt --check,
  cargo clippy --all-targets -- -D warnings, cargo test e cargo build.
- Não declarar compilação, inspeção visual ou publicação sem execução comprovada.
- Publicar exclusivamente em maxwba/rea-goku-hishoden, por branch e PR, sem merge automático.
- Preservar histórico remoto: obter clone antes de integrar arquivos locais.
