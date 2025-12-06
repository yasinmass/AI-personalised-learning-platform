import requests
from bs4 import BeautifulSoup

BASE = 'http://127.0.0.1:8000'
LOGIN = BASE + '/admin/login/'
ADD = BASE + '/admin/courses/coursevideo/add/'
USERNAME = 'admin'
PASSWORD = 'AdminPass123'

s = requests.Session()
# get login page
r = s.get(LOGIN, timeout=10)
print('login status', r.status_code)
# parse csrf token
soup = BeautifulSoup(r.text, 'html.parser')
csrf = soup.find('input', attrs={'name':'csrfmiddlewaretoken'})
if csrf:
    token = csrf.get('value')
    print('csrf token found')
else:
    token = None
    print('no csrf token found')
# post login
login_data = {
    'username': USERNAME,
    'password': PASSWORD,
}
headers = {'Referer': LOGIN}
if token:
    login_data['csrfmiddlewaretoken'] = token
r2 = s.post(LOGIN, data=login_data, headers=headers, timeout=10)
print('post login status', r2.status_code)
# try to get add page
r3 = s.get(ADD, timeout=10)
print('add page status', r3.status_code)
print('has js include?', 'courses/admin_coursevideo.js' in r3.text)
print('has id_course?', 'id="id_course"' in r3.text)
print('has id_topic?', 'id="id_topic"' in r3.text)
# fetch fetch-topics endpoint for course 8
ep = BASE + '/admin/courses/coursevideo/fetch-topics/?course_id=8'
r4 = s.get(ep, timeout=10)
print('fetch topics status', r4.status_code, r4.text)
