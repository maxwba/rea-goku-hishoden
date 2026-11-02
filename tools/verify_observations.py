"""Reproduz checkpoints humanos sem exibir pixels, conteúdo da ROM ou memória."""
import argparse
import json
from pathlib import Path

from reference_probe import ROOT, Probe, private_output, scenario
from reference_viewer import CATEGORIES, find_rom
from rom_inspector import inspect

IDENTITY = ('schema', 'sameboy', 'model', 'random_seed', 'boot_sha256',
            'library_sha256', 'pixel_encoding', 'byteorder')


def complete_records(path):
    # O observador pode continuar aberto. Uma última linha ainda em escrita não é usada.
    data = private_output(path).read_text()
    if not data.endswith('\n'):
        data = data.rsplit('\n', 1)[0] + '\n' if '\n' in data else ''
    return [json.loads(line) for line in data.splitlines()]


def replay_checkpoints(probe, plan, notes):
    plan = scenario(plan)
    checkpoints = {note['frame']: note for note in notes}
    if any(type(frame) is not int or not 0 <= frame < plan['frames'] for frame in checkpoints):
        raise ValueError('Checkpoint fora do roteiro.')
    if any(note.get('category') not in CATEGORIES for note in notes):
        raise ValueError('Classificação inválida.')
    events = {event['frame']: event['keys'] for event in plan['events']}
    keys = []
    result = []
    for frame in range(plan['frames']):
        keys = events.get(frame, keys)
        snapshot = probe.frame(keys)
        if frame in checkpoints:
            note = checkpoints[frame]
            if any(note.get(key) != value for key, value in snapshot.items()):
                raise ValueError(f'Checkpoint não reproduzido no frame {frame}.')
            result.append({'frame': frame, 'category': note['category'], 'verified': True})
    return result


def verify_journal(path, rom):
    rows = complete_records(path)
    if not rows or rows[0].get('tool') != 'local-reference-viewer':
        return []
    metadata = rows[0]
    rom_hash = inspect(rom)['sha256']
    if metadata.get('rom_sha256') != rom_hash:
        raise ValueError('Referência diferente da sessão observada.')
    epochs = sorted({row['epoch'] for row in rows if row.get('kind') == 'human_observation'})
    reports = []
    for epoch in epochs:
        # Uma remarcação do mesmo checkpoint substitui a classificação anterior.
        selected = {row['frame']: row for row in rows
                    if row.get('kind') == 'human_observation' and row['epoch'] == epoch}
        notes = list(selected.values())
        end = max(selected) + 1
        inputs = [{'frame': row['frame'], 'keys': row['keys']} for row in rows
                  if row.get('kind') == 'input' and row['epoch'] == epoch and row['frame'] < end]
        plan = scenario({'name': f'checkpoint-epoch-{epoch}', 'frames': end, 'events': inputs})
        probe = Probe(rom)
        try:
            current = probe.metadata(plan)
            if any(metadata.get(key) != current.get(key) for key in IDENTITY):
                raise ValueError('Backend ou boot diferente da sessão observada.')
            reports.extend({'session': path.name, 'epoch': epoch, **item}
                           for item in replay_checkpoints(probe, plan, notes))
        finally:
            probe.close()
    if inspect(rom)['sha256'] != rom_hash:
        raise RuntimeError('Hash da referência alterado durante a verificação.')
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path)
    parser.add_argument('--journal', type=Path)
    args = parser.parse_args()
    try:
        rom = find_rom(args.rom)
        paths = [args.journal] if args.journal else sorted((ROOT / 'private-analysis').glob('observation-*.jsonl'))
        reports = [report for path in paths for report in verify_journal(path, rom)]
        print(json.dumps({'verified_checkpoints': reports}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        parser.exit(1, f'Verificação não concluída: {error}\n')


if __name__ == '__main__':
    main()
