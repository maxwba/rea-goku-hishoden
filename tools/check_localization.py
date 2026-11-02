"""Valida catálogo e inventário sem acessar a ROM ou executar o aplicativo."""
import json
import re
from pathlib import Path


def validate(catalog, inventory, rust_source):
    errors = []
    keys = inventory.get('demo_keys')
    if not isinstance(keys, list) or not all(isinstance(key, str) for key in keys):
        return ['Inventário precisa conter uma lista demo_keys de strings.']
    if len(set(keys)) != len(keys):
        errors.append('Inventário contém chaves duplicadas.')
    if not isinstance(catalog, dict):
        return errors + ['Catálogo precisa ser um objeto JSON.']
    missing = set(keys) - set(catalog)
    extra = set(catalog) - set(keys)
    if missing:
        errors.append('Chaves ausentes: ' + ', '.join(sorted(missing)))
    if extra:
        errors.append('Chaves fora do inventário: ' + ', '.join(sorted(extra)))
    match = re.search(r'REQUIRED_KEYS:\s*\[&str;\s*(\d+)\]\s*=\s*\[(.*?)\];',
                      rust_source, re.DOTALL)
    if not match:
        errors.append('Declaração REQUIRED_KEYS não encontrada no Rust.')
    else:
        rust_keys = re.findall(r'"([^"]+)"', match.group(2))
        if len(rust_keys) != int(match.group(1)) or len(set(rust_keys)) != len(rust_keys):
            errors.append('Quantidade ou unicidade de REQUIRED_KEYS inválida.')
        if set(rust_keys) != set(keys):
            errors.append('Chaves do Rust divergem do inventário.')
    for key, value in catalog.items():
        if not isinstance(value, str) or not value.strip():
            errors.append(f'Texto ausente ou inválido: {key}')
            continue
        if any(character != '\n' and not (32 <= ord(character) <= 126
               or 160 <= ord(character) <= 255) for character in value):
            errors.append(f'Caractere fora das faixas da fonte demonstrativa: {key}')
    for key in ('options.scale', 'options.palette'):
        if key in catalog and isinstance(catalog[key], str) and catalog[key].count('{value}') != 1:
            errors.append(f'Marcador {{value}} inválido: {key}')
    return errors


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Chave JSON duplicada: {key}')
        result[key] = value
    return result


def main():
    root = Path(__file__).resolve().parents[1]
    try:
        catalog = json.loads((root / 'localization/pt-BR.json').read_text(),
                             object_pairs_hook=unique_object)
        inventory = json.loads((root / 'localization/inventory.json').read_text(),
                               object_pairs_hook=unique_object)
        rust_source = (root / 'src/localization/mod.rs').read_text()
        errors = validate(catalog, inventory, rust_source)
    except (OSError, ValueError) as error:
        print(f'Falha ao ler localização: {error}')
        return 1
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'{len(catalog)} chaves válidas, inventário e Rust consistentes; '
          'tradução do conteúdo original permanece pendente.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
