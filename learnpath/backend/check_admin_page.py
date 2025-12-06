import requests
url = 'http://127.0.0.1:8000/admin/courses/coursevideo/add/'
try:
    r = requests.get(url, timeout=10)
    print('status', r.status_code)
    print('has_js:', 'courses/admin_coursevideo.js' in r.text)
    print('has_id_course:', 'id="id_course"' in r.text)
    print('has_id_topic:', 'id="id_topic"' in r.text)
    # show lines containing our JS include or ids
    for l in r.text.split('\n'):
        if 'courses/admin_coursevideo.js' in l or 'id="id_course"' in l or 'id="id_topic"' in l:
            print(l.strip())
except Exception as e:
    print('error', e)
