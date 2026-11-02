# REA e fluxo alternativo — consulta em 2026-11-02

Fontes oficiais consultadas:
- https://github.com/morluto/rea
- https://sameboy.github.io/
- https://rgbds.gbdev.io/
- https://github.com/NationalSecurityAgency/ghidra

O README atual do REA oferece setup via `npx rea-agents setup`, declara integração
com Codex e backends nativos incluindo Ghidra. Exige Node 22.23.4+, 24.22.1+ ou
26.12.1+ nas respectivas séries. O Node local 26.10.0 não satisfaz esse requisito.
O setup altera registros MCP/instruções e pede revisão das mudanças; não foi executado.

Não foi comprovado suporte SM83/LR35902 e carregamento bancado MBC2 no backend.
Suporte genérico a Ghidra não comprova isso. Não foi importada ROM no REA, não foi
registrado MCP, e nenhuma conexão ou ferramenta REA foi testada.
Para reavaliar: obter versão fixada de fonte oficial em diretório sem ROM, revisar
pacote e setup, comprovar linguagem SM83 e loader com programa sintético próprio,
revisar configuração proposta e testar conexão/listagem antes de qualquer análise.
Não enviar bytes da ROM ao agente mesmo que o backend execute localmente.

Alternativa adotada no planejamento: debugger SameBoy para rastros locais,
disassembly SM83 separado e inspetor Python próprio. O inspetor e o core SameBoy 1.0.4 já foram
validados com coleta local reproduzível. O core inclui debugger/disassembler SM83,
mas a interface de debugger não foi usada para classificar rotinas nesta etapa.
RGBDS 1.0.4 também está disponível localmente; o aplicativo Cocoa não foi instalado. Ghidra requer JDK compatível
(documentação atual solicita JDK 25); confirmar na versão escolhida.
