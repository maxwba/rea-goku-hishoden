"""Compara coletas privadas sem exibir imagens, memória ou hashes dos quadros."""
import argparse
import json
from pathlib import Path

from reference_probe import private_output


def load(path):
    with private_output(path).open() as stream:
        metadata = json.loads(next(stream))['metadata']
        frames = [json.loads(line) for line in stream]
    if len(frames) != metadata['scenario']['frames']:
        raise ValueError('Coleta incompleta.')
    if any(value.get('frame') != index for index, value in enumerate(frames)):
        raise ValueError('Sequência de frames inválida.')
    return metadata, frames


def compare(left, right):
    lm, lf = left
    rm, rf = right
    for key in ('schema', 'sameboy', 'model', 'random_seed', 'rom_sha256', 'boot_sha256',
                'library_sha256', 'pixel_encoding', 'byteorder'):
        if key not in lm or key not in rm:
            raise ValueError('Identidade da coleta incompleta: ' + key)
        if lm[key] != rm[key]:
            raise ValueError('Coletas incompatíveis: ' + key)
    if lm['schema'] not in (1, 2):
        raise ValueError('Schema de coleta não suportado.')
    if len(lf) != len(rf):
        raise ValueError('Cenários precisam ter a mesma duração.')
    differences = [a['frame'] for a, b in zip(lf, rf)
                   if a['frame_sha256'] != b['frame_sha256']]
    if lm['schema'] == 2 and any(set(frame.get('memory', {})) != {'wram', 'vram', 'oam', 'tilemaps'} for frame in lf + rf):
        raise ValueError('Fingerprints de memória incompletos.')
    memory_changes = {}
    for region in ('wram', 'vram', 'oam', 'tilemaps'):
        if all(region in frame.get('memory', {}) for frame in lf + rf):
            changed = [a['frame'] for a, b in zip(lf, rf)
                       if a['memory'][region] != b['memory'][region]]
            memory_changes[region] = {'different_frames': len(changed),
                                      'first_difference': changed[0] if changed else None}
    return {'memory_differences': memory_changes, 'frames_compared': len(lf), 'identical_trace': lf == rf,
            'different_visual_frames': len(differences),
            'first_visual_difference': differences[0] if differences else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('left', type=Path)
    parser.add_argument('right', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(compare(load(args.left), load(args.right))))
    except (OSError, ValueError, KeyError, StopIteration) as error:
        parser.exit(1, f'Comparação não concluída: {error}\n')


if __name__ == '__main__':
    main()
