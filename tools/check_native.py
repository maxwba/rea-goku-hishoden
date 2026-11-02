"""Executa o percurso SDL da demo com vídeo virtual e preferências isoladas."""
import os
import subprocess
import tempfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    binary = root / 'target/debug/rea-goku-hishoden'
    if not binary.is_file():
        print('Execute ./tools/dev.sh build antes de verificar o percurso nativo.')
        return 1
    environment = {**os.environ, 'SDL_VIDEODRIVER': 'dummy',
                   'SDL_RENDER_DRIVER': 'software', 'SDL_AUDIODRIVER': 'dummy'}
    with tempfile.TemporaryDirectory(prefix='rea-native-check-') as folder:
        save = Path(folder) / 'saves/demo-preferences.json'
        save.parent.mkdir()
        original = b'preferences intentionally invalid for the smoke test'
        save.write_bytes(original)
        try:
            result = subprocess.run([str(binary), '--smoke-test'], cwd=folder,
                                    env=environment, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f'Verificação nativa não concluída: {error}')
            return 1
        if result.returncode:
            print(result.stderr)
            return 1
        if save.read_bytes() != original or 'Preferências não carregadas' in result.stderr:
            print('O teste nativo acessou ou alterou preferências indevidamente.')
            return 1
    print('Percurso SDL passou: tela inicial, menu, diálogo progressivo e opções; '
          'escala/paleta e preferências isoladas verificadas.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
