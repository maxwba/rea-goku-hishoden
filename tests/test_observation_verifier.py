import sys
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from verify_observations import replay_checkpoints, complete_records


class FakeProbe:
    def __init__(self):
        self.counter = 0
        self.inputs = []

    def frame(self, keys):
        self.inputs.append(list(keys))
        self.counter += 1
        return {'pc': self.counter, 'frame_sha256': 'synthetic'}


class ObservationVerifierTests(unittest.TestCase):
    def test_replays_held_keys_before_comparing_checkpoints(self):
        probe = FakeProbe()
        plan = {'name': 'synthetic', 'frames': 4,
                'events': [{'frame': 1, 'keys': ['start']}, {'frame': 3, 'keys': []}]}
        notes = [{'frame': 2, 'category': 'menu', 'pc': 3, 'frame_sha256': 'synthetic'}]
        self.assertEqual(replay_checkpoints(probe, plan, notes),
                         [{'frame': 2, 'category': 'menu', 'verified': True}])
        self.assertEqual(probe.inputs, [[], ['start'], ['start'], []])

    def test_wrong_state_is_rejected_instead_of_reclassified(self):
        plan = {'name': 'synthetic', 'frames': 1, 'events': []}
        note = {'frame': 0, 'category': 'title', 'pc': 99, 'frame_sha256': 'synthetic'}
        with self.assertRaises(ValueError):
            replay_checkpoints(FakeProbe(), plan, [note])

    def test_checkpoint_beyond_the_plan_is_rejected(self):
        with self.assertRaises(ValueError):
            replay_checkpoints(FakeProbe(), {'name': 'synthetic', 'frames': 1, 'events': []},
                               [{'frame': 1, 'category': 'menu'}])


    def test_live_journal_uses_only_complete_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.jsonl'
            path.write_text('{"kind":"metadata"}\n{"kind":"unfinished')
            with patch('verify_observations.private_output', return_value=path):
                self.assertEqual(complete_records(path), [{'kind': 'metadata'}])
            path.write_text('{"invalid":}\n')
            with patch('verify_observations.private_output', return_value=path):
                with self.assertRaises(ValueError):
                    complete_records(path)
