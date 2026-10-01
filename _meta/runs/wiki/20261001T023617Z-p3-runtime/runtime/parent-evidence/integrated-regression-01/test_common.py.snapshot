"""P3 common helper tracer: no live source reads or writes."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).parent
sys.dont_write_bytecode = True

class CommonTests(unittest.TestCase):
    def test_safe_helpers_and_synthetic_root_boundary(self):
        path = HERE / 'p3_common.py'
        self.assertTrue(path.exists(), 'P3 common adapter missing')
        spec = importlib.util.spec_from_file_location('p3_common_under_test', path)
        assert spec is not None and spec.loader is not None
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual(m.decode(m.encoded({'한글': None})), {'한글': None})
        self.assertEqual(m.sha(b'abc'), m.helper('publish').sha(b'abc'))
        with tempfile.TemporaryDirectory(prefix='synthetic-', dir=HERE) as folder:
            self.assertEqual(m.synthetic_root(Path(folder)), Path(folder))
            fs = m.helper('publish').Files(folder)
            m.ensure_dirs(fs, 'one/two')
            self.assertTrue((Path(folder)/'one/two').is_dir())
            with self.assertRaises(ValueError):
                m.ensure_dirs(fs, '../escape')
        with self.assertRaises(ValueError):
            m.synthetic_root(m.ROOT)
        with self.assertRaises(TimeoutError):
            m.check_deadline(1.0, lambda: 1.0)
        m.check_deadline(2.0, lambda: 1.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
