"""Visualização privada de referência, exclusivamente em loopback, sem salvar imagens.

Nunca abrir este visualizador com ferramentas de captura do agente. Ele existe para
observação humana local, separado do runtime Rust. Sem dependências web externas.
"""
import argparse
import base64
import json
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from reference_probe import ROOT, Probe, private_output, scenario
from rom_inspector import inspect

CATEGORIES = {'title', 'menu', 'dialogue', 'world', 'battle', 'other'}
PRESETS = {
    'before-start': [(360, [])],
    'after-start': [(360, []), (12, ['start']), (228, [])],
    'after-down': [(360, []), (12, ['start']), (228, []), (12, ['down']), (48, [])],
    'after-a': [(360, []), (12, ['start']), (228, []), (12, ['a']), (48, [])],
}
RESOURCES = {'/': ('index.html', 'text/html; charset=utf-8'),
             '/viewer.js': ('viewer.js', 'text/javascript; charset=utf-8'),
             '/viewer.css': ('viewer.css', 'text/css; charset=utf-8')}


def find_rom(explicit=None):
    if explicit:
        path = Path(explicit).resolve()
    else:
        candidates = [p for p in ROOT.iterdir() if p.is_file()
                      and p.suffix.lower() in {'.gb', '.gbc', '.rom', '.bin', '.iso'}]
        if len(candidates) != 1:
            raise ValueError('Forneça --rom: é necessário identificar uma única referência local.')
        path = candidates[0]
    if not inspect(path)['valid']:
        raise ValueError('Referência rejeitada pelo inspetor Game Boy.')
    return path


def validate_step(value):
    if not isinstance(value, dict) or set(value) != {'frames', 'keys'}:
        raise ValueError('Passo inválido.')
    plan = scenario({'name': 'viewer-input', 'frames': value['frames'],
                     'events': [{'frame': 0, 'keys': value['keys']}]})
    if plan['frames'] > 60:
        raise ValueError('Avance no máximo 60 frames por requisição.')
    return plan['frames'], plan['events'][0]['keys']


class Session:
    def __init__(self, rom):
        self.rom = rom
        self.rom_hash = inspect(rom)['sha256']
        self.probe = Probe(rom)
        self.frame = 0
        self.epoch = 0
        self.keys = []
        self.events = []
        self.last = None
        self.exported = None
        stamp = f'{time.time_ns()}-{secrets.token_hex(4)}'
        self.output = private_output(ROOT / 'private-analysis' / f'observation-{stamp}.jsonl')
        self.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.stream = self.output.open('x')
            self.record({'kind': 'metadata', 'tool': 'local-reference-viewer',
                         'rom_sha256': self.rom_hash,
                         **self.probe.metadata({'name': 'interactive', 'frames': 0, 'events': []})})
        except Exception:
            self.probe.close()
            raise

    def record(self, value):
        self.stream.write(json.dumps(value, ensure_ascii=False) + '\n')
        self.stream.flush()

    def export(self):
        if not self.frame or self.exported == self.frame:
            return
        plan = scenario({'name': f'observation-epoch-{self.epoch}',
                         'frames': self.frame, 'events': self.events})
        target = self.output.with_name(f'{self.output.stem}-epoch-{self.epoch}-{self.frame}.scenario.json')
        with private_output(target, suffix='.json').open('x') as stream:
            json.dump(plan, stream, ensure_ascii=False, indent=2)
        self.exported = self.frame
        self.record({'kind': 'scenario_export', 'epoch': self.epoch,
                     'frame': self.frame, 'file': target.name})

    def step(self, value):
        count, keys = validate_step(value)
        if self.frame + count > 36000:
            raise ValueError('Limite de sessão atingido. Reinicie para continuar.')
        if keys != self.keys or not self.events:
            self.events.append({'frame': self.frame, 'keys': keys})
            self.keys = keys
            self.record({'kind': 'input', 'epoch': self.epoch, 'frame': self.frame, 'keys': keys})
        for _ in range(count):
            self.last = self.probe.frame(keys)
            self.frame += 1
        # Nenhum pixel é gravado em disco: somente enviado à página no próprio computador.
        pixels = bytearray()
        for pixel in self.probe.pixels:
            pixels.extend(((pixel >> 16) & 255, (pixel >> 8) & 255, pixel & 255, 255))
        return {'frame': self.frame, 'epoch': self.epoch,
                'rgba': base64.b64encode(pixels).decode('ascii')}

    def label(self, value):
        if not isinstance(value, dict) or set(value) != {'category'} or not isinstance(value['category'], str) or value['category'] not in CATEGORIES:
            raise ValueError('Classificação inválida.')
        if self.last is None:
            raise ValueError('Avance ao menos um frame antes de classificar.')
        self.record({'kind': 'human_observation', 'epoch': self.epoch,
                     'frame': self.frame - 1, 'category': value['category'], **self.last})
        self.export()
        return {'saved': True, 'frame': self.frame - 1}

    def replay(self, value):
        if (not isinstance(value, dict) or set(value) != {'preset'}
                or not isinstance(value['preset'], str) or value['preset'] not in PRESETS):
            raise ValueError('Ponto de observação inválido.')
        self.reset()
        result = None
        for duration, keys in PRESETS[value['preset']]:
            while duration:
                count = min(duration, 60)
                result = self.step({'frames': count, 'keys': keys})
                duration -= count
        self.record({'kind': 'preset', 'epoch': self.epoch, 'name': value['preset'],
                     'frame': self.frame - 1})
        return result

    def reset(self):
        self.export()
        self.probe.close()
        self.probe = Probe(self.rom)
        self.frame = 0
        self.epoch += 1
        self.events = []
        self.keys = []
        self.last = None
        self.exported = None
        self.record({'kind': 'reset', 'epoch': self.epoch})
        return {'reset': True}

    def close(self):
        try:
            self.export()
            self.record({'kind': 'end', 'epoch': self.epoch, 'frames': self.frame,
                         'rom_unchanged': inspect(self.rom)['sha256'] == self.rom_hash})
        finally:
            self.probe.close()
            self.stream.close()


