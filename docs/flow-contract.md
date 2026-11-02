# C-002 — entrada por tela inicial e checkpoints humanos

## Evidências verificadas

As observações abaixo foram marcadas pelo usuário no visualizador local. Cada
checkpoint foi reproduzido a partir do reset com os mesmos inputs e backend;
hash de quadro, hashes de memória, PC, banco e tempo emulado coincidiram.
Os registros completos e seus fingerprints permanecem privados.

| Sessão de reset | Frame (índice zero) | Classificação humana | Condição registrada |
| --- | --- | --- | --- |
| 1 | 359 | Tela inicial | Sem botões |
| 3 | 599 | Menu | Start nos frames 360–371 |
| 4 | 659 | Menu | Start seguido de Baixo |
| 5 | 659 | Menu | Start seguido de A |
| 5 | 2471 | Diálogo | Continuação interativa com várias entradas |

A transição tela inicial → menu mediante Start está confirmada nessas condições.
O estado após A também foi classificado como menu; não concluímos que A no primeiro
menu abra diretamente o diálogo. O checkpoint de diálogo ocorre após uma sequência
mais longa, incluindo direções, A e B. Os significados das opções e a estrutura dos
menus intermediários permanecem sem identificação textual.

## Implementação nativa

A demo inicia em uma tela própria, com Enter representando Start para abrir seu menu.
O menu conserva rótulos próprios: Diálogo exemplo, Opções e Sair. Z confirma; Enter
continua funcionando como atalho da demonstração. Essas entradas não são tradução
ou identificação das opções originais. O caminho Diálogo exemplo é autoral.

A caixa de diálogo oferece texto progressivo em UTF-8, paginação, identificação
"Exemplo" e contador de páginas. Uma confirmação primeiro revela o restante da página;
a seguinte avança, ou conclui retornando ao menu. Esquerda revisita a página anterior;
Esc retorna ao menu. A animação usa 30 ms por caractere como escolha da demo.
Nem esse intervalo, nem esses atalhos de revisão, nem o conteúdo foram recuperados
do cartucho. Os textos são próprios, sem diálogos originais copiados.

## Verificação reproduzível

```sh
python3 tools/verify_observations.py
python3 tools/check_native.py
```

O primeiro comando lê somente os checkpoints humanos privados completos e rejeita
ROM/backend incompatíveis ou divergência de estado. Não modifica classificações.
O segundo executa um roteiro sintético de 38 frames pelo tratamento de eventos e
renderização SDL: título, menu, diálogo, opções, mudança de escala/paleta e retorno.
Ele usa vídeo virtual, inputs de teste e diretório temporário. Não lê nem grava as
preferências do usuário. Não depende de ROM ou SameBoy.

A versão sdl3 usada não aceita KeyDown em sua API push_event. O teste une eventos
sintéticos ao iterador de eventos do mesmo loop; não usa injeção na fila do sistema.
O teste verifica renderizador, controles interpretados, dimensões, cenas e texto
parcial. A aparência e a interação no desktop continuam dependendo de teste humano.
