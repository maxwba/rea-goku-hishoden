"""Coleta local SameBoy: somente hashes/metadados, nunca imagens ou bytes da ROM.

SameBoy é ferramenta separada de engenharia reversa, sem vínculo com o binário Rust.
A saída só pode ser gravada dentro de private-analysis/.
"""
import argparse
import ctypes as c
import hashlib
import json
import sys
from pathlib import Path

from rom_inspector import inspect

ROOT = Path(__file__).resolve().parents[1]
SAMEBOY = ROOT / '.tools/sameboy/SameBoy-1.0.4'
KEYS = {'right': 0, 'left': 1, 'up': 2, 'down': 3,
        'a': 4, 'b': 5, 'select': 6, 'start': 7}
LOG = c.CFUNCTYPE(None, c.c_void_p, c.c_char_p, c.c_uint)
RGB = c.CFUNCTYPE(c.c_uint32, c.c_void_p, c.c_uint8, c.c_uint8, c.c_uint8)


def scenario(value):
    if not isinstance(value, dict) or not isinstance(value.get('name'), str):
        raise ValueError('Cenário precisa de um nome.')
    frames = value.get('frames')
    if type(frames) is not int or not 1 <= frames <= 36000:
        raise ValueError('Quantidade de frames precisa estar entre 1 e 36000.')
    events = value.get('events')
    if not isinstance(events, list):
        raise ValueError('Cenário precisa de uma lista de eventos.')
    previous = -1
    for event in events:
        if not isinstance(event, dict):
            raise ValueError('Evento precisa ser um objeto.')
        frame = event.get('frame')
        if type(frame) is not int or not previous < frame < frames:
            raise ValueError('Frames devem ser únicos, crescentes e dentro do cenário.')
        keys = event.get('keys')
        if not isinstance(keys, list) or any(not isinstance(key, str) or key not in KEYS for key in keys):
            raise ValueError('Botão não reconhecido.')
        if len(set(keys)) != len(keys):
            raise ValueError('Botões duplicados no evento.')
        if {'left', 'right'} <= set(keys) or {'up', 'down'} <= set(keys):
            raise ValueError('Direções opostas não são permitidas.')
        previous = frame
    return value


def private_output(path, suffix=".jsonl"):
    resolved = Path(path).resolve()
    private = (ROOT / 'private-analysis').resolve()
    if private not in resolved.parents:
        raise ValueError('Saída precisa estar dentro de private-analysis/.')
    if suffix not in {'.jsonl', '.json'} or resolved.suffix != suffix:
        raise ValueError('Extensão de saída privada inválida.')
    return resolved


def bind(library, name, arguments, result=None):
    function = getattr(library, name)
    function.argtypes = arguments
    function.restype = result
    return function


