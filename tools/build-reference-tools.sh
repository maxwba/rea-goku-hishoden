#!/bin/sh
# Dependências de análise isoladas. Não lê ROM, não altera o sistema ou o GitHub.
set -eu
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_ROOT"
mkdir -p .tools/sameboy .tools/rgbds
case "$(uname -s):$(uname -m)" in
    Darwin:arm64) ;;
    *) printf '%s\n' 'Este procedimento foi validado somente em macOS ARM64.' >&2; exit 1 ;;
esac
curl --proto '=https' --proto-redir '=https' --tlsv1.2 -fLsS \
    https://github.com/LIJI32/SameBoy/archive/refs/tags/v1.0.4.tar.gz \
    -o .tools/sameboy/source.tar.gz
curl --proto '=https' --proto-redir '=https' --tlsv1.2 -fLsS \
    https://github.com/gbdev/rgbds/releases/download/v1.0.4/rgbds-macos.zip \
    -o .tools/rgbds/archive.zip
python3 - <<'PY'
from pathlib import Path
import hashlib
import zipfile
source = Path('.tools/sameboy/source.tar.gz')
source_hash = '5786552a51e3d1d26d768eec65485b5e8bebd4dc295fbd6194026edec1b7d474'
if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
    raise SystemExit('Arquivo fonte SameBoy divergente: interrompido.')
archive = Path('.tools/rgbds/archive.zip')
expected = '62d1669bbe3b2bf2cfc2e72076d3c8c00fc023a9cc15d458f0c723bd9d0312c4'
if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
    raise SystemExit('Checksum RGBDS divergente: interrompido.')
with zipfile.ZipFile(archive) as files:
    # Extrai somente os quatro executáveis; não executa install.sh.
    for name in ['rgbasm', 'rgblink', 'rgbfix', 'rgbgfx']:
        target = Path('.tools/rgbds') / name
        target.write_bytes(files.read(name))
        target.chmod(0o755)
PY
if [ ! -d .tools/sameboy/SameBoy-1.0.4 ]; then
    tar -xzf .tools/sameboy/source.tar.gz -C .tools/sameboy
fi
SDK_ROOT=${SDKROOT:-/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk}
export SDKROOT="$SDK_ROOT"
# Sobrescreve LDFLAGS para expor a API pública: o Makefile macOS original
# inclui exported_symbols_list=/dev/null, que oculta os símbolos da dylib.
make -C .tools/sameboy/SameBoy-1.0.4 -B -j4 CONF=release \
    SYSROOT="$SDK_ROOT" RGBDS="$PROJECT_ROOT/.tools/rgbds/" \
    LDFLAGS="-lc -lm -ldl -isysroot $SDK_ROOT -flto" \
    build/lib/libsameboy.dylib build/bin/BootROMs/dmg_boot.bin \
    > .tools/sameboy/build.log 2>&1
.tools/rgbds/rgbasm --version
printf '%s\n' 'SameBoy 1.0.4 preparado para referência local. Veja .tools/sameboy/build.log.'
