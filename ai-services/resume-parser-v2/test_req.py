import urllib.request, json
import uuid

with open('test_resume.txt', 'r', encoding='utf-8') as f:
    text_data = f.read()
    
boundary = uuid.uuid4().hex
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="test_resume.txt"\r\n'
    f'Content-Type: text/plain\r\n\r\n'
    f'{text_data}\r\n'
    f'--{boundary}--\r\n'
).encode('utf-8')

req = urllib.request.Request('http://localhost:8000/api/v1/intelligence/analyze', data=body)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8')).get('data', {})
    print('SKILLS:', data.get('skills'))
    print('SECTIONS:', [s.get('section_name') for s in data.get('layout_structure', {}).get('sections', [])])
except Exception as e:
    print('ERROR:', e)
