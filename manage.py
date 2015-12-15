#!/usr/bin/env python
'''
This is the script for launching the application and managing resources.

For a list of available commands, type:
python manage.py --help

First, we create an app object (which is in fact an instance of the Flask class)
using the create_app factory function defined in the sales_finder package.

Then we create a manager object to allow the user to run functions from the command
line. We attach the manager object to the app object.
'''

import os
from flask.ext.script import Manager, Shell, prompt_bool
from sqlalchemy.exc import SQLAlchemyError

from sales_finder import create_app, db, sales_data

# Create an app object, either using the FLASK_CONFIG environment
# variable, or else the default config object
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Initialize the manager object, so we can easily use command line
# to set up/configure/launch the app
manager = Manager(app)



""" Define manager commands """
# The manager object allows us to add commands that the user can call from
# the command line. Each command is just a way to call a function, which we define
# in this module. Note that -runserver- is added as a command by default.
# -shell- is also a default command, but we re-define it to add the application context



'''
shell command

This command allows us to launch a shell with the objects our app will use already
created, in the form of a _context_. That way, we can debug, and also interact with
the database just as our app would.
'''

def make_shell_context():
    '''Collect the app, database, and sales_data objects into a context dict.
    This will allow us to use the -shell- command to open an interactive python
    shell with all the objects as they would be when the app is running.'''
    return dict(app=app, db=db, sales_data=sales_data)

# Add the shell command to the manager
manager.add_command("shell", Shell(make_context=make_shell_context))



'''
test command

This command will run the unittests
'''

# The manager.command decorator means the test() function will be
# available on the command line as a subcommand for manager.py
@manager.command
def test():
    '''Run unit tests'''
    import unittest

    # Get all the tests in the "tests" package and run them
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)



'''
init_db command

This command will create a new database from scratch, loading data from the NYC Department
of Finance's website. Because it overwrites the database, it requires the user to confirm.

On a fresh installation, this command needs to be run to create the database the rest of the app
relies on.
'''

# Use decorators to tell the manager to treat this as a command, and also to set up the options
# available to the user from the command line. Typing "python manage.py init_db --help" will
# display these options.
@manager.option('--noconfirm', action='store_true', dest='no_confirm', default=False,
                help="Flag to avoid asking user for confirmation")
def init_db(no_confirm=False, drop_all_tables=False):
    '''Create the database from scratch. This will DELETE any data already in the database.

    no_confirm will skip user confirmation
    drop_all_tables will reset the entire database, not just the table set in the app's config
    '''

    # Unless the no_confirm parameter is true, prompt user for a response, converted to a boolean.
    # If the response is negative (false), cancel the operation and return. Otherwise, keeep going.
    if not no_confirm:
        try:
            if not prompt_bool(
                    "This will DESTROY all data in database and download new data. Are you sure"):
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
        except SQLAlchemyError: # Raised if table doesn't exist
            print "(table %s does not exist)" % table

    print "\nInitializing database..."
    sales_data.create_from_scratch()



if __name__ == '__main__':
    try:
        manager.run()
    except KeyboardInterrupt:
        print "\nQUITTING"
