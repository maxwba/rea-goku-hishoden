"""Resume somente as classificações humanas locais, sem pixels, memória ou diálogos."""
import argparse
import json
from pathlib import Path

from reference_probe import ROOT, private_output
from reference_viewer import CATEGORIES


def summarize_records(records):
    if not records or records[0].get('tool') != 'local-reference-viewer':
        return None
    labels = []
    for record in records:
        if record.get('kind') != 'human_observation':
            continue
        if record.get('category') not in CATEGORIES:
            raise ValueError('Classificação humana não reconhecida.')
        if type(record.get('frame')) is not int or record['frame'] < 0:
            raise ValueError('Quadro da observação inválido.')
        if type(record.get('epoch')) is not int or record['epoch'] < 0:
            raise ValueError('Sessão da observação inválida.')
        labels.append({key: record[key] for key in ('epoch', 'frame', 'category')})
    return labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='*', type=Path)
    args = parser.parse_args()
    paths = args.files or sorted((ROOT / 'private-analysis').glob('observation-*.jsonl'))
    result = {'sessions': 0, 'observations': []}
    try:
        for path in paths:
            records = [json.loads(line) for line in private_output(path).read_text().splitlines()]
            labels = summarize_records(records)
            if labels is not None:
                result['sessions'] += 1
                result['observations'].extend({'session': path.name, **label} for label in labels)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Não foi possível resumir as observações: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
