import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assessments.models import Roadmap
from courses.models import Course


def extract_topics_from_roadmap(data):
    topics = []
    if not isinstance(data, dict):
        return topics
    # chapters
    for ch in data.get('chapters', []) or []:
        ch_topics = ch.get('topics') or []
        if isinstance(ch_topics, str):
            ch_topics = [ch_topics]
        for t in ch_topics:
            t = (t or '').strip()
            if t and t not in topics:
                topics.append(t)
    # related
    for rt in data.get('related_topics', []) or []:
        r = (rt or '').strip()
        if r and r not in topics:
            topics.append(r)
    # modules (legacy)
    for m in data.get('modules', []) or []:
        if isinstance(m, str):
            mname = m.strip()
            if mname and mname not in topics:
                topics.append(mname)
            continue
        if isinstance(m, dict):
            mname = m.get('title') or m.get('name')
            if mname:
                mname = (mname or '').strip()
                if mname and mname not in topics:
                    topics.append(mname)
            for t in (m.get('topics') or m.get('lessons') or []) or []:
                if isinstance(t, dict):
                    tn = t.get('title') or t.get('name') or ''
                else:
                    tn = t
                tn = (tn or '').strip()
                if tn and tn not in topics:
                    topics.append(tn)
    return topics


for cid in range(1, 9):
    try:
        course = Course.objects.filter(id=cid).first()
        if not course:
            print(json.dumps({'course_id': cid, 'error': 'Course not found'}))
            continue
        roadmap = Roadmap.objects.filter(course_id=cid).order_by('-created_at').first()
        if not roadmap:
            print(json.dumps({'course_id': cid, 'topics': []}))
            continue
        topics = extract_topics_from_roadmap(roadmap.roadmap_data)
        print(json.dumps({'course_id': cid, 'topics': topics}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'course_id': cid, 'error': str(e)}))
