"""Exercise the actual frontend proxy and database; remove only this test's post."""
import json
import sys
import uuid
from urllib.request import Request, urlopen

base = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'http://127.0.0.1:2000'


def call(path, method='GET', data=None):
    body = None if data is None else json.dumps(data).encode()
    with urlopen(Request(base + path, data=body, method=method,
                         headers={'Content-Type': 'application/json'}), timeout=15) as response:
        raw = response.read()
        return response.status, json.loads(raw) if raw else None


assert call('/api/health')[1]['status'] == 'ok'
marker = 'CI smoke ' + uuid.uuid4().hex[:8]
status, post = call('/api/posts', 'POST', {'title': marker, 'content': 'CRUD integration test'})
assert status == 201
post_id = post['id']
try:
    assert any(p['id'] == post_id for p in call('/api/posts')[1])
    status, updated = call('/api/posts/' + str(post_id), 'PUT',
                           {'title': marker + ' updated', 'content': '수정 확인'})
    assert status == 200 and updated['content'] == '수정 확인'
    assert any(p['id'] == post_id and p['content'] == '수정 확인' for p in call('/api/posts')[1])
finally:
    assert call('/api/posts/' + str(post_id), 'DELETE')[0] == 204
assert all(p['id'] != post_id for p in call('/api/posts')[1])
print('PASS: health, create, list, update, delete through frontend proxy')
