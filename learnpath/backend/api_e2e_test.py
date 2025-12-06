import urllib.request, urllib.error, json, ssl

BASE='http://127.0.0.1:8000/api'
ctx=ssl.create_default_context()

def http_get(path, token=None):
    req=urllib.request.Request(BASE+path)
    req.add_header('Content-Type','application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            return json.load(resp)
    except Exception as e:
        print('GET error', path, e)
        return None

def http_post(path, data, token=None):
    body=json.dumps(data).encode('utf-8')
    req=urllib.request.Request(BASE+path, data=body, method='POST')
    req.add_header('Content-Type','application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        print('POST HTTPError', path, e.code, e.read().decode())
        return None
    except Exception as e:
        print('POST error', path, e)
        return None

print('Listing courses...')
courses=http_get('/courses/list')
print('courses=', courses)

print('Registering user...')
reg=http_post('/auth/register', {
    'email':'e2e_test_user@example.com', 'username':'e2e_test_user', 'first_name':'E2E', 'last_name':'Test', 'password':'Testpass123', 'password2':'Testpass123'
})
print('reg=', reg)

print('Logging in...')
login=http_post('/auth/login', {'email':'e2e_test_user@example.com','password':'Testpass123'})
print('login=', login)
if not login or 'token' not in login:
    print('Login failed, abort')
    exit(1)

token=login['token']
print('Token obtained')

# choose first course id
if courses and isinstance(courses, list) and len(courses)>0:
    course_id=courses[0]['id']
else:
    print('No courses available')
    exit(1)

print('Generate questions for course', course_id)
questions=http_post('/assessment/generate-questions', {'course_id': course_id}, token=token)
print('questions=', questions)

# Prepare dummy answers
answers={}
if questions and 'questions' in questions:
    for i,q in enumerate(questions['questions']):
        answers[str(i)]='A'

print('Submitting assessment...')
submit=http_post('/assessment/submit', {'assessment_id': questions.get('assessment_id') if questions else None, 'answers': answers}, token=token)
print('submit=', submit)

if not submit:
    print('Submit failed')
    exit(1)

assessment_id=submit.get('assessment_id') or local.get('assessment_id') if False else None
# If API returned assessment id in response use it, else get from questions
if 'assessment_id' in submit:
    assessment_id=submit['assessment_id']
elif questions and 'assessment_id' in questions:
    assessment_id=questions['assessment_id']

print('assessment_id=', assessment_id)

print('Generating roadmap...')
roadmap=http_post('/assessment/generate-roadmap', {'assessment_id': assessment_id, 'duration_weeks': 12, 'skill_level': submit.get('skill_level'), 'user_answers': answers}, token=token)
print('roadmap=', roadmap)

print('E2E test completed')
