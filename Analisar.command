#!/bin/bash
# Ferramenta privada de análise; não é o executável do jogo nativo.
set -u
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_ROOT" || exit 1
python3 tools/reference_viewer.py --open
STATUS=$?
if [ "$STATUS" -ne 0 ] && [ -t 0 ]; then
    printf '\nNão foi possível iniciar a ferramenta local de análise.\n'
    read -r -p 'Pressione Enter para fechar... ' _
fi
exit "$STATUS"