def handler_for(session, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Não registra corpos, URL com segredo nem conteúdo do cartucho.

        def reply(self, status, body, content_type='application/json; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def json_reply(self, status, value):
            self.reply(status, json.dumps(value, ensure_ascii=False).encode())

        def local_request(self):
            return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

        def do_GET(self):
            if not self.local_request():
                self.json_reply(403, {'error': 'Origem não permitida.'})
                return
            resource = RESOURCES.get(urlsplit(self.path).path)
            if not resource:
                self.json_reply(404, {'error': 'Recurso inexistente.'})
                return
            name, kind = resource
            self.reply(200, (ROOT / 'tools/reference-ui' / name).read_bytes(), kind)

        def do_POST(self):
            expected_origin = f'http://127.0.0.1:{self.server.server_port}'
            supplied = self.headers.get('X-Reference-Token', '')
            if (not self.local_request() or not secrets.compare_digest(supplied, token)
                    or self.headers.get('Origin', expected_origin) != expected_origin):
                self.json_reply(403, {'error': 'Sessão local não autorizada.'})
                return
            try:
                if self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('Envie JSON.')
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 2048:
                    raise ValueError('Requisição inválida.')
                value = json.loads(self.rfile.read(length))
                if self.path == '/api/step':
                    result = session.step(value)
                elif self.path == '/api/replay':
                    result = session.replay(value)
                elif self.path == '/api/label':
                    result = session.label(value)
                elif self.path == '/api/reset' and value == {}:
                    result = session.reset()
                else:
                    raise ValueError('Ação inválida.')
                self.json_reply(200, result)
            except (ValueError, TypeError, KeyError) as error:
                self.json_reply(400, {'error': str(error)})
            except (OSError, RuntimeError):
                self.json_reply(500, {'error': 'Falha local; encerre pelo Terminal e preserve o diagnóstico.'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path)
    parser.add_argument('--open', action='store_true', help='Abre no navegador padrão do computador.')
    args = parser.parse_args()
    session = None
    try:
        session = Session(find_rom(args.rom))
        token = secrets.token_urlsafe(32)
        with HTTPServer(('127.0.0.1', 0), handler_for(session, token)) as server:
            url = f'http://127.0.0.1:{server.server_port}/#{token}'
            print('Visualizador de referência local. Encerre com Ctrl+C no Terminal.', flush=True)
            print('Use o navegador deste computador; não faça capturas nem envie telas ao agente.', flush=True)
            print(f'Interface local: http://127.0.0.1:{server.server_port}/', flush=True)
            if not args.open:
                print('Use --open ou Analisar.command para abrir uma sessão autorizada no navegador.', flush=True)
            if args.open:
                webbrowser.open(url)
            server.serve_forever()
    except KeyboardInterrupt:
        print('\nColeta local encerrada.')
    except (OSError, ValueError, RuntimeError, AttributeError) as error:
        parser.exit(1, f'Visualizador não iniciado: {error}\n')
    finally:
        if session:
            session.close()


if __name__ == '__main__':
    main()
