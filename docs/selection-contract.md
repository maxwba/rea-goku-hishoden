# C-001 — seleção vertical limitada

## Observações reproduzidas

Condições: SameBoy 1.0.4, DMG-B, boot livre, seed 1, sem bateria carregada.
Start pressionado nos frames 360–371. Pulsos direcionais de 12 frames, iniciados
no frame 600, espaçados por 60 frames. Coletas de 1200 frames.

- Sem direção, um Baixo e dois Baixo produzem três sequências visuais distintas.
- As sequências com dois, três, quatro e cinco Baixo coincidem nos últimos 120 frames.
- Cima a partir do estado inicial não altera os pixels nem OAM em relação ao controle.
- Após dois Baixo, um Cima coincide com o resultado de um Baixo nos últimos 120 frames.
- Após dois Baixo, dois ou três Cima coincidem com o controle sem direção nesse intervalo.
- OAM e pixels mudam com a seleção; VRAM e mapas de tiles permanecem iguais ao controle.
- A no frame 600 altera VRAM e mapas de tiles; B e outro Start não alteram os pixels
  no ensaio, embora WRAM registre diferenças. Isso não comprova ausência de efeitos internos.

Os planos de input ficam em tools/scenarios; registros detalhados somente em
private-analysis. Contagem da interface do visualizador é de frames executados;
as posições nos registros começam em zero.

## Hipótese

Os resultados são compatíveis com um seletor vertical de três posições, com limites,
implementado visualmente por sprites. O significado das posições e das telas ainda
precisa de classificação humana local. Não inferimos nomes, novos jogos, saves,
combate ou eventos específicos desses dados.

## Aplicação nativa

A navegação da demonstração agora usa três posições e para nos extremos; Cima e
Baixo não dão a volta. O teste de integração exercita o contrato com ações sintéticas
0 → 1 → 2 → 2 → 1 → 0 → 0. Os rótulos Diálogo exemplo, Opções e Sair continuam sendo
próprios da demo; não correspondem a uma tradução ou identificação das opções originais.

A reprodução nativa desta navegação passou nos testes. As primeiras classificações humanas foram reproduzidas e documentadas em
flow-contract.md; o significado textual das opções originais ainda não foi recuperado.
