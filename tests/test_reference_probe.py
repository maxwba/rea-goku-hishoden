import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from reference_probe import private_output, scenario
from compare_probes import compare


class ReferenceProbeTests(unittest.TestCase):
    def test_valid_schedule(self):
        plan = {'name': 'synthetic', 'frames': 4,
                'events': [{'frame': 0, 'keys': ['start']}, {'frame': 2, 'keys': []}]}
        self.assertEqual(scenario(plan), plan)

    def test_invalid_frames_and_keys_are_rejected(self):
        for event in [{'frame': -1, 'keys': []}, {'frame': 4, 'keys': []},
                      {'frame': True, 'keys': []}, {'frame': 0, 'keys': ['invalid']},
                      {'frame': 0, 'keys': ['left', 'right']},
                      {'frame': 0, 'keys': ['a', 'a']}, {'frame': 0, 'keys': [{}]}]:
            with self.subTest(event=event), self.assertRaises(ValueError):
                scenario({'name': 'synthetic', 'frames': 4, 'events': [event]})

    def test_unsorted_and_duplicate_events_are_rejected(self):
        for frames in [[2, 1], [1, 1]]:
            with self.assertRaises(ValueError):
                scenario({'name': 'synthetic', 'frames': 4,
                          'events': [{'frame': frame, 'keys': []} for frame in frames]})

    def test_private_output_is_enforced(self):
        self.assertEqual(private_output('private-analysis/synthetic.jsonl').suffix, '.jsonl')
        for path in ['docs/trace.jsonl', 'private-analysis/../public.jsonl',
                     'private-analysis/trace.gb']:
            with self.assertRaises(ValueError):
                private_output(path)

    def test_comparison_identifies_first_divergence(self):
        metadata = {'schema': 1, 'sameboy': 'synthetic', 'model': 'synthetic',
                    'random_seed': 1, 'rom_sha256': 'synthetic', 'boot_sha256': 'synthetic',
                    'library_sha256': 'synthetic', 'pixel_encoding': 'synthetic', 'byteorder': 'little'}
        first = (metadata, [{'frame': 0, 'frame_sha256': 'a'},
                            {'frame': 1, 'frame_sha256': 'b'}])
        second = copy.deepcopy(first)
        self.assertTrue(compare(first, second)['identical_trace'])
        second[1][1]['frame_sha256'] = 'c'
        result = compare(first, second)
        self.assertEqual(result['first_visual_difference'], 1)
        self.assertEqual(result['different_visual_frames'], 1)
        second[0]['random_seed'] = 2
        with self.assertRaises(ValueError):
            compare(first, second)


    def test_comparison_rejects_missing_identity(self):
        with self.assertRaises(ValueError):
            compare(({}, []), ({}, []))

    def test_memory_fingerprints_distinguish_graphics_and_work_ram(self):
        metadata = {'schema': 2, 'sameboy': 'synthetic', 'model': 'synthetic',
                    'random_seed': 1, 'rom_sha256': 'synthetic', 'boot_sha256': 'synthetic',
                    'library_sha256': 'synthetic', 'pixel_encoding': 'synthetic', 'byteorder': 'little'}
        frames = [{'frame': 0, 'frame_sha256': 'same',
                   'memory': {'wram': 'initial', 'vram': 'same', 'oam': 'same', 'tilemaps': 'same'}}]
        changed = copy.deepcopy(frames)
        changed[0]['memory']['wram'] = 'changed'
        result = compare((metadata, frames), (metadata, changed))
        self.assertEqual(result['different_visual_frames'], 0)
        self.assertEqual(result['memory_differences']['wram']['first_difference'], 0)
        self.assertEqual(result['memory_differences']['tilemaps']['different_frames'], 0)
        del changed[0]['memory']['vram']
        with self.assertRaises(ValueError):
            compare((metadata, frames), (metadata, changed))