class Probe:
    def __init__(self, rom):
        self.lib = c.CDLL(str(SAMEBOY / 'build/lib/libsameboy.dylib'))
        ptr = c.c_void_p
        api = self.lib
        bind(api, 'GB_alloc', [], ptr)
        bind(api, 'GB_init', [ptr, c.c_int], ptr)
        bind(api, 'GB_dealloc', [ptr])
        bind(api, 'GB_load_rom', [ptr, c.c_char_p], c.c_int)
        bind(api, 'GB_load_boot_rom', [ptr, c.c_char_p], c.c_int)
        bind(api, 'GB_set_log_callback', [ptr, LOG])
        bind(api, 'GB_set_rgb_encode_callback', [ptr, RGB])
        bind(api, 'GB_set_pixels_output', [ptr, c.POINTER(c.c_uint32)])
        bind(api, 'GB_debugger_set_disabled', [ptr, c.c_bool])
        bind(api, 'GB_random_seed', [c.c_uint64])
        bind(api, 'GB_set_key_mask', [ptr, c.c_int])
        bind(api, 'GB_run_frame', [ptr], c.c_uint64)
        bind(api, 'GB_get_registers', [ptr], c.POINTER(c.c_uint16))
        bind(api, 'GB_get_direct_access', [ptr, c.c_int,
             c.POINTER(c.c_size_t), c.POINTER(c.c_uint16)], ptr)
        bind(api, 'GB_get_screen_width', [ptr], c.c_uint)
        bind(api, 'GB_get_screen_height', [ptr], c.c_uint)
        # Mantém referências aos callbacks enquanto o core os usa.
        self.log = LOG(lambda *_: None)
        self.rgb = RGB(lambda _gb, r, g, b: (r << 16) | (g << 8) | b)
        api.GB_random_seed(1)
        self.gb = api.GB_init(api.GB_alloc(), 0x002)  # GB_MODEL_DMG_B
        if not self.gb:
            raise RuntimeError('Não foi possível alocar o core SameBoy.')
        try:
            api.GB_set_log_callback(self.gb, self.log)
            api.GB_debugger_set_disabled(self.gb, True)
            if api.GB_load_rom(self.gb, str(rom).encode()):
                raise RuntimeError('SameBoy não carregou a ROM local.')
            boot = SAMEBOY / 'build/bin/BootROMs/dmg_boot.bin'
            if api.GB_load_boot_rom(self.gb, str(boot).encode()):
                raise RuntimeError('Boot ROM livre do SameBoy indisponível.')
            if (api.GB_get_screen_width(self.gb), api.GB_get_screen_height(self.gb)) != (160, 144):
                raise RuntimeError('Dimensões do modelo DMG inesperadas.')
            self.pixels = (c.c_uint32 * (160 * 144))()
            api.GB_set_rgb_encode_callback(self.gb, self.rgb)
            api.GB_set_pixels_output(self.gb, self.pixels)
        except Exception:
            self.close()
            raise

    def close(self):
        if self.gb:
            self.lib.GB_dealloc(self.gb)
            self.gb = None

    def memory_fingerprints(self):
        result = {}
        # Enum GB_direct_access_t verificado nos headers SameBoy 1.0.4.
        # Não há leitura de ROM nem serialização dos bytes dessas regiões.
        for name, access in [('wram', 1), ('vram', 3), ('oam', 7)]:
            size = c.c_size_t()
            bank = c.c_uint16()
            pointer = self.lib.GB_get_direct_access(self.gb, access, c.byref(size), c.byref(bank))
            if not pointer or size.value > 65536:
                raise RuntimeError('Região de memória inesperada no modelo DMG.')
            data = c.string_at(pointer, size.value)
            result[name] = hashlib.sha256(data).hexdigest()
            if name == 'vram':
                # Mapas de tiles da especificação DMG, separados dos dados de tiles.
                result['tilemaps'] = hashlib.sha256(data[0x1800:0x2000]).hexdigest()
        return result

    def metadata(self, plan):
        return {'schema': 2, 'sameboy': '1.0.4', 'model': 'DMG-B',
                'library_sha256': hashlib.sha256((SAMEBOY / 'build/lib/libsameboy.dylib').read_bytes()).hexdigest(),
                'pixel_encoding': 'native-u32-0x00RRGGBB', 'byteorder': sys.byteorder,
                'random_seed': 1,
                'boot_sha256': hashlib.sha256((SAMEBOY / 'build/bin/BootROMs/dmg_boot.bin').read_bytes()).hexdigest(),
                'scenario': plan}

    def frame(self, keys):
        self.lib.GB_set_key_mask(self.gb, sum(1 << KEYS[key] for key in keys))
        elapsed = self.lib.GB_run_frame(self.gb)
        bank = c.c_uint16()
        size = c.c_size_t()
        self.lib.GB_get_direct_access(self.gb, 0, c.byref(size), c.byref(bank))
        # O ponteiro de ROM não é desreferenciado nem serializado.
        return {'frame_sha256': hashlib.sha256(bytes(self.pixels)).hexdigest(),
                'pc': self.lib.GB_get_registers(self.gb)[5],
                'rom_bank': bank.value, 'emulated_ns': elapsed,
                'memory': self.memory_fingerprints()}


def run(rom, plan, output):
    report = inspect(rom)
    if not report['valid']:
        raise ValueError('ROM rejeitada pelo inspetor; análise interrompida.')
    output = private_output(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    probe = Probe(rom)
    hashes = set()
    try:
        # Não substitui uma coleta anterior.
        with output.open('x') as stream:
            header = {**probe.metadata(plan), 'rom_sha256': report['sha256']}
            stream.write(json.dumps({'metadata': header}) + '\n')
            events = {event['frame']: event['keys'] for event in plan['events']}
            keys = []
            for frame in range(plan['frames']):
                keys = events.get(frame, keys)
                result = probe.frame(keys)
                hashes.add(result['frame_sha256'])
                stream.write(json.dumps({'frame': frame, 'keys': keys, **result}) + '\n')
    finally:
        probe.close()
    if inspect(rom)['sha256'] != report['sha256']:
        raise RuntimeError('Hash da referência mudou durante a coleta.')
    return {'frames': plan['frames'], 'distinct_frame_hashes': len(hashes),
            'rom_unchanged': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--scenario', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        plan = scenario(json.loads(args.scenario.read_text()))
        print(json.dumps(run(args.rom.resolve(), plan, args.output)))
    except (OSError, ValueError, RuntimeError, AttributeError) as error:
        parser.exit(1, f'Coleta não concluída: {error}\n')


if __name__ == '__main__':
    main()
