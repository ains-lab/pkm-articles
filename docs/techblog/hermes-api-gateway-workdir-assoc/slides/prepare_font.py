#!/usr/bin/env python3
"""Create a renamed OFL Korean subset using existing FontTools, no installation."""
from pathlib import Path
import sys,hashlib,json,importlib
# Optionally point at an already installed/cached FontTools module directory.
if len(sys.argv)>1:sys.path.insert(0,sys.argv[1])
subset=importlib.import_module('fontTools.subset')
TTFont=importlib.import_module('fontTools.ttLib').TTFont
root=Path(__file__).resolve().parent
original=Path('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')
font=TTFont(original)
text=''.join(p.read_text() for ext in ['*.py','*.js','*.css'] for p in root.glob(ext))+''.join(p.read_text() for p in root.parent.glob('*.md'))+(root.parent/'verification.json').read_text()
options=subset.Options()
options.drop_tables+=['TSI0','TSI1','TSI2','TSI3','TSI5']
options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*']
subsetter=subset.Subsetter(options=options);subsetter.populate(text=text);subsetter.subset(font)
for record in font['name'].names:
    replacement={1:'LectureWikiSans',2:'Regular',3:'LectureWikiSans-Regular-v1',4:'LectureWikiSans Regular',6:'LectureWikiSans-Regular',16:'LectureWikiSans',17:'Regular'}.get(record.nameID)
    if replacement is not None:record.string=replacement.encode(record.getEncoding(),errors='replace')
font.flavor='woff2'
out=root/'lecture-korean.woff2';font.save(out)
report={'original_file':str(original),'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'output_file':out.name,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'license':'OFL-1.1','family':'LectureWikiSans','original_file_unchanged':True,'dropped_editor_tables':['TSI0','TSI1','TSI2','TSI3','TSI5'],'reason':'Chromium OTS rejected zero-length TSI3 in the installed original; use standard FontTools subset with renamed derivative.'}
(root/'font-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
