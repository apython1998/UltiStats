from flask import jsonify, request, url_for, g
from app import db
from app.models import User
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.api.errors import bad_request, error_response


@bp.route('/v1/register', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict(include_email=True))
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/v1/login', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@bp.route('/v1/logout', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204


@bp.route('/v1/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
 return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/v1/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict(include_email=True))


@bp.route('/v1/users/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user is not g.current_user:
        return bad_request('Cannot delete other users')
    else:
        user.revoke_token()
        db.session.delete(user)
        db.session.commit()
        response = jsonify(None)
        response.status_code = 204
        return response
