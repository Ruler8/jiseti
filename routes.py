from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, NormalUser, Administrator, Record, Media

def register_routes(app):

    @app.route('/')
    def home():
        return make_response("<h1>Welcome to Jiseti</h1>", 200)

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        role = data.get('role', 'user')

        if role == 'admin':
            if Administrator.query.filter_by(email=data['email']).first():
                return make_response({'error': 'Email already registered as admin'}, 400)
            new_admin = Administrator(
                name=data['name'],
                email=data['email'],
                password=data['password'],
                admin_number=data['admin_number']
            )
            db.session.add(new_admin)
            db.session.commit()
            return make_response({'message': 'Administrator account created'}, 201)
        else:
            if NormalUser.query.filter_by(email=data['email']).first():
                return make_response({'error': 'Email already registered'}, 400)
            new_user = NormalUser(
                name=data['name'],
                email=data['email'],
                password=data['password']
            )
            db.session.add(new_user)
            db.session.commit()
            return make_response({'message': 'User account created'}, 201)

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        role = data.get('role', 'user')

        if role == 'admin':
            user = Administrator.query.filter_by(email=data['email'], password=data['password']).first()
        else:
            user = NormalUser.query.filter_by(email=data['email'], password=data['password']).first()

        if not user:
            return make_response({'error': 'Invalid credentials'}, 401)

        access_token = create_access_token(identity={'id': user.id, 'role': role})
        return make_response({'access_token': access_token}, 200)

    @app.route('/normal_users')
    @jwt_required()
    def list_normal_users():
        identity = get_jwt_identity()
        if identity['role'] != 'admin':
            return make_response({'error': 'Unauthorized'}, 403)
        users = NormalUser.query.all()
        return make_response([
            {'id': u.id, 'name': u.name, 'email': u.email}
            for u in users
        ], 200)

    @app.route('/records', methods=['POST'])
    @jwt_required()
    def create_record():
        identity = get_jwt_identity()
        if identity['role'] != 'user':
            return make_response({'error': 'Only normal users can create records'}, 403)

        data = request.get_json()
        record = Record(
            type=data['type'],
            title=data['title'],
            description=data['description'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            normal_user_id=identity['id']
        )
        db.session.add(record)
        db.session.commit()
        return make_response({'message': 'Record created'}, 201)

    @app.route('/records')
    @jwt_required()
    def list_records():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        records = Record.query.paginate(page=page, per_page=per_page, error_out=False)
        return make_response({
            'records': [rec.to_dict() for rec in records.items],
            'total': records.total,
            'page': records.page,
            'pages': records.pages
        }, 200)

    @app.route('/records/<int:id>', methods=['PATCH'])
    @jwt_required()
    def edit_record(id):
        identity = get_jwt_identity()
        if identity['role'] != 'user':
            return make_response({'error': 'Unauthorized'}, 403)

        record = Record.query.get_or_404(id)
        if record.normal_user_id != identity['id']:
            return make_response({'error': 'Unauthorized'}, 403)
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
    @jwt_required()
    def delete_record(id):
        identity = get_jwt_identity()
        if identity['role'] != 'user':
            return make_response({'error': 'Unauthorized'}, 403)

        record = Record.query.get_or_404(id)
        if record.normal_user_id != identity['id']:
            return make_response({'error': 'Unauthorized'}, 403)
        if record.status != 'draft':
            return make_response({'error': 'Cannot delete finalized record'}, 403)

        db.session.delete(record)
        db.session.commit()
        return make_response({'message': 'Record deleted'}, 200)

    @app.route('/records/<int:id>/status', methods=['PATCH'])
    @jwt_required()
    def update_status(id):
        identity = get_jwt_identity()
        if identity['role'] != 'admin':
            return make_response({'error': 'Only admins can change record status'}, 403)

        record = Record.query.get_or_404(id)
        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ['under investigation', 'rejected', 'resolved']:
            return make_response({'error': 'Invalid status'}, 400)

        record.status = new_status
        db.session.commit()
        return make_response({'message': f'Status updated to {new_status}'}, 200)

    @app.route('/records/<int:id>/media', methods=['POST'])
    @jwt_required()
    def add_media(id):
        identity = get_jwt_identity()
        if identity['role'] != 'user':
            return make_response({'error': 'Unauthorized'}, 403)

        record = Record.query.get_or_404(id)
        if record.normal_user_id != identity['id']:
            return make_response({'error': 'Unauthorized'}, 403)
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