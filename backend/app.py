import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc))

    def as_dict(self):
        return dict(id=self.id, title=self.title, content=self.content,
                    created_at=self.created_at.isoformat())


def create_app(database_url=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url or os.environ['DATABASE_URL'],
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
        MAX_CONTENT_LENGTH=65536,
    )
    db.init_app(app)

    @app.cli.command('init-db')
    def init_db():
        db.create_all()

    @app.get('/api/health')
    def health():
        db.session.execute(text('SELECT 1'))
        return jsonify(status='ok', version=os.getenv('APP_VERSION', 'development'))

    @app.get('/api/posts')
    def list_posts():
        return jsonify([p.as_dict() for p in db.session.execute(
            db.select(Post).order_by(Post.id.desc())).scalars()])

    def payload():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None
        title, content = data.get('title'), data.get('content')
        if not isinstance(title, str) or not isinstance(content, str):
            return None
        title, content = title.strip(), content.strip()
        if not 1 <= len(title) <= 120 or not 1 <= len(content) <= 10000:
            return None
        return dict(title=title, content=content)

    @app.post('/api/posts')
    def create_post():
        data = payload()
        if data is None:
            return jsonify(error='제목은 1~120자, 내용은 1~10000자로 입력하세요.'), 400
        post = Post(**data)
        db.session.add(post)
        db.session.commit()
        return jsonify(post.as_dict()), 201

    @app.put('/api/posts/<int:post_id>')
    def update_post(post_id):
        post = db.get_or_404(Post, post_id)
        data = payload()
        if data is None:
            return jsonify(error='제목은 1~120자, 내용은 1~10000자로 입력하세요.'), 400
        post.title, post.content = data['title'], data['content']
        db.session.commit()
        return jsonify(post.as_dict())

    @app.delete('/api/posts/<int:post_id>')
    def delete_post(post_id):
        post = db.get_or_404(Post, post_id)
        db.session.delete(post)
        db.session.commit()
        return '', 204

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        app.logger.exception('Database operation failed')
        return jsonify(error='데이터베이스 연결을 확인해 주세요.'), 503

    return app
