"""Nonstream entrypoint; shares all safety checks with compile-one.py."""
import importlib.util
from pathlib import Path


def main(argv=None, *, client_factory=None):
    path = Path(__file__).resolve().parent.parent / '20260929T083140Z-p2-resume/compile-one.py'
    spec = importlib.util.spec_from_file_location('p2_compile_engine', path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main(argv, stream=False, client_factory=client_factory)


if __name__ == '__main__':
    raise SystemExit(main())
