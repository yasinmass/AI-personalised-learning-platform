import requests
BASE='http://127.0.0.1:8000'
for cid in range(1,9):
    try:
        r = requests.get(f'{BASE}/admin/courses/coursevideo/fetch-topics/?course_id={cid}', timeout=5)
        print('course', cid, 'status', r.status_code, 'topics', r.text)
    except Exception as e:
        print('course', cid, 'error', e)
