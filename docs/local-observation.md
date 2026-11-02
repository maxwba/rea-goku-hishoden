# Observação humana local

A ferramenta é separada do jogo nativo. Jogar.command continua abrindo a demonstração
Rust sem ROM; Analisar.command usa somente a referência local no próprio computador.

## Como observar

1. Abra Analisar.command com duplo clique. O navegador padrão abre uma página local.
2. Em Pontos de observação, escolha uma sequência e clique Carregar ponto.
3. Observe a tela, selecione sua classificação e clique Salvar observação local.
4. Repita para Sem botões, Após Start, Start e Baixo e Start e A. As categorias são
   descrições suas; a ferramenta não tenta identificar automaticamente o conteúdo.
5. Para explorar outros pontos, clique Rodar e use setas, Z (A), X (B), Enter (Start)
   e Backspace (Select). Pause para marcar. Reiniciar começa uma nova sequência.
6. Ao terminar, use Ctrl+C no Terminal que iniciou a ferramenta.

Não é necessário transcrever diálogos, compartilhar capturas ou copiar recursos.
O objetivo é vincular a sequência reproduzível de botões a uma classificação humana.
A interface mostra a quantidade de frames executados; o registro da observação usa
o índice do último frame, começando em zero. A execução interativa não promete
sincronização de áudio nem velocidade exata de hardware.

## Dados e separação

A página e os scripts são locais, sem CDNs, fontes externas ou analytics. O servidor
vincula-se somente a 127.0.0.1 em porta temporária, verifica Host/Origin e exige um
segredo efêmero nos pedidos de emulação. Esse segredo vai ao navegador no fragmento
da URL e não é impresso no Terminal nem gravado nos registros. Conteúdo tem no-store;
nenhum arquivo da raiz ou da pasta privada é servido por uma rota genérica.
Não abra o visualizador com ferramentas de captura ou navegação do agente.

Pixels passam apenas entre memória do core e navegador no mesmo computador.
A ferramenta não os grava em arquivo. Os registros privados contêm hashes, metadados,
entradas e classificações escolhidas de uma lista fixa; não há campo para copiar textos.
Ao marcar, reiniciar ou encerrar normalmente, uma sequência de inputs é exportada
como .scenario.json dentro de private-analysis. A referência não é modificada.

Para resumir as classificações sem expor pixels ou memória:

```sh
python3 tools/summarize_observations.py
```

Para reproduzir um roteiro exportado, fornecer seu caminho a --scenario do
reference_probe.py e escolher um nome de saída novo na pasta privada.

## Validações realizadas

- Rotas locais testadas com dados sintéticos; origens, Host e segredo incorretos rejeitados.
- Rotas de arquivos privados e tentativas de acesso fora dos recursos previstos rejeitadas.
- HTTP real com core local: preset de 600 frames e dimensões do quadro válidos.
- Sessões de 432 e 600 frames exportadas e reproduzidas; fingerprints, PC, banco e tempo
  do último frame coincidiram integralmente.
- Nenhum quadro original foi exibido ao agente, capturado, salvo em imagem ou enviado
  a serviço externo durante essas verificações.
- Testes não confirmam a aparência do visualizador no desktop; essa observação cabe
  ao usuário local. Nenhuma classificação de tela foi atribuída automaticamente.


## Conferir o que já foi marcado

```sh
python3 tools/verify_observations.py
```

O verificador refaz cada época de reset até os checkpoints marcados e compara
fingerprints, PC, banco e tempo. Não mostra a tela nem altera classificações. Só usa
linhas completas do registro, para permitir que o observador continue aberto.
As cinco primeiras marcações humanas foram reproduzidas com sucesso.
