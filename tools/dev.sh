#!/bin/sh
# Usa ferramentas locais quando disponíveis, sem alterar o ambiente do usuário.
set -eu
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
if [ -x "$PROJECT_ROOT/.tools/cargo/bin/cargo" ]; then
    export CARGO_HOME="$PROJECT_ROOT/.tools/cargo"
    export RUSTUP_HOME="$PROJECT_ROOT/.tools/rustup"
    PATH="$CARGO_HOME/bin:$PATH"
fi
if [ -x "$PROJECT_ROOT/.tools/python/cmake/data/bin/cmake" ]; then
    PATH="$PROJECT_ROOT/.tools/python/cmake/data/bin:$PATH"
fi
# Prefere o SDK padrão das Command Line Tools. O xcrun pode selecionar um SDK
# beta mais recente que o linker instalado. SDKROOT explícito sempre prevalece.
if [ "$(uname -s)" = "Darwin" ] && [ -z "${SDKROOT:-}" ] \
    && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk ]; then
    export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk
fi
export PATH
# Ao abrir o script sem argumentos, inicia a demonstração.
if [ "$#" -eq 0 ]; then
    set -- run
fi
exec cargo "$@"
