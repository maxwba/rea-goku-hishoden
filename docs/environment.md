# Ambiente e validações

## Plataforma validada

macOS 26.6.2 ARM64, Apple Clang 21.0.0, Python 3.9.6, Rust/Cargo 1.99.1,
rustfmt 1.10.0, clippy 0.1.99 e CMake 4.4.4. SDL3 3.4.18 é compilada e vinculada
estaticamente pelo Cargo. As dependências estão fixadas em Cargo.lock.

O desenvolvimento usou ferramentas isoladas em .tools, sem alterar o PATH global.
Essa pasta não é versionada nem necessária em um checkout com Rust/CMake no PATH.
As ferramentas opcionais de referência são SameBoy 1.0.4 e RGBDS 1.0.4, também locais.
A biblioteca de análise e seu boot livre foram compilados; o aplicativo Cocoa completo,
Ghidra e integração MCP não foram configurados.

## Resultados executados

- cargo fmt --check: passou.
- cargo clippy --all-targets -- -D warnings: passou sem avisos.
- cargo test --no-default-features: 15 testes passaram.
- cargo test: 15 testes passaram.
- cargo build: passou; executável nativo ARM64 gerado.
- Python unittest: 33 testes passaram, sem usar a ROM.
- Verificador de localização: 22 chaves consistentes entre catálogo, inventário e Rust.
- tools/check_native.py: percurso SDL sintético de 38 frames passou com vídeo virtual.
  Percorre título, menu, texto parcial, paginação, opções e retorno; tamanho final
  320 × 288 e paleta Gray confirmados. Preferências ficam isoladas no teste.
- JavaScript e scripts de shell: sintaxe validada.
- Referência local: cinco checkpoints humanos reproduzidos com igualdade de quadro,
  hashes de memória, PC, banco e tempo; os registros continuam privados.

A abertura por duplo clique, a escala, as paletas e o visualizador de referência foram
confirmados pelo usuário. A nova tela inicial e a animação de diálogo foram verificadas
por testes e vídeo virtual; sua inspeção visual no desktop ainda está pendente.

## Compatibilidade do SDK Apple

A seleção automática de MacOSX27.0.sdk falhou com o linker instalado, por formato de
arquitetura desconhecido. O SDK padrão das Command Line Tools, MacOSX26.5.sdk,
compilou corretamente. tools/dev.sh prefere o SDK padrão quando SDKROOT não está
definido. Nenhuma configuração do sistema é modificada; SDKROOT explícito prevalece.

## Separação de dados

O binário Rust não depende de ROM, emulador, boot ROM ou rastros privados. Os textos,
narração, paletas e gráficos da demo são próprios. Os tempos de apresentação também
são escolhas autorais, sem alegação de recuperação dos tempos originais.

ROM e patch tiveram hashes conferidos e permaneceram inalterados. Coletas e observações
humanas não são distribuídas. A CI contém somente verificações independentes da referência;
o resultado de cada execução remota deve ser consultado no GitHub Actions.
