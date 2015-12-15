# sales-finder

SalesFinder is an app to explore data on residential property sales in New York City. It is built using [Flask](http://flask.pocoo.org/), a lightweight framework for web apps in python.

## Code Layout for SalesFinder
The main package, `sales_finder`, contains code to create the app and manage the database, as well as to tell the server how to route requests.

`sales_finder/__init__.py` contains and app _factory_ function, which will create an app instance. This allows us to build an app instance for testing, for example, and a different one for the main development.

`sales_finder.main` is the package that contains the main "blueprint", which is a way of packaging routing code together to apply to an app instance; sales_finder.main is what tells the server to run the `results` function when the user goes to `http://localhost:5000/results/`. It also handles HTTP errors (i.e. 404 and 500 response codes).

The `templates` folder in sales_finder contains the [Jinja2](http://jinja.pocoo.org/docs/dev/) templates that the app will use to construct HTML pages dynamically, based on the user's input.

`sales_finder/data.py` contains code for loading sales data and saving it to a database (by default, SQLite3, though the app is designed to be deployable to, for example, Heroku), as well as querying the database and returning summary statistics for different subsets.

`sales_finder/plots.py` contains code for plotting data.

`sales_finder.tests` is the package for running unit tests.

`config.py` defines different configurations (e.g. production, development, testing).

`manage.py` is the main file used to run, install, and maintain SalesFinder. It contains code to allow the user to manage SalesFinder from the command line. This may be the best starting point for reading the code, although the code to run SalesFinder is the `manage.py runserver` command, which is a default and part of the Flask-Script package. The key code that `runserver` does is create an app instance, create a server, and then instruct the server to handle requests using the `sales_finder` package.

## Instalation

Before installation, we recommend setting up a __virtual environment__. There's a great guide to virtual environments here:
http://docs.python-guide.org/en/latest/dev/virtualenvs/


Start by `cd`ing to the directory where you want to install SalesFinder. Then type:
```
git clone https://github.com/bk1051/sales-finder.git
```

This will clone SalesFinder into the `sales-finder` directory. Next, type:

```
cd sales-finder
virtualenv venv
source venv/bin/activate
```

Now you'll need to install the project dependencies, using `pip` (which `virtualenv` should have installed for you):

```
pip install -r requirements.txt
```

Now, set up the database. The default is to use an SQLite3 database, which is stored as a file in the root directory of the repo. To initialize it (which will download data from the Department of Finance's website), type:

```
python manage.py init_db
```

When it asks if you're sure you want to replace the data in the database, type `y` (or `Y`, or `Yes`, etc.). It will take some time to download all the data and store it in the database.

Once that's done, to run on your local server, just type:
```
python manage.py runserver
```

Finally, open a web browser and go to [http://localhost:5000/](http://localhost:5000/), and you should see SalesFinder running!

## Testing
To run tests:
```
python manage.py test
```
