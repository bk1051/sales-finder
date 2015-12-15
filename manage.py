#!/usr/bin/env python
'''
This is the script for launching the application and managing resources.

For a list of available commands, type:
python manage.py --help
'''

import os
from flask.ext.script import Manager, Shell, prompt_bool
from sqlalchemy.exc import SQLAlchemyError

from app import create_app, db, sales_data

# Create an app object, either using the FLASK_CONFIG environment
# variable, or else the default config object
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Initialize the manager object, so we can easily use command line
# to set up/configure/launch the app
manager = Manager(app)

#migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, sales_data=sales_data)

# Add the shell command to the manager, so we can launch a shell
# with the objects already created in the form of a context
manager.add_command("shell", Shell(make_context=make_shell_context))



# The manager.command decorator means the test() function will be
# available on the command line as a subcommand for manager.py
@manager.command
def test():
    '''Run unit tests'''
    import unittest
    # Get all the tests in the "tests" package and run them
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
@manager.option('--noconfirm', dest='no_confirm', type=bool, default='False', 
                help="Flag to avoid asking user for confirmation")
@manager.option('--drop-all', dest='drop_all_tables', type=bool, default='False',
                help="Flag to drop all tables in the database. Default to drop only table set based on config.")
def init_db(no_confirm=False, drop_all_tables=False):
    '''This will create the database from scratch'''

    # Unless the no_confirm parameter is true, prompt user for a response, converted to a boolean.
    # If the response is negative (false), cancel the operation and return. Otherwise, keeep going.
    if not no_confirm:
        try:
            if not prompt_bool("This will DESTROY all data in database and download new data. Are you sure"):
                print "Cancelled"
                return
        except EOFError:
            print "\nInvalid response. Aborting."
            return

    if drop_all_tables:
        drop_tables = db.engine.table_names()
    else:
        drop_tables = [sales_data.table]

    print "Dropping tables: %s" % drop_tables
    for table in drop_tables:
        try:
            db.engine.execute("DROP TABLE %s" % table)
        except SQLAlchemyError as e:
            print "Table %s does not exist\n%s" % (table, e)

    

    print "\nInitializing database..."
    sales_data.create_from_scratch()




if __name__ == '__main__':
    try:
        manager.run()
    except KeyboardInterrupt:
        print "\nQUITTING"