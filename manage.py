#!/usr/bin/env python
'''
This is the script for launching the application
'''

import os
from app import create_app, db
#from app.models import User, Role
from flask.ext.script import Manager, Shell
#from flask.ext.migrate import Migrate, MigrateCommand

# Create an app object, either using the FLASK_CONFIG environment
# variable, or else the default config object
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Initialize the manager object, so we can easily use command line
# to set up/configure/launch the app
manager = Manager(app)

#migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app) #, db=db, User=User, Role=Role)

# Add the shell command to the manager, so we can launch a shell
# with the objects already created in the form of a context
manager.add_command("shell", Shell(make_context=make_shell_context))
#manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()