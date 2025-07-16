from flask import request, jsonify, make_response
from models import db, User, Record, Media

def register_routes(app):

    @app.route('/')
    def home():
        return make_response("<h1>Welcome to Jiseti</h1>", 200)

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return make_response({'error': 'Email already registered'}, 400)

        new_user = User(
            name=data['name'],
            email=data['email'],
            password=data['password'],  # Note: Plaintext for demo only
            role=data.get('role', 'user')
        )
        db.session.add(new_user)
        db.session.commit()
        return make_response({'message': 'User created'}, 201)

    @app.route('/users')
    def list_users():
        users = User.query.all()
        return make_response([
            {'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role}
            for u in users
        ], 200)

    @app.route('/records', methods=['POST'])
    def create_record():
        data = request.get_json()
        record = Record(
            type=data['type'],
            title=data['title'],
            description=data['description'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            user_id=data['user_id']
        )
        db.session.add(record)
        db.session.commit()
        return make_response({'message': 'Record created'}, 201)

    @app.route('/records')
    def list_records():
        records = Record.query.all()
        return make_response([rec.to_dict() for rec in records], 200)

    @app.route('/records/<int:id>', methods=['PATCH'])
    def edit_record(id):
        record = Record.query.get_or_404(id)
        if record.status != 'draft':
            return make_response({'error': 'Cannot edit finalized record'}, 403)

        data = request.get_json()
        record.title = data.get('title', record.title)
        record.description = data.get('description', record.description)
        record.latitude = data.get('latitude', record.latitude)
        record.longitude = data.get('longitude', record.longitude)
        db.session.commit()
        return make_response({'message': 'Record updated'}, 200)

    @app.route('/records/<int:id>', methods=['DELETE'])
    def delete_record(id):
        record = Record.query.get_or_404(id)
        if record.status != 'draft':
            return make_response({'error': 'Cannot delete finalized record'}, 403)
        db.session.delete(record)
        db.session.commit()
        return make_response({'message': 'Record deleted'}, 200)

    @app.route('/records/<int:id>/status', methods=['PATCH'])
    def update_status(id):
        record = Record.query.get_or_404(id)
        data = request.get_json()
        user = User.query.get(data.get('admin_id'))

        if not user or not user.is_admin():
            return make_response({'error': 'Only admins can change record status'}, 403)

        new_status = data.get('status')
        if new_status not in ['under investigation', 'rejected', 'resolved']:
            return make_response({'error': 'Invalid status'}, 400)

        record.status = new_status
        db.session.commit()
        return make_response({'message': f'Status updated to {new_status}'}, 200)

    @app.route('/records/<int:id>/media', methods=['POST'])
    def add_media(id):
        record = Record.query.get_or_404(id)
        if record.status != 'draft':
            return make_response({'error': 'Cannot add media to finalized record'}, 403)

        data = request.get_json()
        new_media = Media(
            image_url=data.get('image_url'),
            video_url=data.get('video_url'),
            record_id=id
        )
        db.session.add(new_media)
        db.session.commit()
        return make_response({'message': 'Media added'}, 201)
