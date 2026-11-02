import json
import sys
import threading
import unittest
from http.client import HTTPConnection
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from reference_viewer import handler_for, validate_step, Session


class FakeSession:
    def step(self, value):
        count, keys = validate_step(value)
        return {'frame': count, 'keys': keys, 'rgba': 'synthetic'}

    def label(self, value):
        return {'saved': True}

    def reset(self):
        return {'reset': True}


class ViewerHTTPTests(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(('127.0.0.1', 0), handler_for(FakeSession(), 'synthetic-token'))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        request_headers = {'Host': f'127.0.0.1:{self.server.server_port}',
                           'Content-Type': 'application/json',
                           'X-Reference-Token': 'synthetic-token'}
        request_headers.update(headers or {})
        connection.request(method, path, body=json.dumps(body) if body is not None else None,
                           headers=request_headers)
        response = connection.getresponse()
        data = response.read()
        result = response.status, dict(response.getheaders()), data
        connection.close()
        return result

    def test_step_only_returns_data_to_authorized_local_request(self):
        status, headers, data = self.request('POST', '/api/step', {'frames': 2, 'keys': ['a']})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)['frame'], 2)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertNotIn('Access-Control-Allow-Origin', headers)

    def test_foreign_origin_token_and_host_are_rejected(self):
        for headers in [{'Origin': 'https://example.com'}, {'X-Reference-Token': 'wrong'},
                        {'Host': 'example.com'}]:
            with self.subTest(headers=headers):
                status, _, _ = self.request('POST', '/api/step', {'frames': 1, 'keys': []}, headers)
                self.assertEqual(status, 403)

    def test_file_system_is_not_served(self):
        for path in ['/private-analysis/file.jsonl', '/../../CODEX_SETUP.md', '/api/step']:
            status, _, _ = self.request('GET', path)
            self.assertEqual(status, 404)
        status, _, _ = self.request('GET', '/', headers={'Host': 'example.com'})
        self.assertEqual(status, 403)

    def test_invalid_steps_are_rejected(self):
        for payload in [{'frames': 61, 'keys': []}, {'frames': True, 'keys': []},
                        {'frames': 1, 'keys': ['left', 'right']}, {'frames': 1}, []]:
            status, _, _ = self.request('POST', '/api/step', payload)
            self.assertEqual(status, 400)

    def test_ui_has_no_remote_resource_and_has_no_cache(self):
        status, headers, body = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertNotIn(b'https://', body)
        self.assertIn('frame-ancestors', headers['Content-Security-Policy'])
        self.assertEqual(headers['Cache-Control'], 'no-store')


class SessionValidationTests(unittest.TestCase):
    def test_label_requires_observed_frame_and_known_category(self):
        session = Session.__new__(Session)
        session.last = None
        for value in [{'category': 'menu'}, {'category': {}}, {'category': 'original-dialogue'}]:
            with self.assertRaises(ValueError):
                session.label(value)

    def test_step_makes_complete_input_events_and_never_records_pixels(self):
        class Probe:
            pixels = [0x00112233] * (160 * 144)
            def frame(self, keys):
                return {'frame_sha256': 'synthetic', 'memory': {'wram': 'synthetic'}}
        session = Session.__new__(Session)
        session.probe = Probe()
        session.frame = 0
        session.epoch = 0
        session.events = []
        session.keys = []
        session.last = None
        with patch.object(session, 'record') as record:
            result = session.step({'frames': 2, 'keys': ['start']})
            session.step({'frames': 1, 'keys': []})
            self.assertEqual(session.events, [{'frame': 0, 'keys': ['start']}, {'frame': 2, 'keys': []}])
            self.assertEqual(result['frame'], 2)
            self.assertTrue(result['rgba'])
            for call in record.call_args_list:
                self.assertNotIn('rgba', call.args[0])
                self.assertNotIn('pixels', call.args[0])


class HumanObservationTests(unittest.TestCase):
    def test_summary_exposes_only_human_categories_and_frame_numbers(self):
        from summarize_observations import summarize_records
        records = [{'tool': 'local-reference-viewer'},
                   {'kind': 'human_observation', 'epoch': 1, 'frame': 42,
                    'category': 'menu', 'frame_sha256': 'synthetic',
                    'memory': {'wram': 'synthetic'}, 'pc': 123}]
        self.assertEqual(summarize_records(records), [{'epoch': 1, 'frame': 42, 'category': 'menu'}])
        records[1]['category'] = 'unknown'
        with self.assertRaises(ValueError):
            summarize_records(records)

    def test_non_viewer_trace_is_not_classified(self):
        from summarize_observations import summarize_records
        self.assertIsNone(summarize_records([{'metadata': {'schema': 2}}]))


class PresetTests(unittest.TestCase):
    def test_preset_reconstructs_exact_start_schedule(self):
        class Probe:
            pixels = [0] * (160 * 144)
            def frame(self, keys):
                return {'frame_sha256': 'synthetic'}
        session = Session.__new__(Session)
        session.probe = Probe()
        session.epoch = 0
        def reset():
            session.frame = 0
            session.keys = []
            session.events = []
            session.last = None
        with patch.object(session, 'reset', side_effect=reset), patch.object(session, 'record'):
            result = session.replay({'preset': 'after-start'})
            self.assertEqual(result['frame'], 600)
            self.assertEqual(session.events, [{'frame': 0, 'keys': []},
                                              {'frame': 360, 'keys': ['start']},
                                              {'frame': 372, 'keys': []}])
            for value in [{'preset': '../private'}, {'preset': []}, {}]:
                with self.assertRaises(ValueError):
                    session.replay(value)
