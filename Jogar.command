#!/bin/bash
# Abre pelo Finder ou Terminal; mantém o erro visível se a inicialização falhar.
set -u
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_ROOT" || exit 1
if ! mkdir -p logs; then
    printf 'Não foi possível criar a pasta de diagnóstico.\n'
    read -r -p 'Pressione Enter para fechar... ' _
    exit 1
fi
LOG_FILE="logs/session-$(date +%Y%m%d-%H%M%S)-$$.log"
printf 'Iniciando a demonstração. Diagnóstico: %s\n' "$LOG_FILE"
./tools/dev.sh run 2>&1 | tee "$LOG_FILE"
STATUS=${PIPESTATUS[0]}
if [ "$STATUS" -ne 0 ]; then
    printf '\nA demonstração encerrou com erro (%s).\n' "$STATUS"
    printf 'O diagnóstico foi salvo em %s\n' "$LOG_FILE"
    if [ -t 0 ]; then
        read -r -p 'Pressione Enter para fechar... ' _
    fi
fi
exit "$STATUS"
