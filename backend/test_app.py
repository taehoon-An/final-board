import unittest
from app import create_app, db


class BoardTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('sqlite://')
        self.app.config['TESTING'] = True
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_crud(self):
        response = self.client.post('/api/posts', json={'title': '첫 글', 'content': '내용'})
        self.assertEqual(response.status_code, 201)
        post_id = response.json['id']
        self.assertEqual(self.client.get('/api/posts').json[0]['title'], '첫 글')
        response = self.client.put(f'/api/posts/{post_id}', json={'title': '수정', 'content': '수정 내용'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/posts').json[0]['content'], '수정 내용')
        self.assertEqual(self.client.delete(f'/api/posts/{post_id}').status_code, 204)
        self.assertEqual(self.client.get('/api/posts').json, [])

    def test_validation_and_missing_post(self):
        for data in [None, [], {}, {'title': '', 'content': '내용'}, {'title': 'x'*121, 'content': '내용'}]:
            self.assertEqual(self.client.post('/api/posts', json=data).status_code, 400)
        self.assertEqual(self.client.delete('/api/posts/999').status_code, 404)
        self.assertEqual(self.client.get('/api/health').json['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
