import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from rom_inspector import inspect, LOGO


class InspectorTests(unittest.TestCase):
    def inspect_bytes(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.dat'
            path.write_bytes(data)
            result = inspect(path)
            self.assertEqual(path.read_bytes(), data)
            return result

    def cartridge(self):
        data = bytearray(32768)
        data[0x104:0x134] = LOGO
        checksum = 0
        for byte in data[0x134:0x14d]:
            checksum = (checksum - byte - 1) & 255
        data[0x14d] = checksum
        data[0x14e:0x150] = (sum(data) & 65535).to_bytes(2, 'big')
        return data

    def test_synthetic_valid_header_and_read_only(self):
        self.assertTrue(self.inspect_bytes(self.cartridge())['valid'])

    def test_short_patch_is_rejected(self):
        self.assertFalse(self.inspect_bytes(b'BPS1')['valid'])

    def test_truncation_is_rejected(self):
        self.assertFalse(self.inspect_bytes(self.cartridge()[:-1])['valid'])

    def test_corruption_is_rejected(self):
        data = self.cartridge()
        data[0x200] ^= 1
        self.assertFalse(self.inspect_bytes(data)['global_checksum_valid'])

    def test_logo_is_required(self):
        data = self.cartridge()
        data[0x104] ^= 1
        self.assertFalse(self.inspect_bytes(data)['logo_valid'])


if __name__ == '__main__':
    unittest.main()
