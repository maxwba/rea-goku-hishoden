# Coleta local de referência

A demonstração Rust e o core de análise são programas separados. O executável nativo
não usa SameBoy nem lê ROM. Este procedimento não extrai imagens, áudio, textos,
instruções SM83 nem blocos de memória para arquivos: registra somente fingerprints
e metadados de execução. Todas as coletas ficam em private-analysis, ignorada pelo Git.

## Ferramentas

- SameBoy 1.0.4: fonte oficial LIJI32/SameBoy, tag v1.0.4, licença preservada em .tools.
- RGBDS 1.0.4: quatro executáveis macOS oficiais, checksum conferido, sem executar install.sh.
- Make e Clang instalados no sistema; SDK padrão das Command Line Tools.

```sh
./tools/build-reference-tools.sh
```

O script instala somente em .tools e fixa checksums dos downloads. Compila a dylib
do core e o boot DMG livre do SameBoy. O aplicativo Cocoa completo e o Ghidra não
são instalados. cppp não é necessário porque não geramos os headers distribuíveis.
O build original macOS oculta todos os símbolos da dylib; o script fornece LDFLAGS
para disponibilizar sua API pública. Compilação, carregamento via ctypes e execução
real foram validados em macOS ARM64. Não foi configurado MCP.

Fontes primárias: https://github.com/LIJI32/SameBoy e https://github.com/gbdev/rgbds.

## Coleta reproduzível

Substituir arquivo-local.gb pelo caminho da referência local; não copiá-la ao projeto
Rust, às fixtures nem a serviços externos. Use um nome novo para cada resultado.

```sh
python3 tools/reference_probe.py --rom "arquivo-local.gb" \
  --scenario tools/scenarios/idle.json --output private-analysis/idle-a.jsonl
python3 tools/reference_probe.py --rom "arquivo-local.gb" \
  --scenario tools/scenarios/idle.json --output private-analysis/idle-b.jsonl
python3 tools/compare_probes.py private-analysis/idle-a.jsonl private-analysis/idle-b.jsonl
```

Modelo fixo DMG-B, seed 1 e boot livre do SameBoy, sem bateria salva nem save state
carregados. Cada evento define o conjunto completo de botões mantidos desde aquele
frame até o próximo evento. Frames são indexados a partir de zero e avançados por
GB_run_frame, conforme o core instalado. Eventos são aplicados antes de executar o frame.
Não é uma medição de latência do cartucho em hardware original.

O inspetor valida a referência antes da emulação. O JSONL registra identidade da ROM,
boot e biblioteca por SHA-256, formato de pixel/endian, cenário, hashes dos quadros,
PC e banco selecionado por frame. Pixels existem apenas em memória e são descartados.
Não há acesso de rede no coletor. Logs do core são suprimidos para evitar impressão de
conteúdo do jogo. O hash da ROM é conferido após a execução. Saída fora da pasta privada,
sobrescrita de coleta anterior e cenários inválidos são rejeitados.

## Evidências obtidas nesta etapa

Coletas completas de 900 frames por cenário, incluindo repetições independentes:

| Comparação | Resultado |
| --- | --- |
| Sem botões × repetição | Rastros idênticos nos 900 frames |
| Start × repetição | Rastros idênticos nos 900 frames |
| Sem botões × Start em 360, solto em 372 | Primeira diferença visual em 363; 537 frames divergentes |
| Start × Start seguido de Baixo em 600, solto em 612 | Primeira diferença visual em 601; 299 frames divergentes |

O hash de quadro mede igualdade de pixels, sem classificar a tela. PC e banco são
amostras por frame, não cobertura de todas as instruções. Não afirmamos que as diferenças
representam menu, início de partida, seleção de personagem ou outra semântica.
A reproducibilidade vale para este modelo, boot, seed, biblioteca e planos de entrada.
SGB, boot original, bateria e outros modelos ainda não foram comparados.

## Próximas evidências necessárias

1. Correlacionar as diferenças com observação local das telas, sem publicar capturas.
2. Instrumentar transições de estado e escritas WRAM/MBC2 em rastros privados.
3. Usar o disassembler SM83 do debugger em arquivos locais, preservando código extraído.
4. Repetir trajetórias e documentar apenas contratos comportamentais observados.
5. Implementar estados nativos e testes sintéticos a partir desses contratos, usando
   placeholders próprios até esclarecer a autorização de recursos e traduções.

## Segunda etapa: memória e navegação

O schema 2 inclui hashes de WRAM, VRAM, OAM e mapas de tiles, sem serializar seus bytes.
Comparações agora exigem identidade completa do backend e fingerprints completos
para esse schema. Coletas antigas sem identidade suficiente devem ser refeitas.

Ensaios de 1200 frames distinguiram três sequências visuais estáveis com limites e
reversão pelas direções, compatíveis com seleção por sprites. A altera mapas de tiles
nas condições do ensaio; B e Start adicionais não alteram pixels. Evidências e limites
em selection-contract.md. Semântica das opções ainda pendente de observação humana.

Analisar.command fornece essa observação em loopback, com presets e exportação dos
inputs. Veja local-observation.md. O binário Rust permanece independente dessa ferramenta.
