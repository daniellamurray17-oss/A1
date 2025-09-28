import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User, Street, Route, StopRequest, Notification
from App.main import create_app
from App.controllers import (
    create_user,
    get_all_users_json,
    get_all_users,
    initialize
)

# Create app and migration object
app = create_app()
migrate = get_migrate(app)

'''
Database Commands
'''
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('Database initialized')

'''
User Commands
'''
user_cli = AppGroup('user', help='User object commands')

@user_cli.command("create", help="Creates a user")
@click.argument("username")
@click.argument("password")
@click.argument("role", default="resident")
def create_user_command(username, password, role):
    create_user(username, password, role=role)
    print(f'User {username} with role {role} created!')

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli)

'''
Test Commands
'''
test = AppGroup('test', help='Testing commands')

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))

app.cli.add_command(test)
