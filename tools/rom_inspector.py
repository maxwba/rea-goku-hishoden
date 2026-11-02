"""Inspeção local, somente leitura; não extrai recursos nem imprime bytes da ROM."""
import argparse
import hashlib
import json
from pathlib import Path

LOGO = bytes.fromhex(
    'CE ED 66 66 CC 0D 00 0B 03 73 00 83 00 0C 00 0D '
    '00 08 11 1F 88 89 00 0E DC CC 6E E6 DD DD D9 99 '
    'BB BB 67 63 6E 0E EC CC DD DC 99 9F BB B9 33 3E'
)
MAPPERS = {0: 'ROM ONLY', 1: 'MBC1', 2: 'MBC1+RAM', 3: 'MBC1+RAM+BATTERY',
           5: 'MBC2', 6: 'MBC2+BATTERY', 0x0f: 'MBC3+TIMER+BATTERY',
           0x10: 'MBC3+TIMER+RAM+BATTERY', 0x11: 'MBC3', 0x12: 'MBC3+RAM',
           0x13: 'MBC3+RAM+BATTERY', 0x19: 'MBC5', 0x1a: 'MBC5+RAM',
           0x1b: 'MBC5+RAM+BATTERY', 0x1c: 'MBC5+RUMBLE',
           0x1d: 'MBC5+RUMBLE+RAM', 0x1e: 'MBC5+RUMBLE+RAM+BATTERY'}
ROM_SIZES = {**{i: 32768 << i for i in range(9)},
             0x52: 72 * 16384, 0x53: 80 * 16384, 0x54: 96 * 16384}
RAM_SIZES = {0: 0, 1: 2048, 2: 8192, 3: 32768, 4: 131072, 5: 65536}


def inspect(path):
    data = Path(path).read_bytes()
    result = {'size_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
              'valid': False, 'issues': []}
    if len(data) < 0x150:
        result['issues'].append('Arquivo menor que o header Game Boy completo.')
        return result
    header_checksum = 0
    for byte in data[0x134:0x14d]:
        header_checksum = (header_checksum - byte - 1) & 255
    cgb = data[0x143]
    title_end = 0x13f if cgb in (0x80, 0xc0) else 0x144
    result.update({
        'title': data[0x134:title_end].split(b'\0')[0].decode('ascii', errors='replace'),
        'cgb_flag': cgb, 'sgb_flag': data[0x146],
        'cartridge_type': data[0x147],
        'mapper': MAPPERS.get(data[0x147], 'Não catalogado pelo inspetor'),
        'declared_rom_bytes': ROM_SIZES.get(data[0x148]),
        'declared_ram_bytes': RAM_SIZES.get(data[0x149]),
        'mbc2_internal_ram': '512 x 4 bits' if data[0x147] in (5, 6) else None,
        'logo_valid': data[0x104:0x134] == LOGO,
        'header_checksum_valid': header_checksum == data[0x14d],
        'global_checksum_valid': ((sum(data) - data[0x14e] - data[0x14f]) & 65535)
                                 == int.from_bytes(data[0x14e:0x150], 'big'),
    })
    for key in ('logo_valid', 'header_checksum_valid', 'global_checksum_valid'):
        if not result[key]:
            result['issues'].append(key + ': falhou')
    if result['declared_rom_bytes'] != len(data):
        result['issues'].append('Tamanho ROM divergente ou código desconhecido.')
    if result['declared_ram_bytes'] is None:
        result['issues'].append('Código de tamanho RAM desconhecido.')
    if cgb not in (0, 0x80, 0xc0):
        result['issues'].append('Flag CGB não reconhecida; requer revisão.')
    result['valid'] = not result['issues']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.rom)
    except OSError:
        parser.exit(2, 'Não foi possível ler o arquivo local.\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
