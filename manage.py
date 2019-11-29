# -*- coding:utf-8 -*-
from flask import current_app
from datetime import datetime, timedelta
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import func
from app import create_app
from app.extensions import db

app = create_app('development')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db)


def command_list_routes(name):
    from colorama import init, Fore
    from tabulate import tabulate
    init()
    table = []
    print(Fore.LIGHTRED_EX + name)
    for rule in app.url_map.iter_rules():
        table.append([
            Fore.BLUE + rule.endpoint,
            Fore.GREEN + ','.join(rule.methods),
            Fore.YELLOW + rule.rule])

    print(tabulate(sorted(table),
                   headers=(
                       Fore.BLUE + 'End Point(method name)',
                       Fore.GREEN + 'Allowed Methods',
                       Fore.YELLOW + 'Routes'
                   ), showindex="always", tablefmt="grid"))




@manager.command
def routes():
    command_list_routes('API Routes')


@manager.command
def secret_key():
    import os
    import binascii
    return binascii.hexlify(os.urandom(24))


@manager.option('-i', '--uid', help='User id')
def jwt_token(uid):
    jwt = JWTAuth()
    jwt.exp = 3600 * 24 * 100
    user = User.query.get(uid)
    user_wechat = UserWechat.query.filter_by(user_id=uid).first()
    ret = jwt.encode({'oid': user_wechat.public_openid, 'uid': user.id})
    return ret.decode('utf-8')


manager.add_command('shell', Shell(make_context=make_shell_context))

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
