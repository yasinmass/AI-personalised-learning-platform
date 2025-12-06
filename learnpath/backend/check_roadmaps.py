import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course
from assessments.models import Roadmap

for c in Course.objects.all().order_by('id'):
    print(f"Course {c.id}: {getattr(c, 'title', '')}")
    r = Roadmap.objects.filter(course=c).order_by('-created_at').first()
    if not r:
        print('  No Roadmap found')
        continue
    data = r.roadmap_data
    if not isinstance(data, dict):
        print('  Roadmap data is not a dict, type=', type(data))
        print('  Raw:', data)
        continue
    chapters = data.get('chapters')
    if not chapters:
        # Try legacy 'modules' shape and extract topics if possible
        extracted = []
        for m in data.get('modules', []) or []:
            if isinstance(m, str):
                nm = m.strip()
                if nm:
                    extracted.append(nm)
                continue
            if isinstance(m, dict):
                mname = m.get('title') or m.get('name')
                if mname:
                    extracted.append(mname)
                for t in (m.get('topics') or m.get('lessons') or []) or []:
                    if isinstance(t, dict):
                        tn = t.get('title') or t.get('name')
                    else:
                        tn = t
                    if tn:
                        extracted.append(tn)
        if extracted:
            print('  No chapters — extracted topics/modules:')
            for e in extracted:
                print('   -', e)
        else:
            print('  Roadmap has no chapters; keys=', list(data.keys()))
        continue
    print('  Chapters:')
    for ch in chapters:
        ch_title = ch.get('title') or ch.get('name') or '<no title>'
        topics = []
        for t in ch.get('topics', []):
            if isinstance(t, dict):
                topics.append(t.get('title') or t.get('name'))
            else:
                topics.append(t)
        print(f"    - {ch_title}: topics={topics}")
