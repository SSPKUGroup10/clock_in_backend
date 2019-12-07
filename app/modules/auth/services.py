from app.extensions import db
from app.models import User


from app.modules.errors import ERRORS
from . import jwt


def jwt_auth_response(jwt_token, user):
    return {
        'accessToken': jwt_token.decode('utf-8'),
        'userInfo': user.username
    }


def user_login(kwargs):
    if not kwargs.get('username') or not kwargs.get('password'):
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg':  "用户账号密码为空"}
    user = User.query.filter_by(username=kwargs['username']).first()
    if user is None:
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg': '用户名不存在！'}
    if not user.verify_password(kwargs['password']):
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg': '用户名或密码错误！'}

    jwt_token = jwt.encode({'uid': user.id})

    return {'status': 1, 'data': jwt_auth_response(jwt_token, user)}


def register(kwargs):
    if not kwargs.get('username') or not kwargs.get('password'):
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg':  "用户账号密码为空"}
    user = User.query.filter_by(username=kwargs['username']).first()
    if user:
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg': '用户名已存在！'}
    user = User()
    user.username = kwargs.get('username')
    user.password = kwargs.get('password')
    db.save(user)

    jwt_token = jwt.encode({'uid': user.id})
    return {'status': 1, 'data': jwt_auth_response(jwt_token, user)}