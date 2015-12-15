# sales-finder

SalesFinder is an app to explore data on residential property sales in New York City.

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

To run tests:
```
python manage.py test
```
