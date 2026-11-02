# Engenharia reversa inicial

## Observação

Foi identificado um único dump Game Boy de 262144 bytes (256 KiB). Logo,
checksum do header e checksum global são válidos; tamanho declarado coincide.
Flags: CGB 0 (DMG), SGB 3; cartucho 0x06 (MBC2 com bateria).
Código de RAM 0 não significa ausência da RAM interna MBC2: 512 × 4 bits.
Hash e título do header ficam no relatório local privado, sem bytes extraídos.
O patch BPS existente permanece intacto e não foi aplicado.

Mapa físico inicial: 16 bancos de 16 KiB, índices 0 a 15.
Para cada banco b, intervalo do arquivo [b × 0x4000, (b + 1) × 0x4000).
Banco 0 ocupa a janela CPU 0000–3FFF; janela selecionável em 4000–7FFF.
Esse mapa descreve o formato, não identifica funções, textos nem recursos.

## Hipóteses

Nenhuma rotina ou mecânica foi identificada semanticamente. O nome do arquivo não comprova
versão, procedência ou correspondência do patch. Checksum válido não autentica origem.

## Próxima coleta local

1. Instalar e iniciar SameBoy; abrir a referência local sem serviços externos.
2. Registrar privadamente sequência de inputs desde reset, banco ativo e endereços CPU.
3. Observar transições da tela inicial e menus, com breakpoints de entrada e escrita
   de registradores MBC2; consultar a ajuda do debugger instalado antes dos comandos.
4. Fazer disassembly SM83 local dos caminhos executados, distinguindo código e dados.
   RGBDS serve para montagem/verificação; não é um disassembler completo.
5. Repetir percursos e documentar pré-condições, estados e resultados sem copiar recursos.
6. Só implementar fluxo e combate após evidências reproduzíveis. Testes públicos devem
   usar estados sintéticos próprios, nunca trechos da ROM.

## Localização

Inventário pendente em localization/inventory.json: tela inicial, menus, diálogos,
combate, textos em gráficos e créditos. Antes de extração/tradução, esclarecer licença
ou autorização para uso dos materiais. Depois: mapear tabela de caracteres e controles
localmente, atribuir chaves por contexto, revisar tradução e tamanho na tela, testar
acentos, quebras e paginação. Até lá, somente textos demonstrativos próprios.


## Primeira coleta dinâmica

Core SameBoy 1.0.4/DMG-B e boot livre preparados localmente com RGBDS 1.0.4.
Ferramentas e rastros separados do runtime Rust. Dois ensaios idle e dois com Start
foram idênticos nas respectivas repetições, com 900 frames cada. Start no frame 360
produziu a primeira diferença de pixels no 363; acrescentar Baixo no 600 produziu
primeira diferença em 601. Isso demonstra resposta aos inputs nas condições do ensaio,
sem identificar semanticamente as telas. Não derivamos regras de combate desses dados.
Procedimento, comandos, limites e próximos passos em reference-workflow.md.


## Evidência C-001 e classificação local

Ensaios adicionais com hashes de memória distinguiram três padrões de OAM/pixels,
com saturação ao repetir Baixo e reversão ao repetir Cima. VRAM e mapas de tiles
não mudaram nessas trajetórias; A alterou ambos. Isso sustenta a hipótese de seleção
por sprites com três posições, sem identificar seu significado ou os nomes das opções.
A demo adotou navegação limitada e teste sintético desse comportamento. Ver
selection-contract.md e local-observation.md para evidências e classificação humana.


## Checkpoints humanos reproduzidos

Cinco checkpoints locais foram classificados pelo usuário e reproduzidos com igualdade
de quadro, memória, PC, banco e tempo: tela inicial em 359, menu em 599, menus em 659
por duas trajetórias e diálogo em 2471. O contrato C-002 documenta essas observações.
Start leva da tela inicial a menu. Após A, a observação ainda foi menu; a passagem ao
diálogo ocorre depois de várias entradas, portanto não foi reduzida a uma ação única.
A demo recebeu tela inicial e motor de diálogo com narrativa e tempos próprios.
Semântica dos menus intermediários, diálogos originais e regras continuam pendentes.
