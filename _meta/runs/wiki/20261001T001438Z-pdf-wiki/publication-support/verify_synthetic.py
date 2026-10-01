"""Run the synthetic suite and print machine-readable observed evidence; write nothing itself."""
import ast
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import types
import unittest

BASE = Path(__file__).parent
REPO = BASE.parents[4]
PROTECTED = [REPO/'_meta/runs/wiki/20260929T083140Z-p2-resume/publish-one.py',
             BASE.parent/'runtime/manual_pdf.py']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class CountedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subtest_results = []

    def addSubTest(self, test, subtest, err):
        self.subtest_results.append(dict(test=str(test), case=str(subtest), passed=err is None))
        super().addSubTest(test, subtest, err)

before = {str(p.relative_to(REPO)):digest(p) for p in PROTECTED}
module = types.ModuleType('test_pdf_plan')
module.__file__ = str(BASE/'test_pdf_plan.py')
exec(compile((BASE/'test_pdf_plan.py').read_bytes(), module.__file__, 'exec'), module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
stream = io.StringIO()
from typing import cast
result = cast(CountedResult, unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=CountedResult).run(suite))
after = {str(p.relative_to(REPO)):digest(p) for p in PROTECTED}
assert before == after, 'legacy helper or runtime adapter changed during synthetic verification'
source = (BASE/'pdf_plan.py').read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name):
        assert not (node.func.value.id == 'generic' and node.func.attr in ('inputs','new_plan','validate_plan','publish','main'))
files = {name:dict(sha256=digest(BASE/name),bytes=(BASE/name).stat().st_size,
                  lines=len((BASE/name).read_text().splitlines()))
         for name in ('pdf_plan.py','test_pdf_plan.py','verify_synthetic.py','HANDOFF.md')}
print(json.dumps(dict(schema='pkm-pdf-plan-synthetic-verification/v1',observed_at=datetime.now(timezone.utc).isoformat(),
    command=[sys.executable,'-B',str(Path(__file__))],tests=result.testsRun,
    subtests=len(result.subtest_results),subtest_results=result.subtest_results,failures=len(result.failures),
    errors=len(result.errors),skipped=len(result.skipped),success=result.wasSuccessful(),
    raw_output=stream.getvalue(),protected_code_before=before,protected_code_after=after,
    artifacts=files,syntax='ast.parse passed',legacy_entrypoint_calls='absent',
    scope='Synthetic filesystem only. No live source/result/provider/parser/publication.'),ensure_ascii=False,indent=2))
sys.exit(0 if result.wasSuccessful() else 1)
