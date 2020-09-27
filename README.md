This project is a complement to [python-rules](https://github.com/valhuber/python-rules),
which explains the concepts of rules, as well being used for 
development of `python-rules`.

This project focuses on the practicalities of installation and configuration,
by including 2 (unrelated) samples:
* `nw` (same as in [python-rules](https://github.com/valhuber/python-rules))
* `banking`

This page shows the common install / configure tasks common to both.
In both cases, they use [fab-quickstart](https://github.com/valhuber/fab-quick-start),
which is optional but recommended since it makes it really
easy to explore your database.


## Installing `python-rules-examples`

To get started, you will need:

* Python3.8 (Relies on `from __future__ import annotations`, so requires Python 3.8)

   * Run the windows installer; on mac/Unix, consider [using brew](https://opensource.com/article/19/5/python-3-default-mac#what-to-do)
   
* virtualenv - see [here](https://www.google.com/url?q=https%3A%2F%2Fpackaging.python.org%2Fguides%2Finstalling-using-pip-and-virtual-environments%2F%23creating-a-virtual-environment&sa=D&sntz=1&usg=AFQjCNEu-ZbYfqRMjNQ0D0DqU1mhFpDYmw)  (e.g.,  `pip install virtualenv`)

* An IDE - any will do (I've used [PyCharm](https://www.jetbrains.com/pycharm/download) and [VSCode](https://code.visualstudio.com), install notes [here](https://github.com/valhuber/fab-quick-start/wiki/IDE-Setup)) - ide will do, though different install / generate / run instructions apply for running programs

Issues?  [Try here](https://github.com/valhuber/fab-quick-start/wiki/Mac-Python-Install-Issues).


Using your IDE or command line: 
```
git fork / clone
cd python-rules-examples
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Project Setup Cookbook
This project has already been set up.  Here's how we did it.

#### Create Environment
```
# create your project root (check this into scs)
mkdir python-rules-examples
cd my-project
virtualenv venv
# configure SCS to ignore venv
# windows .env\Scripts\activate
source venv/bin/activate

pip install -i https://test.pypi.org/simple/ python-rules
pip install SQLAlchemy
pip install sqlacodegen

# if using fab
pip install flask-appbuilder
pip install fab-quick-start

```

#### Create Project structure
Use whatever structure you like, but to make things
definite, here's how we did it for `nw` and `banking`:

```
mkdir nw
cd nw
cd nw_logic
```

#### Create Models

There are many ways to create models.
* You can create the models file by hand,
and use that to generate the database, or
* You can use an existing database, and
create a models file to match it.

For existing databases, consider using sqlacodegen.
Here, we'll use `nw` as our example;
we already have a sqlite database in our
`nw-app` folder so:

```
cd nw_app
sqlacodegen sqlite:///Northwind_small.sqlite --noviews > nw/nw_logic/app/models.py
```
The first parameter identifies your database location;
consult the sqlacodegen documentation.

##### Important notes about models
Both `python-rules` and `fab-quickstart` depend on
relationships.  Ideally, they exist in your database,
in which as `sqlcodegen` will find them.  If that's
not practical, SQLAlchemy also lets to define them in your models:
  * declare the **foreign keys**, eg, Orders has a foreign key to customers
    * `CustomerId = Column(ForeignKey('Customer.Id'))`
  * declare the **references** in the parent (not child), eg, declare orders
  for customer like this
    * `OrderDetailList = relationship("OrderDetail", backref="OrderHeader", cascade_backrefs=True)`



## Declaring Logic as Spreadsheet-like Rules
To illustrate, let's use an adaption
of the Northwind database,
with a few rollup columns added.
For those not familiar, this is basically
Customers, Orders, OrderDetails and Products,
as shown in the diagrams below.

##### Declare rules using Python
Logic is declared as spreadsheet-like rules as shown below
from  [`nw/nw_logic/nw_rules_bank.py`](nw/nw_logic/nw_rules_bank.py),
which implements the *check credit* requirement:
```python
def activate_basic_check_credit_rules():
    """ Check Credit Requirement:
        * the balance must not exceed the credit limit,
        * where the balance is the sum of the unshipped order totals
        * which is the rollup of OrderDetail Price * Quantities:
    """

    Rule.constraint(validate=Customer, as_condition=lambda row: row.Balance <= row.CreditLimit,
                    error_msg="balance ({row.Balance}) exceeds credit ({row.CreditLimit})")
    Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal,
             where=lambda row: row.ShippedDate is None)  # *not* a sql select sum
    
    Rule.sum(derive=Order.AmountTotal, as_sum_of=OrderDetail.Amount)
   
    Rule.formula(derive=OrderDetail.Amount, as_expression=lambda row: row.UnitPrice * row.Quantity)
    Rule.copy(derive=OrderDetail.UnitPrice, from_parent=Product.UnitPrice)
```


##### Activate Rules
To test our rules, we use
[`nw/trans_tests/add_order.py`](nw/trans_tests/add_order.py).
It activates the rules using this import:
```python
from nw.nw_logic import session  # opens db, activates logic listener <--
```
 
This executes [`nw/nw_logic/__init__.py`](nw/nw_logic/__init__.py),
which sets up the rule engine:
```python
by_rules = True  # True => use rules, False => use hand code (for comparison)
if by_rules:
    rule_bank_setup.setup(session, engine)     # setup rules engine
    activate_basic_check_credit_rules()        # loads rules above
    rule_bank_setup.validate(session, engine)  # checks for cycles, etc
else:
    # ... conventional after_flush listeners (to see rules/code contrast)
```



## FAB Quick Start
[Python Flask Application Builder (fab)](https://flask-appbuilder.readthedocs.io/en/latest/) creates "basic" applications for database crud operations quickly, with minimal coding.  Typical fab pages can look like this:

1. __Multi-page:__ apps include 1 page per table
1. __Multi-table:__ pages include `related_views` for each related child table, and join in parent data
1. __Favorite field first:__ first-displayed field is "name", or _contains_ "name" (configurable)
1. __Predictive joins:__ favorite field of each parent is shown (product _name_ - not the foreign key `product_id_`)
1. __Ids last:__ such boring fields are not shown on lists, and at the end on other pages

![generated page](https://drive.google.com/uc?export=view&id=1Q3cG-4rQ6Q6RdZppvkrQzCDhDYHnk-F6)

This is the __FAB Quick Start Guide__.  In about 10 minutes, we'll
1. __Install__ Python and FAB, and
1. __Create the application__ above using an existing database called `Northwind` (customers, orders, items, etc).  The app is 52 pages, for 13 underlying tables.



***

### Install Python Pre-reqs
To get started, you will need:
Python3
* __Python__
   * On Windows: just run the [installer](https://www.python.org/downloads/windows/)
   * On Mac / Unix: install with [brew](https://brew.sh) as described [here](https://opensource.com/article/19/5/python-3-default-mac#what-to-do).
      * You may encounter some adventures - 
[try these tips](https://github.com/valhuber/fab-quick-start/wiki/Mac-Python-Install-Issues)
* __virtualenv__ - a best practice for keeping Python / libraries separate for each project.  Install as described [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) (basically,  `pip install virtualenv`)
* __IDE:__ Python works with various debuggers; [here](https://github.com/valhuber/fab-quick-start/wiki/IDE-Setup) are setup instructions for two popular ones.  The screen shot below is VSCode (recommended but not required for this Quick Start).


### Create Sample `nw` project
Follow the procedure below to create a new FAB project.

#### 1 - Create Empty Project Folder and env
First, we create an empty project folder, with a `venv` for dependencies.  
We'll use `nw` for our project directory name.
For more information, see the [FAB docs](https://www.google.com/url?q=https%3A%2F%2Fflask-appbuilder.readthedocs.io%2Fen%2Flatest%2Finstallation.html&sa=D&sntz=1&usg=AFQjCNEUW0UMxjnGD_lI2k5E1QNTHZA8bQ).
```
mkdir nw
cd nw
virtualenv venv
# windows .env\Scripts\activate
source venv/bin/activate
```
Note: You can `deactivate` this `venv`, but you must reactivate using the last command above whenever you wish to work on the project again.

#### 2 - Create Empty fab Project
Install FAB (and dependencies), and create a default empty FAB app:
```
pip install flask-appbuilder
flask fab create-app
```
You will then be prompted for the project name and your db engine type.  When prompted:
* Use the default engine
* Name the project `nw-app`

You should see a structure as shown in the screen shot in the next section.

We now have a well-formed empty project.  We now need to acquire and __configure a database__, set up SQLAlchemy ORM __`models.py`__, and define our pages with __`views.py`__.

#### 3 - Configure Database
To get the database:
1. <a id="raw-url" target="_blank" href="https://github.com/valhuber/fab-quick-start/blob/master/nw-app/Northwind_small.sqlite">Download this file</a>, a sqlite version of Northwind.
1. Copy it to your `nw-app` folder
1. Update your `nw-app/config.py` file to denote this database name (illustrated below): `Northwind_small.sqlite`

Your project will look something like this:

![fab_quick-start project](https://drive.google.com/uc?export=view&id=1f_GutzKmhrZ_oFxiTiZ9x-lzwkdJD3cS)

##### Key FAB inputs can become tedious: `models.py` and `views.py`
FAB requires that we edit __2 key files__ to make our "empty" project interact with the database.  These can get __tedious,__ due to per-page code required for _each_ table / page.  For more information, [see here](https://github.com/valhuber/fab-quick-start/wiki/Tedious-per-page-code).

The following sections show how to __use generators to avoid the tedious hand creation__ of the `views.py` and the `models.py` files.

#### 4 - Create `models.py`
You must provide model classes for SQLAlchemy.  That's a bit of work (13 classes in this small example), but we can automate this with __sqlacodegen__, like this:
```
cd nw-app
pip install sqlacodegen
sqlacodegen sqlite:///Northwind_small.sqlite --noviews > app/models.py
```
This overwrites your `nw/nw-app/app/models.py` module.
For more information, see the [sqlacodegen docs](https://www.google.com/url?q=https%3A%2F%2Fpypi.org%2Fproject%2Fsqlacodegen%2F&sa=D&sntz=1&usg=AFQjCNHZ3ERjfnSO8MA8V20gzLjfeBaIxw).

#### 5 - Define `views.py`
Finally, we need to define some pages.  That's also a bit of work to do that by hand, so let's use __fab-quick-start__
to create the `views.py` file from the `app/models.py` file (__hit enter__ to accept defaults when prompted):

```
pip install fab-quick-start
fab-quick-start run --favorites="name description" --non_favorites="id" > app/views.py
```
This overwrites your `nw/nw-app/app/views.py` file.  For more information, see the [FAB Quick Start Utility docs](https://github.com/valhuber/fab-quick-start#readme).

#### 6 - Create Admin
The FAB system can create tables in your database for authenticating and authorizing users (tables such as `ab_user`, `ab_user_role`, etc).  You create these as follows (Username: `admin`, Password: `p`):
```
(venv)$ export FLASK_APP=app
(venv)$ flask fab create-admin
Username [admin]:
User first name [admin]:
User last name [user]:
Email [admin@fab.org]:
Password:
Repeat for confirmation:
```
Ignore the error "user already exists", since the admin data was pre-loaded.

You can verify your data and admin data like this (mac/unix only):
```
sqlite3 Northwind_small.sqlite  # mac only
> .tables
> .schema Order
> select * from ab_user;
> select * from Territory;
> .quit
```

#### 7 - Run `nw' App
You've now created a app with a dozen pages or so; run it like this:
```
(venv)$ # still cd'd to nw-app
(venv)$ export FLASK_APP=app
(venv)$ flask run
```
Start your browser [here](http://127.0.0.1:5000/).

***



