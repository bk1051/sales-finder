#!/usr/bin/env python
'''
This is the script for launching the application
'''

import os
from app import create_app, db
from app.models import Sale
from app.data import SalesData
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
    return dict(app=app, db=db, Sale=Sale)

# Add the shell command to the manager, so we can launch a shell
# with the objects already created in the form of a context
manager.add_command("shell", Shell(make_context=make_shell_context))
#manager.add_command('db', MigrateCommand)


# The manager.command decorator means the test() function will be
# available on the command line as a subcommand for manager.py
@manager.command
def test():
    '''Run unit tests'''
    import unittest
    # Get all the tests in the "tests" package and run them
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


def warn_user(message):
    '''Warn user about database overwriting'''
    if message is not None:
        print message
    answer = raw_input("Are you sure you want to do this? [y/n] ")
    while answer.lower()[0] not in ('y', 'n'):
        answer = raw_input("Please enter y or n. ")

    return answer.lower()[0] == 'y'


@manager.command
def init_db():
    '''This will create the database from scratch'''
    try:
        if not warn_user("This will DESTROY all data in the database and replace with newly \ndownloaded data."):
            print "Cancelled"
            return
    except EOFError:
        print "\nInvalid response. Aborting."
        return

    print "\nInitializing database..."
    db.drop_all()
    db.create_all()
    salesdata = SalesData()
    salesdata.create_from_scratch(db)




if __name__ == '__main__':
    try:
        manager.run()
    except KeyboardInterrupt:
        print "\nQUITTING"